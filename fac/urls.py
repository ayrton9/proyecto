from django.urls import path,include

from .views import ClienteView , ClienteNew,ClienteEdit , cliente_inactivar, FacturaView, facturas , \
                   ProductoView , borrar_detalle_factura

from .reportes import imprimir_factura_recibo

urlpatterns = [
   
    path('clientes/',ClienteView.as_view(), name= 'cliente_list'),
    path('clientes/new',ClienteNew.as_view(), name= 'cliente_new'),
    path('clientes/edit/<int:pk>',ClienteEdit.as_view(), name= 'cliente_edit'),
    path('clientes/inactivar/<int:id>',cliente_inactivar, name= 'cliente_inactivar'),

    path('facturas/',FacturaView.as_view(), name= 'factura_list'),
    path('facturas/new',facturas, name= 'factura_new'),
    path('facturas/buscar-producto',ProductoView.as_view(), name= 'factura_producto'),
    path('facturas/edit/<int:id>',facturas, name= 'factura_edit'),

    path('facturas/borrar-detalle/<int:id>',borrar_detalle_factura, name= 'factura_borrar_detalle'),

     path('facturas/imprimir/<int:id>',imprimir_factura_recibo, name= 'factura_imprimir_one'),



]