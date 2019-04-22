import os
from django.views.generic import TemplateView
from services.models import ServiceWorkOrder, Service
from django.db.models import Q

from .service import *
from .procedure import *
from .personnel import *
from .work_orders import *
from .requisitions import *
from .category import *
from .reports import *

class Dashboard( TemplateView):
    template_name = os.path.join('services', 'dashboard.html')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        context['services'] = Service.objects.filter(is_listed=True).count()
        context['wo_open'] = ServiceWorkOrder.objects.filter(Q(status="request") | Q(status="in-progress")).count()
        context['wo_closed'] = ServiceWorkOrder.objects.filter(Q(status="completed")).count()
        today = datetime.date.today()
        start = today - datetime.timedelta(days = 30)
        ServicePersonUtilizationReport.common_context(context, start, today)

        return context