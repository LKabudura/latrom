
import datetime
import itertools
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone

from invoicing import models as inv_models
from common_data.models import SoftDeletionModel
import inventory
from invoicing.models.credit_note import CreditNoteLine
from django.shortcuts import reverse 

class Invoice(SoftDeletionModel):
    '''An invoice is a document that represents a sale. Because of the complexity of the object, both a quotation and an invoice are represented by the same model. The document starts as a quotation and then can move to a proforma invoice culminating in the creation of an invoice.
    In each stage the document can be considered a draft in which case no journal entries are made and no fiscalization takes place. Only non draft invoices can be sent
    
    
    methods
    -------
    add_line 
    set_quote_invoice_number
    _line_total - 
    _line_getter - gets all the invoice lines of a certain type


    

    properties
    --------
    overdue - bool
    overdue_days - int
    total - decimal
    is_quotation - bool
    is_credit -bool
    total_paid - decimal
    total_due - the remainder fo payments
    tax_amount - decimal
    subtotal -decimal
    sales_lines
    sales_total
    service_lines
    service_total
    total_shipping_costs
    percentage_shipping_cost
    returned_total
    sales_only 
    service_only



    '''
    DEFAULT_WAREHOUSE = 1 #use  fixture
    DEFAULT_SALES_REP = 1
    DEFAULT_CUSTOMER = 1
    SALE_STATUS = [
        ('quotation', 'Quotation'),
        ('proforma', 'Proforma Invoice'),
        ('invoice', 'Invoice'),
        ('paid', 'Paid In Full'),
        ('paid-partially', 'Paid Partially'),
    ]# reversal is handled in credit notes

    status = models.CharField(max_length=16, choices=SALE_STATUS)
    invoice_number = models.PositiveIntegerField(null=True)
    quotation_number = models.PositiveIntegerField(null=True)
    quotation_date = models.DateField(blank=True, null=True)
    quotation_valid= models.DateField(blank=True, null=True)
    invoice_validated_by = models.ForeignKey('auth.user', 
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL)
    draft = models.BooleanField(blank=True, default=True)
    customer = models.ForeignKey("invoicing.Customer", 
        on_delete=models.SET_NULL, 
        null=True,
        default=DEFAULT_CUSTOMER)
    salesperson = models.CharField(max_length=64)
    due= models.DateField( default=datetime.date.today)
    date= models.DateField(default=datetime.date.today)
    terms = models.CharField(max_length = 128, 
        blank=True)
    comments = models.TextField(blank=True)
    purchase_order_number = models.CharField(blank=True, 
        max_length=32)
    #product sales specific fields 
    ship_from = models.ForeignKey('inventory.WareHouse', 
        on_delete=models.SET_NULL, 
        null=True,
        default=DEFAULT_WAREHOUSE)
    
    def get_absolute_url(self):
        if self.status in ['invoice', 'proforma','paid', 'paid-partially']:
            return reverse("invoicing:invoice-details", kwargs={"pk": self.pk})
        else:
            return reverse("invoicing:quotation-details", kwargs={
                'pk': self.pk
            })

    def add_line(self, data):
        '''Takes a dictionary that represents the invoice line and create
        the appropriate objects to match the provided data'''
        tax = data['tax']
        
        discount = D(data['discount'])
        if data['type'] == 'product':
            pk = data['selected'].split('-')[0]
            product = inventory.models.InventoryItem.objects.get(pk=pk)
            component = ProductLineComponent.objects.create(
                product=product,
                quantity=data['quantity'],
                unit_price= data['unitPrice']
                
            )
            line = self.invoiceline_set.create(
                line_type=1,#product 
                product=component,
                tax=tax,
                discount=discount
            )
            
            

       
    def update_inventory(self):
        '''Removes inventory from the warehouse'''
        #called in views.py
        for line in self.invoiceline_set.filter(product__isnull=False):
            #check if ship_from has the product in sufficient quantity
            self.ship_from.decrement_item(line.product.product, line.quantity)

    def verify_inventory(self):
        '''Iterates over all the invoice lines and appends checks that indicate 
            shortages. returns a list of these checks'''
        shortages = []
        for line in self.invoiceline_set.filter(product__isnull=False):
            shortage = line.product.check_inventory()
            if shortage['quantity'] > 0:
                shortages.append(shortage)

               
        return shortages

    @property 
    def cost_of_goods_sold(self):
        '''calculates the value of each line in the invoice and returns their 
        sum'''
        return sum([line.product.value for line in self.invoiceline_set.filter(
            product__isnull=False)], D(0.0))

    @property
    def overdue(self):
        '''returns boolean only if it is a valid invoice'''
        if self.status in ['invoice', 'paid-partially'] and not self.draft:
            return self.overdue_days > 0
        return False

    @property
    def overdue_days(self):
        '''returns days due'''
        TODAY = timezone.now().date()
        if TODAY > self.due:
            return (TODAY - self.due).days
        return 0
        
    @property
    def total(self):
        '''the total value of the invoice inclusive of tax'''
        return self.subtotal + self.tax_amount

    @property
    def is_quotation(self):
        '''checks if the invoice is a quotation'''
        return self.status == 'quotation'

    @property
    def on_credit(self):
        '''Checks if the invoice is on credit returns bool'''
        return self.status in ['invoice', 'paid-partially'] and not self.draft \
            and self.due > self.date 

    @property
    def total_paid(self):
        '''Returns the total value of payments made towards the invoice'''
        return sum([p.amount for p in self.payment_set.all()])

    @property
    def total_due(self):
        '''The remaining balance left to be paid on an invoice'''
        return self.total - self.total_paid - self.total_credited

    @property
    def total_credited(self):
        """Returns the total value of all credit notes on invoice"""
        return sum([i.total for i in self.creditnote_set.all()])

    @property
    def tax_amount(self):
        '''The amount of tax paid on the invoice calculated as a total from each line'''
        return sum([i.tax_ for i in self.invoiceline_set.all()])

    @property
    def subtotal(self):
        '''The total of the invoice minus tax including discounts'''
        
        return sum([i.subtotal for i in self.invoiceline_set.all()])

    def __str__(self):
        return 'INV' + str(self.pk)

    @property
    def quotation_is_valid(self):
        return self.status == "quotation" and \
            self.quotation_valid and \
            self.quotation_valid >= datetime.date.today()
        

    def set_quote_invoice_number(self):
        '''This method is called when the invoice is created to follow the numbering sequence stored in the sales config '''
        config = inv_models.SalesConfig.objects.first() 
        if self.is_quotation:
            if self.quotation_number is None:
                self.quotation_number = config.next_quotation_number
                config.next_quotation_number += 1
                config.save()
                self.save()
        elif self.status != 'draft':
            if self.invoice_number is None:
                self.invoice_number = config.next_invoice_number
                config.next_invoice_number += 1
                config.save()
                self.save()
        else:
            return

   

    def _line_total(self, line_type):
        '''Calculates the total value of a certain type of invoice line'''
        return sum([line.subtotal for line in line_type], D(0))

    def _line_getter(self, type_id):
        '''Retrives all the lines in a the invoice of a certain type'''
        return InvoiceLine.objects.filter(
            Q(invoice=self) & Q(line_type=type_id))
    
    @property
    def sales_lines(self):
        '''Returns all product sales lines'''
        return self._line_getter(1)

    @property 
    def sales_total(self):
        '''Returns numeric total of product sales'''
        return self._line_total(self.sales_lines)


    @property
    def service_lines(self):
        '''Returns all service sales lines'''
        return self._line_getter(2)

    @property
    def service_total(self):
        '''Returns all invoice lines for services '''
        return self._line_total(self.service_lines)
        


    @property
    def returned_total(self):
        '''returns the value of products returned to the warehouse'''
        return sum([
            i.product.returned_value for i in self.invoiceline_set.all() \
                if i.product ])


    @property
    def sales_only(self):
        '''returns true if all lines are product lines'''
        return all([True if line.product != None else False \
            for line in self.invoiceline_set.all() ])


    @property
    def service_only(self):
        '''returns true if all lines are service lines'''
        return all([True if line.service != None else False \
            for line in self.invoiceline_set.all() ])
            

            
    def save(self, *args, **kwargs):
        '''Makes sure that every invoice and quotation is numbered.
        Also makes sure that each service has a valid work order request'''
        super().save(*args, **kwargs)
        self.set_quote_invoice_number()


