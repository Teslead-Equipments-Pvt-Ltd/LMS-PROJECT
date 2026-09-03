from django.shortcuts import render
from LMSAPP.services.task_service import get_all_tasks_service
from LMSAPP.services.project_service import get_all_projects_service

def task_page(request):
    
    tasks = get_all_tasks_service()
    projects = get_all_projects_service()
    return render(request, "task.html", {"tasks": tasks, "projects": projects})
