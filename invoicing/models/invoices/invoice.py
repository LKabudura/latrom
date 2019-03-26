
import datetime
import itertools
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone

from accounting.models import Account, Expense, Journal, JournalEntry, Tax
from invoicing import models as inv_models
from services.models import Service
from common_data.models import SoftDeletionModel
import inventory
from services.models import WorkOrderRequest
from invoicing.models.credit_note import CreditNoteLine

class Invoice(SoftDeletionModel):
    '''An invoice is a document that represents a sale. Because of the complexity of the object, both a quotation and an invoice are represented by the same model. The document starts as a quotation and then can move to a proforma invoice culminating in the creation of an invoice.
    In each stage the document can be considered a draft in which case no journal entries are made and no fiscalization takes place. Only non draft invoices can be sent'''
    DEFAULT_TAX = 1
    DEFAULT_WAREHOUSE = 1 #make fixture
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
    salesperson = models.ForeignKey('invoicing.SalesRepresentative',
        on_delete=models.SET_NULL, 
        null=True, 
        default=DEFAULT_SALES_REP)
    due= models.DateField( default=datetime.date.today)
    date= models.DateField(default=datetime.date.today)
    discount = models.DecimalField(max_digits=6, 
        decimal_places=2, 
        default=0.0)
    tax = models.ForeignKey('accounting.Tax', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True)
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
    shipping_expenses = models.ManyToManyField('accounting.Expense')
    
    entry = models.ForeignKey('accounting.JournalEntry', 
        on_delete=models.SET_NULL,  blank=True, null=True)
    
    def add_line(self, data):
        if data['type'] == 'product':
            pk = data['selected'].split('-')[0]
            product = inventory.models.InventoryItem.objects.get(pk=pk)
            component = ProductLineComponent.objects.create(
                product=product,
                quantity=data['quantity']
            )
            line = self.invoiceline_set.create(
                line_type=1,#product 
                product=component
            )
            
        elif data['type'] == 'service':
            pk = data['selected'].split('-')[0]
            service = Service.objects.get(pk=pk)
            component = ServiceLineComponent.objects.create(
                service=service,
                hours=data['hours']
            )
            self.invoiceline_set.create(
                line_type=2,#service
                service=component
            )

            if not self.status in ['quotation', 'draft']:
                if not WorkOrderRequest.objects.filter(
                        invoice=self, service=service).exists():
                    WorkOrderRequest.objects.create(
                        invoice=self, 
                        service=service,
                        status="request"
                    )

        elif data['type'] == 'expense':
            pk = data['selected'].split('-')[0]
            expense = Expense.objects.get(pk=pk)
            component = ExpenseLineComponent.objects.create(
                expense=expense
            )
            self.invoiceline_set.create(
                line_type=3,#expense
                expense=component
            )

    @property
    def overdue(self):
        '''returns boolean'''
        return self.overdue_days < 0

    @property
    def overdue_days(self):
        '''returns days due'''
        TODAY = timezone.now().date()

        if self.due < TODAY:
            return (self.due - TODAY).days
        return 0
        
    @property
    def total(self):
        return self.subtotal + self.tax_amount

    @property
    def is_quotation(self):
        return self.status == 'quotation'

    @property
    def on_credit(self):
        # might need to improve the logic
        return self.status == 'invoice' and \
            self.due < self.date and \
            self.total_due > 0

    @property
    def total_paid(self):
        return sum(
            [p.amount for p in self.payment_set.all()])

    @property
    def total_due(self):
        return self.total - self.total_paid

    @property
    def tax_amount(self):
        if self.tax and self.tax.rate != 0:
            return self.subtotal * D((self.tax.rate / 100.0)).quantize(D('1.00'))
        return 0

    @property
    def subtotal(self):
        return sum(
            [i.subtotal for i in self.invoiceline_set.all()])

    def __str__(self):
        return 'INV' + str(self.pk)

    def set_quote_invoice_number(self):
        # add feature to allow invoices to be viewed as
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

    def create_entry(self):
        j = JournalEntry.objects.create(
                memo= 'Auto generated entry from invoice.',
                date=self.date,
                journal =Journal.objects.get(pk=1),#Cash receipts Journal
                created_by = self.salesperson.employee.user,
                draft=False
            )

        j.credit(self.subtotal, Account.objects.get(pk=4000))

        j.debit(self.total, self.customer.account)

        if self.tax_amount > D(0):
            j.credit(self.tax_amount, Account.objects.get(pk=2001))#sales tax

        self.entry = j
        self.save()
        return j

    def _line_total(self, line_type):
        total = D(0)
        for line in line_type:
            total += line.subtotal

        return total

    def _line_getter(self, type_id):
        return InvoiceLine.objects.filter(
            Q(invoice=self) & Q(line_type=type_id))
    
    @property
    def sales_lines(self):
        return self._line_getter(1)

    @property 
    def sales_total(self):
        return self._line_total(self.sales_lines)


    @property
    def service_lines(self):
        return self._line_getter(2)

    @property
    def service_total(self):
        return self._line_total(self.service_lines)
        

    @property
    def expense_lines(self):
        return self._line_getter(3)

    @property
    def expense_total(self):
        return self._line_total(self.expense_lines)

    #sales specific expenses
    @property
    def total_shipping_costs(self):
        # TODO test
        return sum([e.amount for  e in self.shipping_expenses.all()])

    @property
    def percentage_shipping_cost(self):
        return (float(self.total_shipping_costs) / float(self.total)) * 100.0

    @property
    def returned_total(self):
        return sum(
            [i.returned_value for i in self.invoiceline_set.all()])


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        #move to view
        config = inv_models.SalesConfig.objects.first()
        if self.tax is None and config.sales_tax is not None:
            self.tax = config.sales_tax
            self.save()
        self.set_quote_invoice_number()


