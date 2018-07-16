# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from decimal import Decimal as D
import rest_framework

from django.db import models
from django.db.models import Q
from django.conf import settings
from invoicing.models import Invoice, InvoiceItem
from accounting.models import JournalEntry, Journal, Account
from common_data.utilities import load_config

class Supplier(models.Model):
    '''The businesses and individuals that provide the organization with 
    products it will sell. Basic features include contact details address and 
    contact people.
    The account of the supplier is for instances when orders are made on credit.'''
    name = models.CharField(max_length=64)
    contact_person = models.CharField(max_length=64, blank=True, default="")
    physical_address = models.CharField(max_length=128, blank=True, default="")
    telephone = models.CharField(max_length=16, blank=True, default="")
    email = models.EmailField(max_length=64, blank=True, default="")
    website = models.CharField(max_length=64, blank=True, default="")
    active = models.BooleanField(default=True)
    account = models.ForeignKey('accounting.Account', null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk is None:
            n_suppliers = Supplier.objects.all().count()
            self.account = Account.objects.create(
                name= "Supplier: %s" % self.name,
                id = 2100 + n_suppliers,
                balance =0,
                type = 'liability',
                description = 'Account which represents debt owed to a supplier',
                balance_sheet_category='current-liabilities'
            )
        
        super(Supplier, self).save(*args, **kwargs)
        


PRICING_CHOICES = [
    (0, 'Manual'),
    (1, 'Margin'),
    (2, 'Markup')
]

class Item(models.Model):
    '''The most basic element of inventory. Represents tangible products that are sold.
    this model tracks details concerning sale and receipt of products as well as their 
    value and pricing.
    
    methods
    ----------
    increment - increases the stock of the item.
    decrement - decreases the stock of the item.

    properties
    -----------
    stock_value - returns the value of the stock on hand in the inventory
        based on a valuation rule.
    events - returns representations of all the inventory movements by date and 
    description in the last 30 days
    
    '''
    item_name = models.CharField(max_length = 32)
    code = models.AutoField(primary_key=True)
    unit = models.ForeignKey('inventory.UnitOfMeasure', blank=True, default="", null=True)
    
    pricing_method = models.IntegerField(choices=PRICING_CHOICES, default=0)
    direct_price = models.DecimalField(max_digits=9, decimal_places=2)
    margin = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    markup = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    unit_purchase_price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True, default="")
    supplier = models.ForeignKey("inventory.Supplier", blank=True, null=True)
    image = models.FileField(blank=True, null=True, upload_to=settings.MEDIA_ROOT)
    minimum_order_level = models.IntegerField( default=0)
    maximum_stock_level = models.IntegerField(default=0)
    category = models.ForeignKey('inventory.Category', blank=True, null=True)
    sub_category = models.ForeignKey('inventory.Category', 
       related_name='sub_category', blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.code) + " - " + self.item_name

    @property
    def quantity(self):
        #returns quantity from all warehouses
        items = WareHouseItem.objects.filter(item=self)
        return reduce(lambda x, y: x + y, [i.quantity for i in items], 0)
    
    @property
    def unit_sales_price(self):
        if self.pricing_method == 0:
            price = self.direct_price 
        elif self.pricing_method == 1:
            price = D(self.unit_purchase_price / (1 - self.margin))
        else:
            price = D(self.unit_purchase_price * (1 + self.markup))
        config = load_config()
        
        if config.get('auto_adjust_prices', False):
            multiplier = config.get('global_price_multiplier', 0)
            return price + (price * D(multiplier))
        else:
            return price

    @property
    def stock_value(self):
        '''all calculations are based on the last 30 days
        currently implementing the options of fifo and averaging.
        fifo - first in first out, measure the value of the items 
        based on the price they were bought assuming the remaining items 
        are the last ones bought.
        averaging- calculating the overall stock value on the average of all
        the values during the period under consderation.
        '''
        if self.quantity == 0:
            return 0

        config = load_config()
        #dates under consideration 
        TODAY  = datetime.date.today()
        START = TODAY - datetime.timedelta(days=30)
        
        #get the most recent price older than 30 days
        older_items = OrderItem.objects.filter(
            Q(item=self) 
            & Q(received__gt = 0)
            & Q(order__issue_date__lt = START))

        if older_items.count() > 0:
            previous_price = older_items.latest('order__issue_date').order_price
        else:
            #uses the oldest available price. not implemented here
            previous_price = self.unit_purchase_price
         
        # get the ordered items from the last 30 days.
        ordered_in_last_month = OrderItem.objects.filter(
            Q(item=self) 
            & Q(received__gt = 0)
            & Q(order__issue_date__gte = START)
            & Q(order__issue_date__lte =TODAY))

        #calculate the number of items ordered in the last 30 days
        ordered_quantity = reduce(lambda x, y: x + y, 
            [i.received for i in ordered_in_last_month], 0)
        
        #get the value of items ordered in the last month
        total_ordered_value = reduce(lambda x,y: x + y,
            [i.received_total for i in ordered_in_last_month], 0)
        
        #get the number of sold items in the last 30 days
        sold_in_last_month = InvoiceItem.objects.filter(
            Q(item=self)
            & Q(invoice__date_issued__gte = START)
            & Q(invoice__date_issued__lte =TODAY))

        #calculate the number of items sold in that period
        sold_quantity = reduce(lambda x, y: x + y, 
            [i.quantity for i in sold_in_last_month], 0)

        #get the value of the items sold in the last month
        total_sold_value = reduce(lambda x, y: x + y, 
            [i.total_without_discount for i in sold_in_last_month], 0)
        
        #determine the quantity of inventory before the valuation period
        initial_quantity = self.quantity + ordered_quantity - sold_quantity
        
        # get the value of the items before the valuation period
        initial_value = D(initial_quantity) * previous_price
        total_value = 0
        
        #if no valuation system is being used
        if not config.get('inventory_valuation', None):
            return self.unit_sales_price * D(self.quantity)
        else:
            if config['inventory_valuation'] == 'averaging':
                total_value += initial_value
                total_value += total_ordered_value

                average_value = total_value / (ordered_quantity + initial_quantity)
                return average_value 


            elif config['inventory_valuation'] == 'fifo':
                # while loop compares the quantity sold with the intial inventory,
                # and the new inventory after each new order.
                ordered_in_last_month_ordered = list(ordered_in_last_month.order_by(
                    'order__issue_date'))
                quantity = initial_quantity
                index = 0
                while quantity < sold_quantity:
                    quantity += ordered_in_last_month_ordered[index]
                    index += 1

                if index == 0:
                    total_value += initial_value - total_sold_value
                    total_value += total_ordered_value
                    average_value = total_value / D(ordered_quantity + (initial_quantity - sold_quantity))
                    return average_value
                else:
                    remaining_orders = ordered_in_last_month_ordered[index:]
                    total_value = 0
                    for i in remaining_orders:
                        total_value += i.order_price * i.received
                    average_value = total_value / reduce(lambda x,y: x + y, 
                        [i.received for i in remaining_orders], 0)

            else:
                return self.unit_sales_price * D(self.quantity)

    @property
    def sales_to_date(self):
        items = InvoiceItem.objects.filter(item=self)
        total_sales = reduce(lambda x,y: x + y, [item.quantity * item.price for item in items], 0)
        return total_sales
    
    def delete(self):
        self.active = False
        self.save()

    @property
    def events(self):
        class Event:
            def __init__(self, date, description):
                self.date = date
                self.description= description

            def __lt__(self, other):
                return other.date < self.date
        # 30 day limit on event retrieval.
        epoch = datetime.date.today() - datetime.timedelta(days=30)

        #from invoices
        items= [Event(i.invoice.due_date, 
            "removed %d items from inventory as part of invoice #%d." % (i.quantity, i.invoice.pk)) \
                for i in InvoiceItem.objects.filter(Q(item=self) 
                    & Q(invoice__date_issued__gte= epoch))]
        
        # from orders
        orders = [Event(o.order.issue_date, 
            "added %d items to inventory from purchase order #%d." % (o.received, o.order.pk)) \
                for o in OrderItem.objects.filter(Q(item=self) 
                    & Q(order__issue_date__gte= epoch)) if o.received > 0]

        events = items + orders 
        return sorted(events)

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
    
    expected_receipt_date = models.DateField()
    issue_date = models.DateField()
    type_of_order = models.IntegerField(choices=[
        (0, 'Cash Order'),
        (1, 'Deffered Payment Order'),
        (2, 'Pay on Receipt') ], default=0)
    deferred_date = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey('inventory.supplier', blank=True, null=True)
    bill_to = models.CharField(max_length=128, blank=True, default="")
    ship_to = models.ForeignKey('inventory.WareHouse')
    tracking_number = models.CharField(max_length=64, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, choices=[
        ('received', 'Received'),
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ])
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
        return (float(received) / float(n_items)) * 100

    def create_deffered_entry(self):
        j = JournalEntry.objects.create(
                    reference = "Auto generated entry created by order " + str(self),
                    date=self.deferred_date,
                    memo = self.notes,
                    journal = Journal.objects.get(pk=4)
                )
        j.simple_entry(
                    self.total,
                    self.supplier.account, # since we owe the supplier
                    Account.objects.get(pk=4006),#purchases 
                )

    def create_immediate_entry(self):
        j = JournalEntry.objects.create(
                date = self.issue_date,
                reference = "Auto generated entry from order" + str(self),
                memo=self.notes,
                journal = Journal.objects.get(pk=4)
            )
        j.simple_entry(
                self.total,
                Account.objects.get(pk=1000),#cash
                Account.objects.get(pk=4006),#purchases account
            )

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
    order = models.ForeignKey('inventory.Order', null=True)
    item = models.ForeignKey('inventory.item', null=True)
    quantity = models.FloatField()
    #change and move this to the item
    #make changes to the react app as well
    order_price = models.DecimalField(max_digits=6, decimal_places=2)
    received = models.FloatField(default=0.0)

    @property
    def fully_received(self):
        if self.received < self.quantity:
            return False
        return True

    def receive(self, n):
        n= float(n)
        self.received += n
        
        if not self.order.ship_to.has_item(self.item):
            #item does not yet exist
            wh_item = WareHouseItem.objects.create(item=self.item,
                quantity = n,
                warehouse=self.order.ship_to)
        else:
            wh_item = WareHouseItem.objects.get(warehouse=self.order.ship_to, 
            item= self.item)
            wh_item.increment(n)

        self.item.unit_purchase_price = self.order_price
        self.item.save()
        self.save()
        
    def __str__(self):
        return str(self.item) + ' -' + str(self.order_price)

    def save(self, *args, **kwargs):
        if not self.order_price:
            self.order_price = self.item.unit_purchase_price
        else:
            self.item.unit_purchase_price = self.order_price
            self.item.save()
        super(OrderItem, self).save(*args, **kwargs)
        
    @property
    def received_total(self):
        return D(self.received)  * self.order_price

    @property
    def subtotal(self):
        return D(self.quantity) * self.order_price

