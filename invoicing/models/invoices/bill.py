# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import itertools
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone

import inventory
from accounting.models import Account, Expense, Journal, JournalEntry, Tax
from common_data.models import Person, SingletonModel
from employees.models import Employee
from invoicing.models.payment import Payment
from services.models import Service

from .abstract import AbstractSale


class Bill(AbstractSale):
    '''Used to recover billable expenses'''
    
    customer_reference = models.CharField(max_length=255, blank=True)
    
    @property
    def billable_expenses(self):
        return self.customer.expense_set.filter(Q(billline__isnull=True))

    def add_line(self, expense_id):
        expense = Expense.objects.get(pk=expense_id)
        self.billline_set.create(
            expense=expense
        )
        
    @property
    def subtotal(self):
        return reduce(lambda x, y: x + y, 
            [e.expense.amount for e in self.billline_set.all()], 0)
    
    @property
    def total(self):
        # no tax on bills 
        return self.subtotal
    
    def create_entry(self):
        j = JournalEntry.objects.create(
            reference='INV' + str(self.pk),
            memo= 'Auto generated Entry from unpaid bill from customer.',
            date=self.date,
            journal =Journal.objects.get(pk=3)#Sales Journal
        )
        #check these accounts
        # the corresponding account for the expense incurred
        for line in self.billline_set.all():
            j.credit(line.expense.amount, line.expense.expense_account)
        j.debit(self.total, self.customer.account)#customer account

        if not self.on_credit:
            pmt = Payment.objects.create(
                payment_for=2,
                bill=self,
                amount=self.total,
                date=self.due,
                sales_rep=self.salesperson
            )
            pmt.create_entry()
        return j
            
class BillLine(models.Model):
    bill = models.ForeignKey('invoicing.Bill', on_delete=None)
    expense = models.ForeignKey('accounting.Expense', on_delete=None)
