from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Payslip
from django.http import HttpResponseRedirect
from django.contrib import messages
import re
from django.core.exceptions import ValidationError

# Create your views here.
def view_employees(request):
    employee_objects = Employee.objects.all()
    return render(request, 'payroll_app/employee_list.html', {'employees':employee_objects})

def create_employee(request):
    if(request.method=="POST"):
        reqid = request.POST.get("id-input")
        if not reqid or not reqid.isdigit():
            messages.error(request, 'ID cannot be empty and should contain numbers only. Please try again.')
            return redirect('create_employee')
        if Employee.objects.filter(id=reqid).exists():
            messages.error(request, 'ID already exists. Please try again.')
            return redirect('create_employee')
        else:
            name = request.POST.get("name-input")
            if not name or not name.replace(" ", "").isalnum():
                messages.error(request, 'Name cannot be empty, contain special characters, or numbers. Please try again.')
                return redirect('create_employee')
            print("Processing request.")
            reqallowance = request.POST.get("allowance-input")
            if reqallowance and not reqallowance.isdigit():
                messages.error(request, 'Allowance should contain numbers only. Please try again.')
                return redirect('create_employee')
            try:
                rate = float(request.POST.get("rate-input"))
                if rate <= 0:
                    messages.error(request, 'Rate should be greater than 0. Please try again.')
                    return redirect('create_employee')
            except ValueError:
                messages.error(request, 'Rate should be a valid number. Please try again.')
                return redirect('create_employee')

            try:
                Employee.objects.create(name=name, id_number=reqid, rate=rate, allowance=reqallowance or 0, overtime_pay=0)
                messages.success(request,"Account Created!")
                return redirect('create_employee')
            except ValidationError as e:
                messages.error(request, e.message)
    return render(request, 'payroll_app/create_employee.html')

def view_payslip(request, pk):
    p = get_object_or_404(Payslip, pk=pk)
    grosspay = p.addGrossPay()
    return render(request, 'payroll_app/view_payslip.html', {'p': p, 'grosspay' : grosspay,'base_pay': p.id_number.rate/2})

