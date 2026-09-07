from django.shortcuts import render
from LMSAPP.services.project_service import get_all_projects_service
from LMSAPP.services.task_service import get_all_tasks_service

def dashboard_page(request):
    projects = get_all_projects_service()
    tasks = get_all_tasks_service()

    return render(request, 'dashboard.html')