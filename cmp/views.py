from django.shortcuts import render, redirect

import datetime
from django.http import HttpResponse

from django.contrib import messages

# Create your views here.
from django.views import generic
from django.urls import reverse_lazy

import json

from django.db.models import Sum

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.messages.views import  SuccessMessageMixin

from .models import Proveedor, ComprasEnc, ComprasDet

from inv.models import Producto

from cmp.forms import ProveedorForm, ComprasEncForm

from bases.views import SinPrivilegios

from django.contrib.auth.decorators import login_required, permission_required


class ProveedorView(LoginRequiredMixin, SinPrivilegios, generic.ListView):
    permission_required = "cmp.view_proveedor"
    model =  Proveedor
    template_name = "cmp/proveedor_list.html"
    context_object_name = "obj"
    login_url = 'bases:login'


class ProveedorNew(SuccessMessageMixin, LoginRequiredMixin, SinPrivilegios, generic.CreateView):
    permission_required = "cmp.add_proveedor"
    model = Proveedor
    template_name= "cmp/proveedor_form.html"
    context_object_name = "obj"
    form_class = ProveedorForm
    success_url = reverse_lazy("cmp:proveedor_list")
    login_url = 'bases:login'
    success_message= "Proveedor Creado Satisfactoriamente"

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)


class ProveedorEdit(SuccessMessageMixin, LoginRequiredMixin, SinPrivilegios, generic.UpdateView):
    permission_required = "cmp.change_proveedor"
    model = Proveedor
    template_name= "cmp/proveedor_form.html"
    context_object_name = "obj"
    form_class = ProveedorForm
    success_url = reverse_lazy("cmp:proveedor_list")
    login_url = 'bases:login'
    success_message= "Proveedor Actualizado Satisfactoriamente"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)

@login_required(login_url='/login/')
@permission_required('cmp.change_proveedor', login_url='bases:sin_privilegios')
def proveedor_inactivar(request, id):
    pro = Proveedor.objects.filter(pk=id).first()

    contexto = {}
    template_name = "cmp/inactivar_prv.html"

    if not pro:
        return redirect("cmp:proveedor_list")

    if request.method=='GET':
        contexto={"obj":pro}

    if request.method=='POST':
        pro.estado=False
        pro.save()
        messages.success(request, 'Proveedor Inactivado')
        return redirect('cmp:proveedor_list')

    return render(request,template_name,contexto)


    
class ComprasView(LoginRequiredMixin, SinPrivilegios, generic.ListView):
    permission_required = "cmp.view_comprasenc"
    model =  ComprasEnc
    template_name = "cmp/compras_list.html"
    context_object_name = "obj"
    


@login_required(login_url='/login/')
@permission_required('cmp.view_comprasenc', login_url='bases:sin_privilegios')
def compras(request,compra_id=None):
    template_name="cmp/compras.html"
    prod=Producto.objects.filter(estado=True)
    form_compras={}
    contexto={}

    if request.method=='GET':
        form_compras=ComprasEncForm()
        enc = ComprasEnc.objects.filter(pk=compra_id).first()

        if enc:
            det = ComprasDet.objects.filter(compra=enc)
            fecha_compra = datetime.date.isoformat(enc.fecha_compra)
            fecha_factura = datetime.date.isoformat(enc.fecha_factura)
            e = {
                'fecha_compra':fecha_compra,
                'proveedor': enc.proveedor,
                'observacion': enc.observacion,
                'no_factura': enc.no_factura,
                'fecha_factura': fecha_factura,
                'sub_total': enc.sub_total,
                'descuento': enc.descuento,
                'total': enc.total
            }

            form_compras = ComprasEncForm(e)
        else:
            det=None
        
        contexto={'productos':prod, 'encabezado':enc, 'detalle':det, 'form_enc':form_compras}

    if  request.method=='POST':
        fecha_compra = request.POST.get("fecha_compra")
        observacion = request.POST.get("observacion")
        no_factura = request.POST.get("no_factura")
        fecha_factura = request.POST.get("fecha_factura")
        proveedor = request.POST.get("proveedor")
        sub_total = 0
        descuento = 0
        total = 0
            
        if not compra_id:
            prov = Proveedor.objects.get(pk=proveedor)

            enc = ComprasEnc(
                fecha_compra= fecha_compra,
                observacion= observacion,
                no_factura = no_factura,
                fecha_factura = fecha_factura,
                proveedor = prov,
                uc = request.user
            )

            if enc:
                enc.save()
                compra_id= enc.id
        else:
            enc= ComprasEnc.objects.filter(pk=compra_id).first()
            if enc:

                enc.fecha_compra= fecha_compra
                enc.observacion= observacion
                enc.no_factura = no_factura
                enc.fecha_factura = fecha_factura
                enc.um = request.user.id
                enc.save()

        if not compra_id:
            return redirect("cmp:compras_list")


        producto= request.POST.get("id_id_producto")
        cantidad = request.POST.get("id_cantidad_detalle")
        precio = request.POST.get("id_precio_detalle")
        sub_total_detalle = request.POST.get("id_sub_total_detalle")
        descuento_detalle = request.POST.get("id_descuento_detalle")
        total_detalle = request.POST.get("id_total_detalle")

        prod = Producto.objects.get(pk=producto)

        det = ComprasDet(
            compra = enc,
            producto = prod,
            cantidad = cantidad,
            precio_prv = precio,
            descuento = descuento_detalle,
            costo= 0,
            uc = request.user
        )

        if det:
            det.save()

            sub_total =  ComprasDet.objects.filter(compra=compra_id).aggregate(Sum('sub_total'))
            descuento =  ComprasDet.objects.filter(compra=compra_id).aggregate(Sum('descuento'))

            enc.sub_total = sub_total["sub_total__sum"]
            enc.descuento = descuento["descuento__sum"]
            enc.save()
            
        return redirect("cmp:compras_edit", compra_id = compra_id)

      

    return render(request,template_name,contexto)


class CompraDetDelete(SinPrivilegios, generic.DeleteView):
    permission_required = "cmp.delete_comprasdet"
    model = ComprasDet
    template_name = "cmp/compras_det_del.html"
    context_object_name = 'obj'

    def get_success_url(self):
        compra_id=self.kwargs['compra_id']
        return reverse_lazy('cmp:compras_edit', kwargs = {'compra_id': compra_id})