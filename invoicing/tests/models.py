import datetime
from decimal import Decimal as D

from django.db.models import Q
from django.test import Client, TestCase
from django.urls import reverse

from common_data.models import Individual, Organization
from inventory.models import WareHouseItem
from invoicing.models import *
from .model_util import InvoicingModelCreator
from inventory.tests.model_util import InventoryModelCreator
TODAY = datetime.date.today()



class CommonModelTests(TestCase):
    fixtures = ['common.json','invoicing.json']
        
    def test_update_sales_config(self):
        obj = SalesConfig.objects.get(pk=1)
        obj.default_invoice_comments = "Test comment"
        self.assertIsInstance(obj, SalesConfig)


class CustomerModelTests(TestCase):
    fixtures = ['common.json','invoicing.json']
        
    @classmethod
    def setUpTestData(cls):
        cls.imc = InvoicingModelCreator(cls)
        cls.imc.create_all()

    def setUp(self):
        self.imc.create_invoice()

    def tearDown(self):
        for i in Invoice.objects.all():
            i.delete()

    def test_create_individual_customer(self):
        obj = Customer.objects.filter(individual__isnull=False).first()
        self.assertIsInstance(obj, Customer)

    def test_create_organization_customer(self):
        obj = Customer.objects.filter(organization__isnull=False).first()
        self.assertIsInstance(obj, Customer)

    def test_customer_email(self):
        self.assertIsInstance(self.customer_org.customer_email, str)
        self.assertIsInstance(self.customer_ind.customer_email, str)

    def test_customer_name(self):
        self.assertIsInstance(self.customer_ind.name, str)
        self.assertIsInstance(self.customer_org.name, str)

    def test_customer_type(self):
        self.assertTrue(self.customer_org.is_organization)
        self.assertFalse(self.customer_ind.is_organization)

  
    def test_invoices_property(self):
        '''Invoice created in model creator'''
        self.assertEqual(len([i for i in self.customer_org.invoices]), 1)

    def test_credit_invoices(self):        
        self.assertEqual(len(self.customer_org.credit_invoices), 1)
        #once paid the credit should go down to zero
        self.invoice.status='paid'
        self.invoice.save()
        self.assertEqual(len(self.customer_org.credit_invoices), 0)

    def test_age_list(self):
        self.invoice.due = TODAY - datetime.timedelta(days=8)
        self.invoice.save()
        self.assertEqual(self.customer_org.age_list, [0, 0,D(190.0), 0, 0, 0])


class PaymentModelTests(TestCase):
    fixtures = ['common.json','invoicing.json', 'inventory']
        
    @classmethod
    def setUpTestData(cls):
        imc = InvoicingModelCreator(cls)
        imc.create_all()

    def test_create_payment(self):
        self.assertIsInstance(self.payment, Payment)


    def test_payment_due(self):
        '''invoice value $210, payment value $10'''
        self.assertEqual(self.payment.due, D(200))

   


class SalesRepModelTests(TestCase):
    fixtures = ['common.json','invoicing.json', 'inventory.json']
        
    @classmethod
    def setUpTestData(cls):
        imc = InvoicingModelCreator(cls)
        imc.create_all()
    


class CreditNoteModelTests(TestCase):
    fixtures = ['common.json','invoicing.json', 'inventory.json']

    @classmethod
    def setUpTestData(cls):
        cls.imc = InvoicingModelCreator(cls)
        cls.imc.create_credit_note()
        cls.imc.create_credit_note_line()
    
    def test_create_credit_note(self):
        self.assertIsInstance(self.credit_note, CreditNote)

    def test_returned_products(self):
        self.assertEqual(self.credit_note.returned_products.count(), 1)


    def test_returned_total(self):
        self.assertEqual(self.credit_note.returned_total, 10)



    def test_credit_note_tax_credit(self):
        self.assertEqual(self.credit_note.tax_credit, 0)

    def test_returned_total_with_tax(self):
        self.assertEqual(self.credit_note.returned_total_with_tax, 10)


