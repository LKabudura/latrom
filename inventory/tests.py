# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import urllib
import datetime
from django.utils import timezone
from common_data.tests import create_test_user, create_account_models

from django.test import TestCase,Client
from django.urls import reverse
import models 
from accounting.models import Account, JournalEntry

TODAY = datetime.date.today()

def create_test_inventory_models(cls):
    cls.supplier = models.Supplier.objects.create(
            name='Test Name',
            contact_person='Test Contact Person',
            physical_address='Test Address',
            telephone='1234325345',
            email='test@mail.com',
            website = 'test.site',
            account = cls.account_c
            )

    cls.unit = models.UnitOfMeasure.objects.create(
            name='Test Unit',
            description='Test description'
        )
    cls.category = models.Category.objects.create(
            name='Test Category',
            description='Test description'
        )

    cls.product = models.Product.objects.create(
            name='test name',
            unit=cls.unit,
            pricing_method=0, #KISS direct pricing
            direct_price=10,
            margin=0.5,
            unit_purchase_price=8,
            description='Test Description',
            supplier = cls.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = cls.category,
            sub_category = cls.category
        )
    cls.warehouse = models.WareHouse.objects.create(
        name='Test Location',
        address='Test Address'
    )
    cls.warehouse_item = models.WareHouseItem.objects.create(
        product = cls.product,
        quantity =10,
        warehouse = cls.warehouse
    )
    cls.order = models.Order.objects.create(
            expected_receipt_date = TODAY,
            issue_date = TODAY,
            supplier=cls.supplier,
            bill_to = 'Test Bill to',
            ship_to = cls.warehouse,
            tracking_number = '34234',
            notes = 'Test Note',
            status = 'draft'
        )
    cls.order_item = models.OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=10
        )
    cls.stock_receipt = models.StockReceipt.objects.create(
            order = cls.order,
            receive_date = TODAY,
            note = 'Test Note',
            fully_received=True,
        )


class ModelTests(TestCase):
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        super(ModelTests, cls).setUpTestData()
        create_account_models(cls)
        create_test_inventory_models(cls)

    def test_create_supplier(self):
        sup = models.Supplier.objects.create(
            name='Other Test Name',
            contact_person='Test Contact Person',
            physical_address='Test Address',
            telephone='1234325345',
            email='test@mail.com',
            website = 'test.site',
            account = self.account_c
        )
        self.assertIsInstance(sup, models.Supplier)

    def test_create_product(self):
        product = models.Product.objects.create(
            name='other test name',
            unit=self.unit,
            pricing_method=1,
            direct_price=10,
            margin=0.25,
            unit_purchase_price=8,
            description='Test Description',
            supplier = self.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = self.category,
            sub_category = self.category    
        ) 
        self.assertIsInstance(product, models.Product)
        #and associated functions

    def test_create_order(self):
        ord = models.Order.objects.create(
            expected_receipt_date = TODAY,
            issue_date = TODAY,
            type_of_order=1,
            supplier=self.supplier,
            bill_to = 'Test Bill to',
            ship_to = self.warehouse,
            tracking_number = '34234',
            notes = 'Test Note',
            status = 'submitted'    
        )
        models.OrderItem.objects.create(
            order=ord,
            product=self.product,
            quantity=1,
        )
        self.assertIsInstance(ord, models.Order)
        #NB No transactions are created as yet

    def test_create_order_item(self):
        ord_item = models.OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=10,
            order_price=10
        )
        self.assertIsInstance(ord_item, models.OrderItem)

    def test_create_unit(self):
        unit = models.UnitOfMeasure.objects.create(
            name='Test Unit',
            description='Test description'
        )   
        self.assertIsInstance(unit, models.UnitOfMeasure)

    def test_create_stock_receipt(self):
        src = models.StockReceipt.objects.create(
            order = self.order,
            receive_date = TODAY,
            note = 'Test Note',
            fully_received=True,
        )
        self.assertIsInstance(src, models.StockReceipt)

    def test_create_category(self):
        cat = models.Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.assertIsInstance(cat, models.Category)

    def test_item_sales_to_date(self):
        #measure the number of items sold in entire history
        pass

    def test_item_stock_value(self):
        #needs a much more complex test!
        self.assertEqual(int(self.product.stock_value), 100)

    '''
    def test_item_increment_and_decrement(self):
        self.assertEqual(self.warehouse_item.increment(10), 20)
        self.assertEqual(self.item.decrement(10), 10)
    '''

    def test_order_total(self):
        #10 items @ $8 
        self.assertEqual(self.order.total, 80)

    def test_order_fully_received(self):
        self.assertFalse(self.order.fully_received)

    def test_order_percent_received(self):
        self.assertEqual(self.order.percent_received, 0)

    def test_order_receive(self):
        self.order.receive()
        self.assertTrue(self.order.fully_received)

        #break down changes
        models.StockReceipt.objects.latest('pk').delete()
        for item in self.order.orderitem_set.all():
            item.received = 0
            item.save()

    def test_order_item_fully_received(self):
        self.order_item.received = 10
        self.assertTrue(self.order_item.fully_received)
        
        #roll back changes
        self.order_item.received = 0
        self.order_item.save()

    def test_order_item_receive(self):
        self.order_item.receive(10)
        self.assertTrue(self.order_item.fully_received)
        
        #roll back changes
        self.order_item.received = 0
        self.order_item.save()

    def test_order_item_subtotal(self):
        #10 items @ $8
        self.assertEqual(self.order_item.subtotal, 80)
        

