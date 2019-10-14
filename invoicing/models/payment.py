from django.db import models

from decimal import Decimal as D
from common_data.models import SoftDeletionModel

class Payment(SoftDeletionModel):
    '''Model represents payments made by credit customers only!
    These transactions are currently implemented to require full payment 
    of each invoice. Support for multiple payments for a single invoice
    may be considered as required by clients.
    Information stored include data about the invoice, the amount paid 
    and other notable comments
    
    methods
    ---------
    '''
    PAYMENT_METHODS = [("cash", "Cash" ),
                        ("transfer", "Transfer"),
                        ("debit card", "Debit Card"),
                        ("ecocash", "EcoCash")]
    invoice = models.ForeignKey("invoicing.Invoice", 
        on_delete=models.SET_NULL, 
        null=True)
    amount = models.DecimalField(max_digits=16,decimal_places=2)
    date = models.DateField()
    method = models.CharField(
        max_length=32, 
        choices=PAYMENT_METHODS,
        default='transfer')
    reference_number = models.AutoField(primary_key=True)
    sales_rep = models.CharField(max_length=64)
    comments = models.TextField(default="Thank you for your business")
    
    
    def __str__(self):
        return 'PMT' + str(self.pk)

    @property
    def due(self):
        return self.invoice.total - self.amount

    