class UnitOfMeasure(models.Model):
    '''Simple class for representing units of inventory.'''
    name = models.CharField(max_length=64)
    description = models.TextField(default="")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    '''Used to organize inventory'''
    name = models.CharField(max_length=64)
    description = models.TextField(default="")

    def __str__(self):
        return self.name

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
    order = models.ForeignKey('inventory.Order', null=True)
    #received_by = models.ForeignKey('employees.Employee', 
    #    null=True, limit_choices_to=Q(user__isnull=False))
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
            Account.objects.get(pk=1000),#checking account
            Account.objects.get(pk=1004),#inventory
        )
        

class WareHouse(models.Model):
    name = models.CharField(max_length=128)
    address = models.TextField()
    
    @property
    def all_items(self):
        return self.warehouseitem_set.all()

    def decrement_item(self, item, quantity):
        #safety checks handled elsewhere
        #created to avoid circular imports in invoices
        self.get_item(item).decrement(quantity)


    def has_item(self, item):
        return(
            WareHouseItem.objects.filter(item=item, warehouse=self).count() > 0
        ) 
            
    
    def get_item(self, item):
        if self.has_item(item):
            return WareHouseItem.objects.get(item=item, warehouse=self)
        else:
             return None
    
    def add_item(self, item, quantity):
        #check if record of item is already in warehouse
        if self.has_item(item):
            self.get_item().increment(quantity)
        else:
            self.warehouseitem_set.create(item=item, quantity=quantity)

    def transfer(self, other, item, quantity):
        #transfer stock from current warehouse to other warehouse
        
        if not other.has_item(item):
            raise Exception('The destination warehouse does not stock this item')
        elif not self.has_item(item):
            raise Exception('The source warehouse does not stock this item')

        else:
            other.get_item(item).increment(quantity)
            self.get_item(item).decrement(quantity)
            # for successful transfers, record the transfer cost some way

    def __str__(self):
        return self.name

class WareHouseItem(models.Model):
    item = models.ForeignKey('inventory.Item')
    quantity = models.FloatField()
    warehouse = models.ForeignKey('inventory.Warehouse', null=True)

    def increment(self, amt):
        amount = float(amt)
        if self.quantity + amount > self.item.maximum_stock_level:
            raise Exception('Stock level will exceed maximum allowed')
        self.quantity += amount
        self.save()
        return self.quantity

    def decrement(self, amt):
        amount = float(amt)
        if self.quantity < amount:
            raise ValueError('Cannot have a quantity less than zero')
        self.quantity -= amount
        self.save()
        # check if min stock level is exceeded
        return self.quantity