def delete_employee(request, employee_id):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, id=employee_id)
        employee.delete()
        messages.success(request, "Employee deleted successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        pass


def create_payslip(request):
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        reqmonth = request.POST.get('month')
        reqyear = request.POST.get('year')
        cycle = request.POST.get('cycle')

        errors = []
        if not recipient or recipient == 'Choose...':
            errors.append('Please select a valid recipient.')
        if not reqmonth or reqmonth == 'Choose...':
            errors.append('Please select a valid month.')
        if not reqyear:
            errors.append('Year field cannot be empty.')
        elif not reqyear.isdigit() or len(reqyear) != 4:
            errors.append('Year should be a proper 4-digit year.')
        if not cycle or cycle == 'Choose...':
            errors.append('Please select a valid pay cycle.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('create_payslip')

        if recipient == 'all':
            employees = Employee.objects.all()
            for employee in employees:
                if cycle == '1':
                    tax_d = ((employee.rate / 2) + employee.allowance + employee.overtime_pay - 100) * 0.2
                    tax_h = 0
                    reqtotal_pay = ((employee.rate / 2) + employee.allowance + employee.overtime_pay - 100) - tax_d
                    reqdate_range = "1-15"
                    reqsss = 0 
                    philhealth = 0
                    total_deduc = 100 + tax_d
                elif cycle == '2':
                    philhealth = employee.rate * 0.04
                    reqsss = employee.rate * 0.045
                    tax_h = ((employee.rate / 2) + employee.allowance + employee.overtime_pay - philhealth - reqsss) * 0.2
                    tax_d = 0
                    reqtotal_pay = ((employee.rate / 2) + employee.allowance + employee.overtime_pay - philhealth - reqsss) - tax_h
                    reqdate_range = "16-30"
                    total_deduc = philhealth + reqsss + tax_h

                Payslip.objects.create(
                    id_number=employee,
                    month=reqmonth,
                    date_range=reqdate_range,
                    year=reqyear,
                    pay_cycle=cycle,
                    rate=employee.rate,
                    earnings_allowance=employee.allowance,
                    deductions_tax=tax_d,
                    deductions_health=tax_h,
                    pag_ibig=100,
                    sss=reqsss,
                    overtime=employee.overtime_pay,
                    total_pay=reqtotal_pay,
                    philhealth=philhealth,
                    total_deduc=total_deduc
                )
                employee.overtime_pay = 0
                employee.save()
        else:
            employee = Employee.objects.get(id=recipient)
            if cycle == '1':
                tax_d = ((employee.rate / 2) + employee.allowance + employee.overtime_pay - 100) * 0.2
                tax_h = 0
                reqtotal_pay = ((employee.rate / 2) + employee.allowance + employee.overtime_pay - 100) - tax_d
                reqdate_range = "1-15"
                reqsss = 0 
                philhealth = 0
                total_deduc = 100 + tax_d
            elif cycle == '2':
                philhealth = employee.rate * 0.04
                reqsss = employee.rate * 0.045
                tax_h = ((employee.rate / 2) + employee.allowance + employee.overtime_pay - philhealth - reqsss) * 0.2
                tax_d = 0
                reqtotal_pay = ((employee.rate / 2) + employee.allowance + employee.overtime_pay - philhealth - reqsss) - tax_h
                reqdate_range = "16-30"
                total_deduc = philhealth + reqsss + tax_h

            Payslip.objects.create(
                id_number=employee,
                month=reqmonth,
                date_range=reqdate_range,
                year=reqyear,
                pay_cycle=cycle,
                rate=employee.rate,
                earnings_allowance=employee.allowance,
                deductions_tax=tax_d,
                deductions_health=tax_h,
                pag_ibig=100,
                sss=reqsss,
                overtime=employee.overtime_pay,
                total_pay=reqtotal_pay,
                philhealth=philhealth,
                total_deduc=total_deduc
            )
            employee.overtime_pay = 0
            employee.save()

        return redirect('create_payslip')
    else:
        employees = Employee.objects.all()
        payslips = Payslip.objects.all()
        return render(request, 'payroll_app/create_payslip.html', {'employees': employees, 'payslips': payslips})


def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        id_number = request.POST.get('id_number')
        rate = request.POST.get('rate')
        allowance = request.POST.get('allowance')

        if not name or not name.replace(" ", "").isalnum():
            messages.error(request, 'Name cannot be empty, contain special characters, or numbers. Please try again.')
            return redirect('update_employee', employee_id=employee_id)
        
        if id_number != str(employee.id_number):
            messages.error(request, 'Updating the ID number is not allowed.')
            return redirect('update_employee', employee_id=employee_id)

        try:
            rate = float(rate)
            if rate <= 0:
                messages.error(request, 'Rate should be greater than 0. Please try again.')
                return redirect('update_employee', employee_id=employee_id)
        except ValueError:
            messages.error(request, 'Rate should be a valid number. Please try again.')
            return redirect('update_employee', employee_id=employee_id)

        employee.name = name
        employee.rate = rate
        employee.allowance = allowance
        employee.save()
        messages.success(request, 'Employee updated successfully.')
        return redirect('update_employee', employee_id=employee_id)  

    return render(request, 'payroll_app/update_employee.html', {'employee': employee})

def add_overtime(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        overtime_hours_str = request.POST.get('overtime_hours')
        if overtime_hours_str:
            try:
                overtime_hours = float(overtime_hours_str)
                if overtime_hours >= 0:  # Check if overtime hours is non-negative
                    employee = Employee.objects.get(pk=employee_id)
                    rate = float(employee.rate)
                    overtime_pay = (rate / 160) * 1.5 * overtime_hours  
                    employee.overtime_pay += overtime_pay
                    employee.save()
                else:
                    messages.error(request, 'Overtime hours should be a non-negative number.')
            except (ValueError, TypeError):
                messages.error(request, 'Overtime hours should be a valid number.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        
        
        
        
        
        