import os
import json
import urllib

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView, ListView
from django_filters.views import FilterView
from common_data.views import PaginationMixin

from rest_framework.viewsets import ModelViewSet
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate

from services import models
from inventory.models import Equipment, Consumable, UnitOfMeasure
from services import filters
from services import forms 
from services import serializers
from common_data.utilities import ExtraContext
from common_data.forms import AuthenticateForm


class EquipmentRequisitionCreateView(CreateView):
    template_name = os.path.join('services', 'requisitions', 'equipment', 
        'create.html')
    form_class = forms.EquipmentRequisitionForm
    success_url = reverse_lazy('services:equipment-requisition-list')

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        equipment = json.loads(urllib.parse.unquote(request.POST['equipment']))
        
        for equ in equipment:
            equ_pk = equ['item'].split('-')[0]
            equ_item = Equipment.objects.get(pk=equ_pk)
            line = models.EquipmentRequisitionLine.objects.create(
                requisition=self.object,
                equipment= equ_item,
                requesting_condition=equ['condition'],
                quantity=equ['quantity']
            )
        return resp


class EquipmentRequisitionDetailView(DetailView):
    template_name = os.path.join('services', 'requisitions', 'equipment',
        'authorize_release.html')
    model = models.EquipmentRequisition

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['authorize_form'] = AuthenticateForm()
        return context

class EquipmentRequisitionListView(ExtraContext, PaginationMixin, FilterView):
    filterset_class = filters.EquipmentRequisitionFilter
    queryset = models.EquipmentRequisition.objects.all()
    template_name = os.path.join('services', 'requisitions', 'equipment', 'list.html')

    extra_context = {
        'title': 'List of Equipment Requisitions'
    }

class EquipmentRequisitionAPIView(ModelViewSet):
    pass

def equipment_requisition_authorize(request, pk=None):
    req = get_object_or_404(models.EquipmentRequisition, pk=pk)
    redirect_path = reverse_lazy('services:equipment-requisition-detail', 
        kwargs={
            'pk': pk
            })
    form = AuthenticateForm(request.POST)
    if form.is_valid():
        usr = form.cleaned_data['user']
        authenticated = authenticate(
            username=usr.username, 
            password=form.cleaned_data['password']
            )
        if authenticated:
            if not hasattr(usr, 'employee'):
                return HttpResponseRedirect(redirect_path)
            req.authorized_by = usr.employee
            req.save()
            return HttpResponseRedirect(reverse_lazy('services:equipment-requisition-list'))

    return HttpResponse(request.path)


def equipment_requisition_release(request, pk=None):
    req = get_object_or_404(models.EquipmentRequisition, pk=pk)
    redirect_path = reverse_lazy('services:equipment-requisition-detail', 
        kwargs={
            'pk': pk
            })
    form = AuthenticateForm(request.POST)
    if form.is_valid():
        usr = form.cleaned_data['user']
        authenticated = authenticate(
            username=usr.username, 
            password=form.cleaned_data['password']
            )
        if authenticated:
            if not hasattr(usr, 'employee'):
                return HttpResponseRedirect(redirect_path)            
            req.released_by = usr.employee
            req.save()
            return HttpResponseRedirect(reverse_lazy(
                    'services:equipment-requisition-list'))

    return HttpResponseRedirect(redirect_path)


#################################################
#            Consumable Requisitions            #
#################################################

class ConsumableRequisitionCreateView(CreateView):
    template_name = os.path.join('services', 'requisitions', 'consumables', 
        'create.html')
    form_class = forms.ConsumablesRequisitionForm
    success_url = reverse_lazy('services:consumable-requisition-list')

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        consumables = json.loads(urllib.parse.unquote(request.POST['consumables']))
        
        for con in consumables:
            con_pk = con['item'].split('-')[0]
            con_item = Consumable.objects.get(pk=con_pk)
            unit = UnitOfMeasure.objects.get(pk=con['unit'])
            line = models.ConsumablesRequisitionLine.objects.create(
                requisition=self.object,
                consumable= con_item,
                quantity=con['quantity'],
                unit=unit
            )
        return resp


class ConsumableRequisitionDetailView(DetailView):
    template_name = os.path.join('services', 'requisitions', 'consumables',
        'authorize_release.html')
    model = models.ConsumablesRequisition

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['authorize_form'] = AuthenticateForm()
        return context

class ConsumableRequisitionListView(ExtraContext, PaginationMixin, FilterView):
    filterset_class = filters.ConsumableRequisitionFilter
    queryset = models.ConsumablesRequisition.objects.all()
    template_name = os.path.join('services', 'requisitions', 'consumables', 'list.html')

    extra_context = {
        'title': 'List of Consumables Requisitions'
    }

class ConsumableRequisitionAPIView(ModelViewSet):
    pass

def authenticator(request):
    pass

def consumable_requisition_authorize(request, pk=None):
    req = get_object_or_404(models.ConsumablesRequisition, pk=pk)
    redirect_path = reverse_lazy('services:consumable-requisition-detail', 
        kwargs={
            'pk': pk
            })
    form = AuthenticateForm(request.POST)
    if form.is_valid():
        usr = form.cleaned_data['user']
        authenticated = authenticate(
            username=usr.username, 
            password=form.cleaned_data['password']
            )
        if authenticated:
            if not hasattr(usr, 'employee'):
                return HttpResponseRedirect(redirect_path)
            req.authorized_by = usr.employee
            req.save()
            return HttpResponseRedirect(reverse_lazy('services:consumable-requisition-list'))

    return HttpResponse(request.path)


def consumable_requisition_release(request, pk=None):
    req = get_object_or_404(models.ConsumablesRequisition, pk=pk)
    redirect_path = reverse_lazy('services:consumable-requisition-detail', 
        kwargs={
            'pk': pk
            })
    form = AuthenticateForm(request.POST)
    if form.is_valid():
        usr = form.cleaned_data['user']
        authenticated = authenticate(
            username=usr.username, 
            password=form.cleaned_data['password']
            )
        if authenticated:
            if not hasattr(usr, 'employee'):
                return HttpResponseRedirect(redirect_path)            
            req.released_by = usr.employee
            req.save()
            return HttpResponseRedirect(reverse_lazy(
                    'services:consumable-requisition-list'))

    return HttpResponseRedirect(redirect_path)