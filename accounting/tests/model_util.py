from accounting.models import *
import datetime

class AccountingModelCreator():
    def __init__(self, klass):
        self.cls = klass

    def create_accounts(self):
        self.cls.account_c = Account.objects.create(
            name= 'Model Test Credit Account',
            balance=100,
            type='asset',
            description='Some description'
        )
        self.cls.account_d = Account.objects.create(
            name= 'Model Test Debit Account',
            balance=100,
            type='liability',
            description='Some description'
        )

    def create_expense(self):
        self.cls.expense = Expense.objects.create(
            date=datetime.date.today(),
            description = 'Test Description',
            category=0,
            amount=100,
            billable=False,
            debit_account=self.cls.account_d)

    def create_tax(self):
        if hasattr(self.cls, 'tax'):
            return self.cls.tax
        
        self.cls.tax = Tax.objects.create(
            name="tax",
            rate=15
        )

        return self.cls.tax