class ViewTests(TestCase):
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client

    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)
        
        cls.PRODUCT_DATA = {
            'name' : 'Other Test Item',
            'unit' : cls.unit.pk,
            'margin' : 0.2,
            'markup' : 0.2,
            'direct_price' : 10,
            'pricing_method': 2,
            'unit_purchase_price' : 8,
            'description' : 'Test Description',
            'supplier' : cls.supplier.pk,
            'quantity' : 10,
            'minimum_order_level' : 0,
            'maximum_stock_level' : 20,
            'category' : cls.category.pk,
            'sub_category' : cls.category.pk,
            
        }
        cls.SUPPLIER_DATA = {
            'name' : 'Other Test Name',
            'contact_person' : 'Test Contact Person',
            'physical_address' : 'Test Address',
            'telephone' : '1234325345',
            'email' : 'test@mail.com',
            'website' : 'test.site',
            'account': cls.account_c.pk
        }
        cls.ORDER_DATA = {
            'expected_receipt_date' : TODAY,
            'issue_date' : TODAY,
            'deferred_date' : TODAY,
            'supplier' : cls.supplier.pk,
            'bill_to' : 'Test Bill to',
            'ship_to' : cls.warehouse.pk,
            'type_of_order': 0,
            'tracking_number' : '34234',
            'notes' : 'Test Note',
            'status' : 'draft',
            'items[]': urllib.quote(json.dumps({
                'name': cls.product.pk,
                'quantity': 10,
                'order_price': 10
                }))
        }


    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_home_page(self):
        resp = self.client.get(reverse('inventory:home'))
        self.assertTrue(resp.status_code == 200)

    #MISC

    def test_get_unit_form(self):
        resp = self.client.get(reverse('inventory:unit-create'))
        self.assertTrue(resp.status_code == 200)

    def test_get_category_form(self):
        resp = self.client.get(reverse('inventory:category-create'))
        self.assertTrue(resp.status_code == 200)

    #SUPPLIER

    def test_get_supplier_create(self):
        resp = self.client.get(reverse('inventory:supplier-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_supplier_create(self):
        resp = self.client.post(reverse('inventory:supplier-create'),
            data=self.SUPPLIER_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_supplier_list(self):
        resp = self.client.get(reverse('inventory:supplier-list'))
        self.assertTrue(resp.status_code == 200)

    def test_get_supplier_update(self):
        resp = self.client.get(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.supplier.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_supplier_update(self):
        resp = self.client.post(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.supplier.pk
            }), data=self.SUPPLIER_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_supplier_delete(self):
        resp = self.client.get(reverse('inventory:supplier-delete',
            kwargs={
                'pk': self.supplier.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_supplier_delete(self):
        resp = self.client.post(reverse('inventory:supplier-delete',
            kwargs={
                'pk': models.Supplier.objects.latest('pk').pk
            }))
        self.assertTrue(resp.status_code == 302)

    #ITEM

    def test_get_product_form(self):
        resp = self.client.get(reverse('inventory:product-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_product_form(self):
        resp = self.client.post(reverse('inventory:product-create'),
            data=self.PRODUCT_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_product_list(self):
        resp = self.client.get(reverse('inventory:product-list'))
        self.assertTrue(resp.status_code == 200)

    def test_get_product_update_form(self):
        resp = self.client.get(reverse('inventory:product-update',
            kwargs={
                'pk': self.product.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_product_update_form(self):
        resp = self.client.post(reverse('inventory:product-update',
            kwargs={
                'pk': self.product.pk
            }), data=self.PRODUCT_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_product_delete_form(self):
        resp = self.client.get(reverse('inventory:product-delete',
            kwargs={
                'pk': self.product.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_product_delete_form(self):
        resp = self.client.post(reverse('inventory:product-delete',
            kwargs={
                'pk': models.Product.objects.latest('pk').pk
            }))
        self.assertTrue(resp.status_code == 302)

    def test_get_product_detail(self):
        resp = self.client.get(reverse('inventory:product-detail',
            kwargs={
                'pk': self.product.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_get_quick_product_form(self):
        resp = self.client.get(reverse('inventory:quick-product'))
        self.assertTrue(resp.status_code == 200)

    #ORDER

    def test_get_order_form(self):
        resp = self.client.get(reverse('inventory:order-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_order_form(self):
        resp = self.client.post(reverse('inventory:order-create'), 
        data=self.ORDER_DATA)
        self.assertTrue(resp.status_code == 302)
        #tests the created transaction
        self.assertEqual(Account.objects.get(pk=1004).balance, 100)

    def test_get_order_list(self):
        resp = self.client.get(reverse('inventory:order-list'))
        self.assertTrue(resp.status_code == 200)

    def test_get_order_update_form(self):
        resp = self.client.get(reverse('inventory:order-update',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_order_update_form(self):
        resp = self.client.post(reverse('inventory:order-update',
            kwargs={
                'pk': self.order.pk
            }), data=self.ORDER_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_order_delete_form(self):
        resp = self.client.get(reverse('inventory:order-delete',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_order_delete_form(self):
        resp = self.client.get(reverse('inventory:order-delete',
            kwargs={
                'pk': models.Order.objects.latest('pk').pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_get_order_detail(self):
        resp = self.client.get(reverse('inventory:order-detail',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_receive_from_order(self):
        resp = self.client.get(reverse('inventory:receive-from-order',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertTrue(resp.status_code == 302)

    def test_get_stock_receipt_form(self):
        resp = self.client.get(reverse('inventory:stock-receipt-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_stock_receipt_form(self):
        inv_b4 = Account.objects.get(pk=1004).balance
        resp = self.client.post(reverse('inventory:stock-receipt-create'),
            data={
                'order': self.order.pk,
                'receive_date': TODAY,
                'note': 'test note',
                'received-items': urllib.quote(json.dumps({
                    'item-' + str(self.order_item.pk) : 2
                }))
            })
        self.assertTrue(resp.status_code == 302)
        #test the created transaction
        self.assertEqual(Account.objects.get(pk=1004).balance, inv_b4 + 16 )

    def test_get_config_view(self):
        resp = self.client.get(reverse('inventory:config'))
        self.assertTrue(resp.status_code == 200)

    def test_post_config_view(self):
        resp = self.client.post(reverse('inventory:config'),
            data={
                'inventory_valuation': 'fifo'
            })
        self.assertTrue(resp.status_code == 302)