class InvoiceLine(models.Model):
    LINE_CHOICES = [
        (1, 'product'),
        (2, 'service'),
    ]
    invoice = models.ForeignKey('invoicing.Invoice', 
        on_delete=models.SET_NULL, 
        null=True, 
        default=1)
    product = models.OneToOneField('invoicing.ProductLineComponent',
        on_delete=models.SET_NULL, 
        null=True, )
    service = models.OneToOneField('invoicing.ServiceLineComponent',
        on_delete=models.SET_NULL, 
        null=True,)
    line_type = models.PositiveSmallIntegerField(choices=LINE_CHOICES)
    tax = models.FloatField(default=0.0)
    discount =models.DecimalField(max_digits=16, decimal_places=2, default=0.0)

    #what it is sold for
    
    @property
    def type_string(self):
        mapping = {
            1: 'product',
            2: 'service',
        }
        return mapping[self.line_type]

    @property 
    def component(self):
        mapping = {
            1: self.product,
            2: self.service,
        }

        return mapping[self.line_type]
    
    @property
    def name(self):
        if self.line_type == 1:
            return str(self.component.product).split('-')[1]
        elif self.line_type == 2:
            return self.component.service
        

    def __str__(self):
        if not self.component:
            return "<INVALID INVOICE LINE>"

        if self.line_type == 1:
            return '[PRODUCT] {} x {} @ ${:0.2f}{}'.format(
                self.component.quantity,
                self.name,
                self.unit_price,
                self.component.product.unit
            )
        elif self.line_type == 2:
            ret_string = f'[SERVICE] {self.name}'
            if self.component.flat_fee > 0:
                ret_string += ' Flat rate: {:0.2f}'.format(
                    self.component.flat_fee
                )
            if self.component.hours > 0 and \
                    self.component.hourly_rate > 0:
                ret_string +=  '+ {}Hrs @ ${:0.2f}/Hr'.format(
                    self.component.hours,
                    self.component.hourly_rate)
            
            return ret_string

        

    @property
    def subtotal(self):
        '''Returns the value of the line after the discount and before taxes'''
        return self.nominal_price - self.discount_total

    @property
    def total(self):
        '''Includes price after discount and tax'''
        if not self.component:
            return 0
        
        return self.subtotal + self.tax_

    @property
    def discount_total(self):
        '''Returns the value subtracted from the nominal price due to a discount'''
        return D(self.nominal_price) * (D(self.discount) / D(100.0))

    @property
    def tax_(self):
        '''Returns the tax obtained from an invoice line'''
        if self.tax == None:
            return D(0)
        
        return self.subtotal * D(self.tax/100.0)

    @property
    def nominal_price(self):
        if self.product:
            return self.quantity * self.unit_price
        return self.flat_fee  + (D(self.hours) * D(self.hourly_rate))

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)

        except AttributeError as attrerr:
            if self.product and hasattr(self.product, name):
                return getattr(self.product, name)
            elif self.service and hasattr(self.service, name):
                return getattr(self.service, name)
            
            
            raise attrerr
        raise AttributeError(f"{type(self)} has no attribute '{name}'")
    
