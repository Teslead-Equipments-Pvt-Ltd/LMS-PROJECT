from django.shortcuts import render
from LMSAPP.services.employee_service import get_all_employees

def employee_page(request):

    employees = get_all_employees()

    return render(request, "employee.html", {"employees": employees})  