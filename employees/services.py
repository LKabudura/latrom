from employees import models 
import datetime
import planner
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from common_data.utilities import AutomatedServiceMixin

class PayrollException(Exception):
    pass

class AutomatedPayrollService(AutomatedServiceMixin):
    service_name = 'employees'

    def __init__(self):
        self.settings = models.EmployeesSettings.objects.first()
        self.TODAY  = datetime.date.today()

    def _run(self):
        print("running payroll service")
        schedule = models.PayrollSchedule.objects.first()

        if any([self.TODAY.day == i.date \
                for i in schedule.payrolldate_set.all()]) and \
                    self.settings.last_payroll_date != self.TODAY:
            
            payroll_date = models.PayrollDate.objects.get(date=self.TODAY.day)
            payroll_id = self.settings.payroll_counter + 1
            self.settings.last_payroll_date = self.TODAY
            self.settings.payroll_counter = payroll_id
            self.settings.save()

            employees = payroll_date.all_employees

            for employee in employees:
                if employee.uses_timesheet:
                    sheet = self.get_employee_timesheet(employee)
                    if sheet and sheet.complete:
                        models.Payslip.objects.create(
                            start_period = self.get_start_date(employee),
                            end_period = self.TODAY,
                            employee = employee,
                            normal_hours = sheet.normal_hours.seconds / 3600,
                            overtime_one_hours = sheet.overtime.seconds / 3600,
                            overtime_two_hours = 0,
                            pay_roll_id = payroll_id
                        )
                    
                    else:
                        planner.models.Notification.objects.create(
                            user = self.settings.payroll_officer.user,
                            title = 'Payroll',
                            message = """This notification message was generated by the payroll system.  
                            The employee {} does not have a complete timesheet and therefore the payslip generation
                            process could not complete. Please complete the timesheet then create a manual payslip from the 
                            recorded data.""",
                            action = reverse_lazy('employees:timesheet-update', kwargs={'pk': employee.pk})
                        )

                else:
                    models.Payslip.objects.create(
                        start_period = self.get_start_date(employee),
                        end_period = self.TODAY,
                        employee = employee,
                        normal_hours = 0,
                        overtime_one_hours = 0,
                        overtime_two_hours = 0,
                        pay_roll_id = payroll_id
                    )
            
            self.adjust_leave_days()

    def get_employee_timesheet(self, employee):
        sheet_filters = Q(
            Q(employee=employee) &
            Q(month=self.TODAY.month) &
            Q(year=self.TODAY.year)
        )
        if models.EmployeeTimeSheet.objects.filter(sheet_filters).exists():
            return models.EmployeeTimeSheet.objects.get(sheet_filters)

        return None

    def get_start_date(self, employee):
        mapping = {
            0: datetime.timedelta(days=7),
            1: relativedelta(weeks=2),
            2: relativedelta(months=1)
        }
        return self.TODAY - mapping[employee.pay_grade.pay_frequency]


    def adjust_leave_days(self):
        for employee in models.Employee.objects.filter(pay_grade__isnull=False):
            if employee.last_leave_day_increment is None  or \
                    (self.TODAY -  employee.last_leave_day_increment).days > 30:
                employee.increment_leave_days(
                    employee.pay_grade.monthly_leave_days)
                
        for leave in models.Leave.objects.filter(
                Q(recorded=False) &
                Q(status=1)):
        
            if leave.start_date <= self.TODAY:
                leave.recorded = True
                leave.save()
                leave.employee.deduct_leave_days(leave.duration)