from rest_framework import serializers

from inventory.serializers import InventoryItemSerializer

from .models import *


    
class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['name', 'id',  'organization', 'individual', 'billing_address', 'banking_details']
    


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesConfig
        fields = "__all__"



class ProductLineComponentSerializer(serializers.ModelSerializer):
    product = InventoryItemSerializer(many=False)
    returned_quantity = serializers.ReadOnlyField()
    class Meta:
        model = ProductLineComponent
        fields = "__all__"


class ServiceLineComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLineComponent
        fields = "__all__"

class InvoiceLineSerializer(serializers.ModelSerializer):
    product = ProductLineComponentSerializer(many=False)
    service = ServiceLineComponentSerializer(many=False)
    
    class Meta:
        model = InvoiceLine
        fields = "__all__"

class InvoiceSerializer(serializers.ModelSerializer):
    invoiceline_set = InvoiceLineSerializer(many=True)
    class Meta:
        model = Invoice
        fields = ['invoiceline_set', 'customer', 'id']

