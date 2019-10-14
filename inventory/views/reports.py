import datetime
import os

from django.views.generic import TemplateView, FormView
from common_data.forms import PeriodReportForm
from . import models
from common_data.utilities import (ConfigMixin, 
                                   MultiPageDocument,
                                   ContextMixin,
                                   encode_period,
                                   extract_encoded_period,
                                   extract_period)
                                
from inventory.views.common import CREATE_TEMPLATE
from wkhtmltopdf.views import PDFTemplateView
from django.db.models import Q

class InventoryReport( ConfigMixin, MultiPageDocument,TemplateView):
    template_name = os.path.join('inventory', 'reports', 'inventory',
        'report.html')
    page_length = 20

    def get_multipage_queryset(self):
        return models.InventoryItem.objects.filter(type=0, active=True)

    def get_context_data(self, *args, **kwargs):
        context = super(InventoryReport, self).get_context_data(*args, **kwargs)
        context['items'] = models.WareHouseItem.objects.filter(item__type=0)
        context['date'] = datetime.date.today()
        context['pdf_link'] = True


        #insert config
        return context


class OutstandingOrderReport( ConfigMixin, MultiPageDocument, TemplateView):
    template_name = os.path.join('inventory', 'reports', 'outstanding_orders','report.html')
    page_length = 20

    def get_multipage_queryset(self):
        return models.Order.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(OutstandingOrderReport, self).get_context_data(*args, **kwargs)
        context['orders'] = models.Order.objects.all()
        context['date'] = datetime.date.today()
        context['pdf_link'] = True
        #insert config
        return context



class InventoryReportPDFView( ConfigMixin, MultiPageDocument,  PDFTemplateView):
    template_name = InventoryReport.template_name
    page_length = 20

    def get_multipage_queryset(self):
        return models.WareHouseItem.objects.filter(item__type=0)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['items'] = models.WareHouseItem.objects.all()
        context['date'] = datetime.date.today()
        #insert config
        return context


class OutstandingOrderReportPDFView( ConfigMixin, PDFTemplateView):
    template_name = OutstandingOrderReport.template_name

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #TODO limit to orders that are not yet fully received
        context['orders'] = models.Order.objects.all()
        context['date'] = datetime.date.today()
        #insert config
        return context


class PaymentsDueReportView(ContextMixin,
                            ConfigMixin, 
                            MultiPageDocument, 
                            TemplateView):
    template_name = os.path.join('inventory', 'reports', 'payments_due',
        'report.html')
    page_length = 20
    extra_context ={
        'date': datetime.date.today(),
        'pdf_link': True
    }
    

    def get_multipage_queryset(self):
        return models.Order.objects.filter(
                due__lte=datetime.date.today(),
                status__in=['order', 'received', 'received_partially']) 

class PaymentsDuePDFView(ContextMixin, 
                         ConfigMixin, 
                         MultiPageDocument, 
                         PDFTemplateView):
    template_name = PaymentsDueReportView.template_name
    page_length = PaymentsDueReportView.page_length
    extra_context = {
        'date': datetime.date.today()
    }

    def get_multipage_queryset(self):
        return PaymentsDueReportView.get_multipage_queryset(self)

class VendorAverageDaysToDeliverReportView(ConfigMixin,
                                         ContextMixin,
                                         MultiPageDocument,
                                         TemplateView):

    template_name = os.path.join('inventory', 'reports', 'days_to_deliver', 
        'report.html')
    page_length = 20
    extra_context = {
        'date': datetime.date.today(),
        'pdf_link': True
    } 

    def get_multipage_queryset(self):
        return models.Supplier.objects.all()

class VendorAverageDaysToDeliverPDFView(ContextMixin, 
                                        ConfigMixin, 
                                        MultiPageDocument, 
                                        PDFTemplateView):
    template_name = VendorAverageDaysToDeliverReportView.template_name
    page_length = VendorAverageDaysToDeliverReportView.page_length
    extra_context = {
        'date': datetime.date.today()
    }

    def get_multipage_queryset(self):
        return VendorAverageDaysToDeliverReportView.get_multipage_queryset(self)


#DO NOT PAGINATE, table will handle it