class ProductInvoiceTests(TestCase):
    fixtures = ['common.json','invoicing.json', 'inventory.json']
    
    @classmethod
    def setUpTestData(cls):
        invmc = InventoryModelCreator(cls)
        invmc.create_warehouse_item()
        invmc.create_orderitem()
        cls.imc = InvoicingModelCreator(cls)
        cls.imc.create_all()

    def test_create_invoice(self):
        self.assertIsInstance(self.invoice, Invoice)

    def test_overdue(self):
        self.invoice.due = datetime.date.today() + datetime.timedelta(days=1)
        self.invoice.save()
        self.assertFalse(self.invoice.overdue)
        self.invoice.due = datetime.date.today() - datetime.timedelta(days=1)
        self.invoice.save()        
        self.assertTrue(self.invoice.overdue)


    def test_set_quote_invoice_number(self):
        old_status = self.invoice.status
        self.invoice.status = 'quotation'
        self.invoice.save()
        self.invoice.set_quote_invoice_number()
        self.assertEqual(self.invoice.quotation_number, 2)
        self.invoice.status = old_status
        self.invoice.save()
        self.invoice.set_quote_invoice_number()
        self.assertEqual(self.invoice.invoice_number, 1)


    def test_sales_invoice_cost_of_goods_sold(self):
        self.assertEqual(self.invoice.cost_of_goods_sold, 10)

    def test_total(self):
        self.product_line.tax = 15
        self.product_line.save()
        self.assertAlmostEqual(self.invoice.total, D('211.50'))
        self.product_line.tax=None
        self.product_line.save()

    def test_on_credit(self):
        self.assertFalse(self.invoice.on_credit)
        self.invoice.due = TODAY
        self.invoice.status = 'invoice'
        self.invoice.date = TODAY - datetime.timedelta(days=1)
        self.invoice.save()
        self.assertTrue(self.invoice.on_credit)
        self.invoice.due = TODAY
        self.invoice.save()

    def test_total_paid(self):
        self.assertEqual(self.invoice.total_paid, 10)
        
    def test_total_due(self):
        '''the difference between the invoice total $210 and the payment $10'''
        self.assertEqual(self.invoice.total_due, 190)

    def test_tax_amount(self):
        '''15% tax on $10'''
        self.product_line.tax = 15
        self.product_line.save()
        self.assertAlmostEqual(self.invoice.tax_amount, D('1.50'))
        self.product_line.tax=15
        self.product_line.save()

    def test_subtotal(self):
        self.assertEqual(self.invoice.subtotal, D(210.0))


    def test_returned_total(self):
        pass #TODO fix

    def test_update_inventory(self):

        wh_item = WareHouseItem.objects.get(item=self.product)
        initial_quantity = wh_item.quantity
        self.invoice.update_inventory()
        wh_item = WareHouseItem.objects.get(item=self.product)
        self.assertEqual(wh_item.quantity, initial_quantity - 1)
        wh_item.quantity = 10
        wh_item.save()

    def test_create_sales_invoice_line(self):
        self.assertIsInstance(self.product_line, InvoiceLine)
        
    def test_set_value_of_goods(self):
        self.assertEqual(self.product_line.value, 10)
        

    def test_return_invoice_line(self):
        self.product_line._return(1)
        self.assertTrue(self.product_line.product.returned)
        
    def test_returned_value(self):
        self.product_line._return(1)
        # TODO fix

    def test_line_check_inventory(self):
        # TODO expand tests
        data = self.product_line.check_inventory()
        self.assertIsInstance(data, dict)


    def test_invoice_verify_inventory(self):
        shortages = self.invoice.verify_inventory()
        self.assertEqual(len(shortages), 0)

    def test_verify_inventory_with_shortages(self):
        component = ProductLineComponent.objects.create(
            quantity=1000,
            product=self.product
        )
        line = InvoiceLine.objects.create(
            invoice=self.invoice,
            product=component,
            line_type=1   
        )
        shortages = self.invoice.verify_inventory()
        self.assertEqual(len(shortages), 1)

        #teardown
        line.delete()
        component.delete()


    def test_quotation_is_valid(self):
        self.assertTrue(self.quotation.quotation_is_valid)



class InvoiceModelTests(TestCase):
    fixtures = ['common.json','invoicing.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.imc = InvoicingModelCreator(cls)
        cls.imc.create_all()
        #create request
        

    def test_add_product_line(self):
        pre_total = self.invoice.subtotal
        self.invoice.add_line({
            'type': 'product',
            'selected': '1-name',
            'quantity': 1,            
            'tax': 15,
            'discount': '0',
            'unitPrice': 50.00
        })
        self.assertEqual(self.invoice.total, pre_total + 50)

    def test_add_service_line(self):
        pre_total = self.invoice.subtotal
        self.invoice.add_line({
            'type': 'service',
            'selected': '1-name',
            'hours': 0,
            'tax': 15,
            'fee': '200',
            'discount': '0',
            'rate': 50
        })
        self.assertEqual(self.invoice.total, pre_total + 200)

   


    def test_line_subtotal(self):
        self.assertEqual(self.product_line.subtotal, 10)
        self.assertEqual(self.service_line.subtotal, 100)


    def test_invoice_str(self):
        self.assertIsInstance(str(self.product_line), str)
        self.assertIsInstance(str(self.service_line), str)

    def test_service_line_line_property(self):
        self.assertIsInstance(self.service_line.line, InvoiceLine)

   
    def test_service_gross_income(self):
        pass