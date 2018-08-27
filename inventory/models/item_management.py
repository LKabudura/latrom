# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from decimal import Decimal as D
import rest_framework
from functools import reduce

from django.db import models
from django.db.models import Q
from django.conf import settings
from accounting.models import JournalEntry, Journal, Account
from common_data.models import SingletonModel
from .warehouse_models import WareHouseItem, StorageMedia
import inventory
class Order(models.Model):
    '''The record of all purchase orders for inventory of items that 
    will eventually be sold. Contains the necessary data to update 
    inventory and update the Purchases Journal.
    An aggregate with the OrderItem class.
    A cash order creates a transaction creation.
    A deferred payment pays on the deferred date.(Not yet implemented)
    A pay on receipt order creates the transaction when receiving a 
    goods received voucher.

    properties
    ------------
    total - returns the total value of the items ordered.
    received_total - returns the numerical value of items received
    fully_received - returns a boolean if all the ordered items have 
        been received.
    percent_received - is the percentage of the order that has been
        fulfilled by the supplier.
    
    methods
    -------------
    receive - quickly generates a stock receipt where all items are 
        marked fully received 
    '''
    ORDER_TYPE_CHOICES = [
        (0, 'Cash Order'),
        (1, 'Deffered Payment Order'),
        (2, 'Pay on Receipt') ]
    ORDER_STATUS_CHOICES = [
        ('received-partially', 'Partially Received'),
        ('received', 'Received in Total'),
        ('draft', 'Internal Draft'),
        ('submitted', 'Submitted to Supplier')
    ]
    
    expected_receipt_date = models.DateField()
    issue_date = models.DateField()
    type_of_order = models.IntegerField(choices=ORDER_TYPE_CHOICES, default=0)
    deferred_date = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey('inventory.supplier', on_delete=None,blank=True, null=True)
    supplier_invoice_number = models.CharField(max_length=32, blank=True, default="")
    bill_to = models.CharField(max_length=128, blank=True, default="")
    ship_to = models.ForeignKey('inventory.WareHouse', on_delete=None)
    tax = models.ForeignKey('accounting.Tax',on_delete=None, default=1)
    tracking_number = models.CharField(max_length=64, blank=True, default="")
    notes = models.TextField()
    status = models.CharField(max_length=24, choices=ORDER_STATUS_CHOICES)
    active = models.BooleanField(default=True)
    received_to_date = models.FloatField(default=0.0)
    
    def __str__(self):
        return 'ORD' + str(self.pk)

    @property
    def items(self):
        return self.orderitem_set.all()

    @property
    def total(self):
        return reduce(lambda x, y: x + y , [item.subtotal for item in self.items], 0)

    @property
    def subtotal(self):
        return self.total - self.tax_amount

    @property
    def tax_amount(self):
        if self.tax:
            return self.total * (D(self.tax.rate) / D(100))
        return D(0.0)
    
    @property
    def received_total(self):
        return reduce(lambda x, y: x + y , [item.received_total for item in self.items], 0)
    
    @property
    def fully_received(self):
        for item in self.items:
            if item.fully_received == False : return False
        return True

    @property
    def percent_received(self):
        items = self.orderitem_set.all()
        n_items = items.count()
        received = 0
        for item in items:
            if item.fully_received == True : 
                received += 1
        return (float(received) / float(n_items)) * 100.0

    def create_deffered_entry(self):
        j = JournalEntry.objects.create(
                    reference = "Auto generated entry created by order " + str(self),
                    date=self.deferred_date,
                    memo = self.notes,
                    journal = Journal.objects.get(pk=4)
                )
        j.credit(self.subtotal, Account.objects.get(pk=2000))#accounts payable
        j.debit(self.total, self.supplier.account) # since we owe the supplier
        j.credit(self.tax_amount, Account.objects.get(pk=2001))#sales tax

    def create_immediate_entry(self):
        j = JournalEntry.objects.create(
                date = self.issue_date,
                reference = "Auto generated entry from order" + str(self),
                memo=self.notes,
                journal = Journal.objects.get(pk=4)
            )
        j.credit(self.subtotal, Account.objects.get(pk=1004))#inventory
        j.debit(self.total, Account.objects.get(pk=4006))#purchases account
        j.credit(self.tax_amount, Account.objects.get(pk=2001))#sales tax

    def receive(self):
        if self.status != 'received':
            sr = StockReceipt.objects.create(
                    order=self,
                    receive_date= datetime.date.today(),
                    note = 'Autogenerated receipt from order number' + \
                        str(self.pk),
                    fully_received=True
                )
            for item in self.orderitem_set.all():
                item.receive(item.quantity)
            sr.create_entry()
    #check for deffered date with deferred type of invoice
    


