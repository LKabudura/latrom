

import django_filters

from . import models


class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = models.Customer
        fields = {
            'organization__legal_name': ['icontains'],
            'individual__last_name': ['icontains'],
            
        }


class CreditNoteFilter(django_filters.FilterSet):
    class Meta:
        model = models.CreditNote
        fields = {
            'date': ['exact'],
        }


class InvoiceFilter(django_filters.FilterSet):
    class Meta:
        model = models.Invoice
        fields = {
            'date': ['exact'],
            'customer': ['exact'],
            'status': ['exact']
        }
