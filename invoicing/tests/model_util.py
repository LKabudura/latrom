from invoicing.models import *
from common_data.tests.model_util import CommonModelCreator
from inventory.tests.model_util import InventoryModelCreator

class InvoicingModelCreator():
    def __init__(self, klass):
        self.cls = klass

    def create_all(self):
        self.create_credit_note()
        self.create_credit_note_line()
        self.create_customer_ind()
        self.create_customer_org()
        self.create_invoice()
        self.create_quotation()
        self.create_payment()
        self.create_product_line()
        self.create_product_line_component()
        self.create_service_line()
        self.create_service_line_component()

    def create_customer_ind(self):
        if not hasattr(self.cls,' individual'):
            cmc = CommonModelCreator(self.cls)
            cmc.create_individual()

        self.cls.customer_ind = Customer.objects.create(
            individual= self.cls.individual
        )

        return self.cls.customer_ind

    def create_customer_org(self):
        if not hasattr(self.cls,' organization'):
            cmc = CommonModelCreator(self.cls)
            cmc.create_organization()

        if hasattr(self.cls, 'customer_org'):
            return self.cls.customer_org

        self.cls.customer_org = Customer.objects.create(
            organization= self.cls.organization
        )

        return self.cls.customer_org

    def create_invoice(self):
        if hasattr(self.cls, 'invoice') and self.cls.invoice is not None:
            return self.cls.invoice

        if not hasattr(self.cls, 'customer_org'):
            self.create_customer_org()

        if not hasattr(self.cls, 'warehouse'):
            imc = InventoryModelCreator(self.cls)
            imc.create_warehouse()


        self.cls.invoice = Invoice.objects.create(
            draft=False,
            status='invoice',
            customer=self.cls.customer_org,
            ship_from=self.cls.warehouse,
            salesperson='person'
            )

        return self.cls.invoice 

    def create_quotation(self):
        if hasattr(self.cls, 'quotation') and self.cls.invoice is not None:
            return self.cls.invoice

        if not hasattr(self.cls, 'customer_org'):
            self.create_customer_org()

        if not hasattr(self.cls, 'warehouse'):
            imc = InventoryModelCreator(self.cls)
            imc.create_warehouse()


        self.cls.quotation = Invoice.objects.create(
            draft=False,
            status='quotation',
            quotation_date=datetime.date.today(),
            quotation_valid=datetime.date.today(),
            customer=self.cls.customer_org,
            ship_from=self.cls.warehouse,
            salesperson='self.cls.sales_representative'
            )

        return self.cls.quotation

    def create_product_line_component(self):
        if not hasattr(self.cls, 'product'):
            imc = InventoryModelCreator(self.cls)
            imc.create_product()
        
        self.cls.product_line_component = ProductLineComponent.objects.create(
            product=self.cls.product,
            quantity=1,
        )

        self.cls.product_line_component

    def create_service_line_component(self):
        self.cls.service_line_component = ServiceLineComponent.objects.create(
            service='service',
            hours=0,
            flat_fee=100,
            hourly_rate=10
        )

        return self.cls.service_line_component



    def create_product_line(self):
        if hasattr(self.cls, 'product_line'):
            return self.cls.product_line
            
        if not hasattr(self.cls, 'invoice'):
            self.create_invoice()
        if not hasattr(self.cls, 'product_line_component'):
            self.create_product_line_component()

        self.cls.product_line = InvoiceLine.objects.create(
            invoice=self.cls.invoice,
            product=self.cls.product_line_component,
            line_type=1
        )

        return self.cls.product_line


    def create_service_line(self):
        if hasattr(self.cls, 'service_line'):
            return self.cls.service_line 

        if not hasattr(self.cls, 'invoice'):
            self.create_invoice()
        if not hasattr(self.cls, 'service_line_component'):
            self.create_service_line_component()

        self.cls.service_line = InvoiceLine.objects.create(
            invoice=self.cls.invoice,
            service=self.cls.service_line_component,
            line_type=2
        )

        return self.cls.service_line


    def create_payment(self):
        if not hasattr(self.cls, 'invoice'):
            self.create_invoice()

        self.cls.payment = Payment.objects.create(
            invoice=self.cls.invoice,
            amount=10,
            date=datetime.date.today(),
            sales_rep='self.cls.sales_representative'
        )

    def create_credit_note(self):
        if not hasattr(self.cls, 'invoice'):
            self.create_invoice()

        self.cls.credit_note = CreditNote.objects.create(
            date=datetime.date.today(),
            invoice=self.cls.invoice,
            comments="Test comment"
        )
        return self.cls.credit_note

    def create_credit_note_line(self):
        if not hasattr(self.cls, 'credit_note'):
            self.create_credit_note()
        if not hasattr(self.cls, 'product_line'):
            self.create_product_line()

        self.cls.credit_note_line = CreditNoteLine.objects.create(
            note=self.cls.credit_note,
            line= self.cls.product_line,
            quantity=1
        )

        return self.cls.credit_note_line

   