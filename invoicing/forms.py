
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (HTML, 
                                Fieldset, 
                                Layout,
                                Row,
                                Column, 
                                Submit)
from django import forms
from django.forms.widgets import HiddenInput, MultipleHiddenInput

from accounting.models import Account, Journal,Tax
from common_data.forms import BootstrapMixin, PeriodReportForm
from common_data.models import Organization
from . import models
from django.forms import ValidationError

class SalesConfigForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.SalesConfig
        fields = "__all__"

        widgets = {
            'default_invoice_comments':forms.Textarea(attrs={'rows':4, 'cols':15}),
            'default_credit_note_comments':forms.Textarea(attrs={'rows':4, 'cols':15}),
            'default_quotation_comments':forms.Textarea(attrs={'rows':4, 'cols':15}),
            'default_terms':forms.Textarea(attrs={'rows':4, 'cols':15}),            
        }

    def __init__(self, *args, **kwargs):
        super(SalesConfigForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
            Tab('Document Fields', 
                'default_invoice_comments',
                'default_credit_note_comments',
                'default_quotation_comments',
                'default_terms',
                ),
            Tab('Page Layout',
                'sales_tax',
                'include_tax_in_invoice',
                'next_invoice_number',
                'next_quotation_number',
                'include_units_in_sales_invoice',
                'include_shipping_address',
                ),
            Tab('Invoice Types',
                'use_sales_invoice',
                'use_combined_invoice',
                'use_bill_invoice',
                'use_service_invoice',
                )
        ))

        self.helper.add_input(Submit('submit', "Submit"))
        
class CustomerForm(BootstrapMixin, forms.Form):
    customer_type = forms.ChoiceField(widget=forms.RadioSelect, choices=[
        ('individual', 'Individual'),
        ('organization', 'Organization')
        ])
    name=forms.CharField()
    address=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':10}),
                            required=False)
    billing_address=forms.CharField(widget=forms.Textarea, 
                            required=False)
    banking_details=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':10}),
                            required=False)
    email= forms.EmailField(required=False)
    organization=forms.ModelChoiceField(Organization.objects.all(), 
        required=False)
    phone_1=forms.CharField(required=False)
    phone_2=forms.CharField(required=False)
    image=forms.ImageField(required=False)
    website=forms.CharField(required=False)
    business_partner_number=forms.CharField(required=False)

    other_details=forms.CharField(widget=forms.Textarea, required=False)

    


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout= Layout(
            TabHolder(
                Tab('details',
                    Row(
                        Column('name', css_class='form-group col-6'),
                        Column('organization', css_class='form-group col-6'),
                    ),
                    Row(
                        Column('address', css_class='form-group col-6'),
                        Column('banking_details', css_class='form-group col-6'),
                    ),
                    Row(
                        Column(
                            'phone_1',
                            'phone_2',
                            'email', css_class='form group col-6'
                        ),
                        Column('billing_address', css_class='form group col-6')
                    ),                    
                ),
                Tab('other',
                    'website',
                    'image',
                    'other_details',
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        if cleaned_data['customer_type'] == "individual":
            if " " not in cleaned_data['name']:
                raise ValidationError('The customer name must have both a first and last name separated by a space.')

        return cleaned_data


class SalesRepForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = 'active',
        model = models.SalesRepresentative

class InvoiceCreateMixin(forms.Form):
    apply_payment = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['status'] != 'invoice' and \
                cleaned_data['apply_payment']:
            raise forms.ValidationError('Save the document as invoice if you want to apply a payment')

        return cleaned_data


class CreditNoteForm( forms.ModelForm, BootstrapMixin):
    invoice = forms.ModelChoiceField(models.Invoice.objects.all(), widget=forms.HiddenInput)
    class Meta:
        fields = '__all__'
        model = models.CreditNote

#######################################################
#               Report Forms                          #
#######################################################
# report types
# customer statement
# invoice aging report
# invoice summary
# past due invoices
# outstanding invoices
# payment summary
# sales by item 

class CustomerStatementReportForm(PeriodReportForm):
    customer = forms.ModelChoiceField(models.Customer.objects.all())

class SalesReportForm(PeriodReportForm):
    '''method = forms.ChoiceField(widget=forms.RadioSelect, choices=[("invoice", "Invoice Count"), ("amount", "Sales Value")])'''
    pass


class InvoiceForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        fields = ["status", 'customer', 'purchase_order_number', 'ship_from', 'date', 'due', 'salesperson', 'terms', 'comments']
        model = models.Invoice

class InvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        fields = ["status", 'customer', 'purchase_order_number', 'ship_from', 'date', 'due', 'salesperson',  'terms', 'comments']
        model = models.Invoice

class QuotationForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    quotation_date = forms.DateField(required=True)
    quotation_valid = forms.DateField(required=True)

    class Meta:
        fields = ["status", 'customer', 'quotation_date', 'quotation_valid', 'salesperson', 'terms', 'comments']
        model = models.Invoice

class InvoicePaymentForm(forms.ModelForm, BootstrapMixin):
    invoice = forms.ModelChoiceField(
        models.Invoice.objects.all(), widget=forms.HiddenInput
        )
    
    class Meta:
        exclude = [ 'active']
        model = models.Payment