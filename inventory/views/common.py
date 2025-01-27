# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from inventory.views.util import InventoryConfigMixin 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from common_data.models import GlobalConfig
from common_data.utilities import *
from common_data.views import PaginationMixin
from inventory import filters, forms, models, serializers
from invoicing.models import SalesConfig
from inventory.views.dash_plotters import composition_plot
from formtools.wizard.views import SessionWizardView
from django.conf import settings
from django.core.files.storage import FileSystemStorage

CREATE_TEMPLATE =os.path.join("common_data", "create_template.html")


class InventoryDashboard(InventoryConfigMixin, TemplateView):
    template_name = os.path.join("inventory", "dashboard.html")

    def get(self, *args, **kwargs):
        if models.InventorySettings.objects.first().is_configured:
            resp = super().get(*args, **kwargs)
            return resp 

        else:
            return HttpResponseRedirect(reverse_lazy('inventory:config-wizard'))

            
class AsyncDashboard(ContextMixin, TemplateView):
    template_name = os.path.join('inventory', 'async_dashboard.html')

    def get_context_data(self, *args, **kwargs):
        context =  super().get_context_data(*args, **kwargs)

        context['undelivered_orders'] = models.Order.objects.filter(stockreceipt__isnull=True).count()

        context['outstanding_orders'] = len([ i for i in models.Order.objects.filter(status="order") if i.payment_status != "paid"])

        context['money_owed'] = sum([i.total_due for i in models.Order.objects.filter(status="order")])

        context['vendors'] = models.Supplier.objects.filter(active=True).count()
        context['warehouses'] = models.WareHouse.objects.all().count()
        context['pending_transfers'] = models.TransferOrder.objects.filter(
            completed=False).count()

        context['products'] = models.InventoryItem.objects.filter(
            type=0).count()
        context['equipment'] = models.InventoryItem.objects.filter(
            type=1).count()
        context['consumables'] = models.InventoryItem.objects.filter(
            type=2).count()
        context['graph'] = composition_plot().render(is_unicode=True)

        return context

#######################################################
#                       Units                         #
#######################################################


class UnitCreateView(ContextMixin,  CreateView):
    form_class = forms.UnitForm
    model = models.UnitOfMeasure
    template_name = CREATE_TEMPLATE
    extra_context = {
        'title':'Create New Unit of measure'
    }

class UnitUpdateView(ContextMixin,  UpdateView):
    form_class = forms.UnitForm
    model = models.UnitOfMeasure
    template_name = CREATE_TEMPLATE
    extra_context = {
        'title':'Update Unit of measure'
    }

class UnitDetailView( DetailView):
    model = models.UnitOfMeasure
    template_name = os.path.join('inventory', 'unit', 'detail.html')


class UnitListView(ContextMixin,  PaginationMixin, FilterView):
    filterset_class = filters.UnitFilter
    model = models.UnitOfMeasure
    paginate_by = 20
    template_name = os.path.join('inventory', 'unit', 'list.html')
    extra_context = {
        'title': 'List of Units',
        'new_link': reverse_lazy('inventory:unit-create')
    }


class UnitDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.UnitOfMeasure
    success_url = reverse_lazy('invoicing.product-list')

class UnitAPIView(ModelViewSet):
    serializer_class = serializers.UnitSerializer
    queryset = models.UnitOfMeasure.objects.all()

class ConfigView( UpdateView):
    template_name = os.path.join('inventory', 'config.html')
    form_class = forms.ConfigForm
    model = models.InventorySettings
    success_url = reverse_lazy('inventory:home')
    #change this page

class CategoryCreateView( CreateView):
    form_class = forms.CategoryForm
    model = models.Category
    template_name = os.path.join('inventory', 'category', 'create.html')

class CategoryUpdateView( UpdateView):
    form_class = forms.CategoryForm
    model = models.Category
    template_name = os.path.join('inventory', 'category','update.html')

class CategoryListView( TemplateView):
    template_name = os.path.join('inventory', 'category', 'list.html')

class CategoryDetailView( DetailView):
    template_name = os.path.join('inventory', 'category', 'detail.html')
    model = models.Category

class CategoryListAPIView(ListAPIView):
    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        return models.Category.objects.filter(parent=None)



class ConfigWizard(ConfigWizardBase):
    template_name = os.path.join('inventory', 'wizard.html')
    form_list = [
        forms.ConfigForm, 
        forms.WareHouseForm, 
        forms.SupplierForm, 
        ]

    config_class = models.InventorySettings
    success_url = reverse_lazy('inventory:home')
    file_storage = FileSystemStorage(location=settings.MEDIA_ROOT)

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if step == '2':
            initial.update({'vendor_type': 'organization'})

        return initial