class OrderItem(models.Model):
    '''A component of an order this tracks the order price 
    of an item its quantity and how much has been received.
    
    methods
    -----------
    receive - takes a number and adds its value to the item inventory
        and the orderitem's received quantity field.
    
    properties
    -----------
    received_total - returns the cash value of the items received
    subtotal - returns the cash value of the items ordered
    '''
    ITEM_TYPE_CHOICES =[
        (1, 'Product'),
        (2, 'Consumable'),
        (3, 'Equipment')
        ]
    order = models.ForeignKey('inventory.Order', on_delete=None, )
    item_type = models.PositiveSmallIntegerField(default=1, 
        choices=ITEM_TYPE_CHOICES)
    product = models.ForeignKey('inventory.product', on_delete=None,null=True)
    consumable = models.ForeignKey('inventory.consumable', on_delete=None,null=True)
    equipment = models.ForeignKey('inventory.equipment', on_delete=None,null=True)
    quantity = models.FloatField()
    order_price = models.DecimalField(max_digits=6, decimal_places=2)
    received = models.FloatField(default=0.0)

    def __init__(self, *args,**kwargs):
        super(OrderItem, self).__init__(*args, **kwargs)
        self.mapping = {
            1: self.product,
            2: self.consumable,
            3: self.equipment
        }

    @property
    def item(self):
        return self.mapping[self.item_type]

    @property
    def fully_received(self):
        if self.received < self.quantity:
            return False
        return True

    def receive(self, n, medium=None):
        n= float(n)
        self.received += n
        
        wh_item = self.order.ship_to.add_item(self.item, n)
        if medium:
            medium = StorageMedia.objects.get(pk=medium)
            wh_item.location=medium
            wh_item.save()
        
        self.item.set_purchase_price(self.order_price)
            
        self.save()
        
    def __str__(self):
        return str(self.item) + ' -' + str(self.order_price)

        
    @property
    def received_total(self):
        return D(self.received)  * self.order_price

    @property
    def subtotal(self):
        return D(self.quantity) * self.order_price

class StockReceipt(models.Model):
    '''
    Part of the inventory ordering workflow.
    When an order is generated this object is created to verify 
    the receipt of items and comment on the condition of the 
    products.

    methods
    ---------
    create_entry - method only called for instances where inventory 
    is paid for on receipt as per order terms.
    '''
    order = models.ForeignKey('inventory.Order', on_delete=None)
    received_by = models.ForeignKey('employees.Employee', on_delete=None,
        default=1)
    receive_date = models.DateField()
    note =models.TextField(blank=True, default="")
    fully_received = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + ' - ' + str(self.receive_date)

    def save(self, *args, **kwargs):
        super(StockReceipt, self).save(*args, **kwargs)
        self.order.received_to_date = self.order.received_total
        self.order.save()
        

    def create_entry(self):
        j = JournalEntry.objects.create(
            reference = "ORD" + str(self.order.pk),
            memo = "Auto generated Entry from Purchase Order",
            date =self.receive_date,
            journal = Journal.objects.get(pk=2)
        )
        new_total = self.order.received_total - D(self.order.received_to_date)
        j.simple_entry(
            new_total,
            Account.objects.get(pk=1004),#inventory
            Account.objects.get(pk=1000)#checking account
        )

#might need to rename
class InventoryCheck(models.Model):
    date = models.DateField()
    next_adjustment_date = models.DateField(null=True)#not required
    adjusted_by = models.ForeignKey('employees.Employee', on_delete=None )
    warehouse = models.ForeignKey('inventory.WareHouse', on_delete=None )
    comments = models.TextField()
    
    @property 
    def adjustments(self):
        return self.stockadjustment_set.all()

    @property
    def value_of_all_adjustments(self):
        return reduce(lambda x, y: x + y, 
            [i.adjustment_value for i in self.adjustments], 0)

class StockAdjustment(models.Model):
    warehouse_item = models.ForeignKey('inventory.WareHouseItem', on_delete=None)
    adjustment = models.FloatField()
    note = models.TextField()
    inventory_check = models.ForeignKey('inventory.InventoryCheck', on_delete=None)

    @property
    def adjustment_value(self):
        return D(self.adjustment) * self.warehouse_item.item.unit_purchase_price

    @property
    def prev_quantity(self):
        return self.warehouse_item.quantity + self.adjustment

    def adjust_inventory(self):
        self.warehouse_item.decrement(self.adjustment)

    def save(self, *args, **kwargs):
        super(StockAdjustment, self).save(*args, **kwargs)
        self.adjust_inventory()

class TransferOrder(models.Model):
    issue_date = models.DateField()
    expected_completion_date = models.DateField()
    issuing_inventory_controller = models.ForeignKey('employees.Employee',
        related_name='issuing_inventory_controller', on_delete=None,null=True)
    receiving_inventory_controller = models.ForeignKey('employees.Employee', on_delete=None, null=True)
    actual_completion_date =models.DateField(null=True)#provided later
    source_warehouse = models.ForeignKey('inventory.WareHouse',
        related_name='source_warehouse', on_delete=None,)
    receiving_warehouse = models.ForeignKey('inventory.WareHouse', on_delete=None,)
    order_issuing_notes = models.TextField(blank=True)
    receive_notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    
    #link expenses 
    def complete(self):
        for line in self.transferorderline_set.all():
            self.source_warehouse.decrement_item(line.product, line.quantity)
            self.receiving_warehouse.add_item(line.product, line.quantity)
        self.completed = True
        self.save()

class TransferOrderLine(models.Model):
    product = models.ForeignKey('inventory.Product', on_delete=None)
    quantity = models.FloatField()
    transfer_order = models.ForeignKey('inventory.TransferOrder', on_delete=None)


class InventoryScrappingRecord(models.Model):
    date = models.DateField()
    controller = models.ForeignKey('employees.Employee', on_delete=None)
    warehouse = models.ForeignKey('inventory.WareHouse', on_delete=None)
    comments = models.TextField(blank=True)

    @property
    def scrapping_value(self):
        return reduce(lambda x, y: x + y, 
            [i.scrapped_value \
                for i in self.inventoryscrappingrecordline_set.all()], 
                0)

class InventoryScrappingRecordLine(models.Model):
    product = models.ForeignKey('inventory.Product', on_delete=None)
    quantity = models.FloatField()
    note = models.TextField(blank=True)
    scrapping_record = models.ForeignKey('inventory.InventoryScrappingRecord', on_delete=None)

    @property
    def scrapped_value(self):
        return self.product.unit_sales_price * D(self.quantity)