class InvoiceLine(models.Model):
    LINE_CHOICES = [
        (1, 'product'),
        (2, 'service'),
        (3, 'expense'),
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
    expense = models.OneToOneField("invoicing.ExpenseLineComponent", 
        on_delete=models.SET_NULL, 
        null=True,)
    line_type = models.PositiveSmallIntegerField(choices=LINE_CHOICES)
    #what it is sold for
    
    @property 
    def component(self):
        mapping = {
            1: self.product,
            2: self.service,
            3: self.expense
        }

        return mapping[self.line_type]
    
    def __str__(self):
        if not self.component:
            return "<INVALID INVOICE LINE>"
        if self.line_type == 1:
            return '[PRODUCT] {} x {} @ ${:0.2f}{}'.format(
                self.component.quantity,
                str(self.component.product).split('-')[1],
                self.component.price,
                self.component.product.unit
            )
        elif self.line_type == 2:
            return '[SERVICE] {} Flat fee: ${:0.2f} + {}Hrs @ ${:0.2f}/Hr'.format(
                self.component.service.name,
                self.component.service.flat_fee,
                self.component.hours,
                self.component.service.hourly_rate
            )
        elif self.line_type ==3:
            return '[BILLABE EXPENSE] %s' % self.expense.expense.description

    
    @property
    def subtotal(self):
        if not self.component:
            return 0
        return self.component.subtotal
        


class ProductLineComponent(models.Model):
    product = models.ForeignKey('inventory.InventoryItem', null=True, 
        on_delete=models.SET_NULL)
    returned = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)

    # value is calculated once when the invoice is generated to prevent 
    # distortions as prices change
    #what it is worth to the business
    value = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    quantity = models.DecimalField(
        max_digits=9, 
        decimal_places=2, 
        default=0.0)  

    @property 
    def line(self):
        if InvoiceLine.objects.filter(product=self).exists():
            return InvoiceLine.objects.get(product=self)
        return None

    @property
    def returned_quantity(self):
        if self.line:
            return sum([ item.quantity \
                for item in CreditNoteLine.objects.filter(line=self.line)])
        return 0

    def __str__(self):
        return str(self.product)

    @property
    def subtotal(self):
        return D(self.quantity) * self.price

    def _return(self, quantity):
        self.returned = True
        # TODO should i increase inventory quantity here?
        self.save()

    def set_value(self):
        self.value = self.product.stock_value * D(self.quantity)
        self.save()

    @property
    def returned_value(self):
        if self.price == D(0.0):
            return self.product.unit_sales_price * D(self.returned_quantity)
        return self.price * D(self.returned_quantity)

    def check_inventory(self):
        '''Checks the shipping warehouse for the required quantity of inventory
        if a shortage is present return a dict with the product name and the 
        shortage.
        checks also if pending orders will meet demand in time for the invoices 
        '''
        if self.invoice.ship_from.has_item(self.product):
            wh_item = self.invoice.ship_from.get_item(self.product)
            if wh_item.quantity >= self.quantity:
                return {
                    'product': self.product,
                    'quantity': 0
                }
            else:
                return {
                    'product': self.product,
                    'quantity': self.quantity - wh_item.quantity
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
        
        if self.price == 0.0 and self.product.unit_sales_price != D(0.0):
            self.price = self.product.unit_sales_price
            self.save()

        if self.value == D(0.0) and \
                self.product.product_component.stock_value > D(0.0):
            self.set_value()  

class ServiceLineComponent(models.Model):
    service = models.ForeignKey('services.service',
        on_delete=models.SET_NULL, null=True)
    hours = models.DecimalField(
        max_digits=9, 
        decimal_places=2, 
        default=0.0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)

    @property
    def line(self):
        if InvoiceLine.objects.filter(service=self).exists():
            return InvoiceLine.objects.get(service=self)

        return None

    @property
    def subtotal(self):
        product = float(self.hours) * float(self.service.hourly_rate)
        return D(float(self.service.flat_fee) + product)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.price == 0.0 and self.subtotal > 0:
            self.price = self.subtotal
            self.save()

        

class ExpenseLineComponent(models.Model):
    expense = models.ForeignKey('accounting.Expense', 
        on_delete=models.SET_NULL, 
        null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)

    @property
    def line(self):
        if InvoiceLine.objects.filter(expense=self).exists():
            return InvoiceLine.objects.get(expense=self)

        return None

    @property
    def subtotal(self):
        return self.price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.price == 0.0 and self.expense and self.expense.amount > 0:
            self.price = self.expense.amount
            self.save()