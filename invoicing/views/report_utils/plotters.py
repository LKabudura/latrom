import datetime
from invoicing.models.invoice import Invoice, InvoiceLine
from dateutil import relativedelta
from django.db.models import Q

import pygal

def plot_sales(start, end, filters=Q()):
    y = None
    delta = None

    date_range = (end - start).days
    if abs(date_range) > 70:
        delta = 30
        

    elif abs(date_range) > 20:
        delta = 7
    
    else:
        delta = 1

    y_query = get_queryset_list(Invoice, start, end, delta, filters=Q( 
            Q(status='invoice') | 
            Q(status='paid') | 
            Q(status='paid-partially')) & 
            Q(draft=False) & filters)

    y = [get_sales_totals(q) for q in y_query]


    chart = pygal.Bar(x_title="Periods", x_label_rotation=15)
    chart.title = 'Sales Report'
    chart.x_labels = pygal_date_formatter(start, end)
    chart.add('Sales($)', y)
    

    return chart.render(is_unicode=True)

def plot_lines(start, end, filters=Q()):
    #set deltas
    y = None
    delta = None

    date_range = (end - start).days
    if abs(date_range) > 70:
        delta = 30
        

    elif abs(date_range) > 20:
        delta = 7
    
    else:

        delta = 1

    y_query = get_line_queryset_list(InvoiceLine, start, end, delta, filters=filters)
    

    y = [get_line_totals(q) for q in y_query]


    chart = pygal.Bar(x_title="Periods", x_label_rotation=15)
    chart.title = 'Sales Report'
    chart.x_labels = pygal_date_formatter(start, end)
    chart.add('Sales($)', y)
    

    return chart.render(is_unicode=True)

def get_sales_totals(queryset):
    total = 0
    for invoice in queryset:
        total += invoice.subtotal# no tax

    return total

def get_line_totals(queryset):
    total = 0
    for invoiceline in queryset:
        total += invoiceline.subtotal# no tax

    return total

def get_queryset_list(obj, start, end, delta, filters=Q()):
    curr_date = start
    prev_date = start
    query_list = []

    while curr_date < end:
        curr_date  = curr_date + datetime.timedelta(days=delta)
        query_list.append(obj.objects.filter(
            Q(date__gt=prev_date) & 
            Q(date__lte=curr_date) & filters))
        prev_date = curr_date


    return query_list

def get_line_queryset_list(obj, start, end, delta, filters=Q()):
    curr_date = start
    prev_date = start
    query_list = []
    while curr_date < end:
        curr_date  = curr_date + datetime.timedelta(days=delta)
        query_list.append(obj.objects.filter(
            Q(invoice__date__gt=prev_date) &
                Q(invoice__date__lte=curr_date) &
                Q(invoice__draft=False) &
                Q(
                    Q(invoice__status='invoice') | 
                    Q(invoice__status='paid') | 
                    Q(invoice__status='paid-partially')
                ) & filters))
        prev_date = curr_date


    return query_list

def pygal_date_formatter(start, end):
    date_range = abs((end- start).days)

    if date_range > 70:
        #months 
        delta = relativedelta.relativedelta(months=1)
        formatter = "%B  %Y"
    elif date_range > 10:
        delta = datetime.timedelta(days=7)
        formatter = "%d/%m/%y"
    else:
        delta = datetime.timedelta(days=1)
        formatter ="%d %B '%y"

    curr_date = start
    prev_date = None
    dates = []

    while curr_date < end:
        prev_date = curr_date
        curr_date = curr_date + delta
        dates.append(prev_date)

    if curr_date != end:
        dates.append(end)

    return [d.strftime(formatter) for d in dates]

