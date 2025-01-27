from functools import reduce

from django.db import models
from decimal import Decimal as D

from django.shortcuts import reverse


class CreditNote(models.Model):
    """A document sent by a seller to a customer notifying them
    that a credit has been made  against goods returned
    by the buyer. Linked to invoices. Stores a list of products returned.
    
    properties
    -----------
    returned_products - returns a queryset of all returned products for an invoice
    returned_total - returns the numerical value of the products returned.
    
    methods
    -----------"""
    
    date = models.DateField()
    invoice = models.ForeignKey('invoicing.Invoice', 
            on_delete=models.SET_NULL, null=True)
    comments = models.TextField()#never allow blank comments


    def get_absolute_url(self):
        return reverse("invoicing:credit-note-detail", kwargs={"pk": self.pk})
    

    @property
    def returned_products(self):
        return self.creditnoteline_set.all()
        
    @property
    def returned_total(self):
        return sum([i.returned_value for i in self.returned_products])

    @property
    def tax_credit(self):
        return sum([(i.line.tax_) \
            for i in self.creditnoteline_set.all() if i.line and i.line.tax] ,0)
        
    @property
    def returned_total_with_tax(self):
        return D(self.returned_total) + D(self.tax_credit)

    @property
    def total(self):
        return self.returned_total_with_tax

    @property
    def subtotal(self):
        return self.returned_total

    @property
    def tax_amount(self):
        return self.tax_credit

   

#TODO test
class CreditNoteLine(models.Model):
    note = models.ForeignKey('invoicing.CreditNote', null=True, 
            on_delete=models.SET_NULL)
    line = models.ForeignKey('invoicing.InvoiceLine', null=True,
            on_delete=models.SET_NULL)
    quantity = models.FloatField()

    def __str__(self):
        return "{}".format((str(self.line)))

    @property
    def returned_value(self):
        '''Factors for line by line discount'''
        # support other kinds of objects
        if self.line and self.line.product:
            discount =  self.line.product.nominal_price * \
                (self.line.discount / D(100))
            discounted_price = self.line.product.nominal_price - discount
            return D(self.quantity) * discounted_price

        return 0.0