class ProductLineComponent(models.Model):
    product = models.ForeignKey('inventory.InventoryItem', null=True, 
        on_delete=models.SET_NULL)
    returned = models.BooleanField(default=False)
    unit_price = models.DecimalField(max_digits=16, 
        decimal_places=2, 
        default=0.0)

    # value is calculated once when the invoice is generated to prevent 
    # distortions as prices change
    #what it is worth to the business
    value = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    quantity = models.DecimalField(
        max_digits=16, 
        decimal_places=2, 
        default=0.0)  

    @property
    def nominal_price(self):
        '''The price of the line without discount and taxes'''
        return self.quantity * self.unit_price

    @property 
    def line(self):
        '''The invoice line the component belongs to'''
        if InvoiceLine.objects.filter(product=self).exists():
            return InvoiceLine.objects.get(product=self)
        return None

    @property
    def returned_quantity(self):
        '''The returns effected by credit notes for this particular invoice 
        line'''
        if self.line:
            return sum([ item.quantity \
                for item in CreditNoteLine.objects.filter(line=self.line)])
        return 0

    def __str__(self):
        return str(self.product)


    def _return(self, quantity):
        self.returned = True
        #Must increment inventory here !! Important
        # increment inventory here. Can be scrapped later or just kept in 
        # inventory if ok
        self.invoiceline.invoice.ship_from.add_item(self.product, quantity)
        self.save()

    def set_value(self):
        self.value = self.product.unit_value * D(self.quantity)
        self.save()

    @property
    def returned_value(self):
        '''accounting for discount and tax in unit pricing'''
        if self.quantity > 0:
            invoiced_unit_price = self.line.total / self.quantity
        else: return 0
        
        return invoiced_unit_price * D(self.returned_quantity)

    def check_inventory(self):
        '''Checks the shipping warehouse for the required quantity of inventory
        if a shortage is present return a dict with the product name and the 
        shortage.
        checks also if pending orders will meet demand in time for the invoices 
        '''
        if self.invoiceline.invoice.ship_from.has_item(self.product):
            wh_item = self.invoiceline.invoice.ship_from.get_item(self.product)
            if wh_item.quantity >= self.quantity:
                return {
                    'product': self.product,
                    'quantity': 0
                }
            else:
                return {
                    'product': self.product,
                    'quantity': self.quantity - D(wh_item.quantity)
                }
        else:
            return {
                'product': self.product,
                'quantity': self.quantity
            }
        pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.returned_quantity > 0:
            self.returned = True

        if self.value == D(0.0) and \
                self.product.product_component.unit_value > D(0.0):
            self.set_value()  
        if self.unit_price == D(0.0) and \
                self.product.product_component.unit_sales_price != 0:
            self.unit_price = self.product.product_component.unit_sales_price
            self.save()
        

class ServiceLineComponent(models.Model):
    service = models.CharField(max_length=255)
    hours = models.DecimalField(
        max_digits=16, 
        decimal_places=2, 
        default=0.0)
    flat_fee = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    hourly_rate = models.DecimalField(max_digits=16, decimal_places=2, 
        default=0.0)

    def __str__(self):
        return str(self.service)

    @property
    def nominal_price(self):
        '''Returns the value of the line excluding taxes and discounts'''
        return self.flat_fee  + (D(self.hours) * D(self.hourly_rate))

    @property
    def line(self):
        '''Returns the invoice line the component belongs to'''
        if InvoiceLine.objects.filter(service=self).exists():
            return InvoiceLine.objects.get(service=self)

        return None



    @property
    def gross_income(self):
        return self.invoiceline.subtotal - self.cost_of_sale


    @property
    def nominal_price(self):
        return self.price
