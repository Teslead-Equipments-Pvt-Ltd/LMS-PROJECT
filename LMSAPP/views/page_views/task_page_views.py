from django.shortcuts import render
from LMSAPP.services.task_service import get_all_tasks_service
from LMSAPP.services.project_service import get_all_projects_service
from LMSAPP.services.employee_service import get_all_employees

def task_page(request):
    employee=get_all_employees()
    tasks = get_all_tasks_service()
    projects = get_all_projects_service()
    return render(request, "task.html", {"tasks": tasks, "projects": projects,"employee":employee})
