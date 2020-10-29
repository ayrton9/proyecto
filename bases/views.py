from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.views import generic



class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'bases/home.html'
    login_url = 'bases:login'

