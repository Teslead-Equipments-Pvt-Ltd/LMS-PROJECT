from django.shortcuts import render
from LMSAPP.services.project_service import get_all_projects_service
from LMSAPP.services.task_service import get_all_tasks_service

def dashboard_page(request):
    projects = get_all_projects_service()
    tasks = get_all_tasks_service()

    # Calculate Project Metrics
    total_projects = len(projects)
    project_not_worked = sum(1 for p in projects if p.get('status') == 'Not Worked')
    project_in_progress = sum(1 for p in projects if p.get('status') == 'In Progress')
    project_pending = sum(1 for p in projects if p.get('status') == 'Pending')
    project_completed = sum(1 for p in projects if p.get('status') == 'Completed')

    # Calculate Task Metrics
    total_tasks = len(tasks)
    task_not_worked = sum(1 for t in tasks if t.get('status') == 'Not Worked')
    task_in_progress = sum(1 for t in tasks if t.get('status') == 'In Progress')
    task_pending = sum(1 for t in tasks if t.get('status') == 'Pending')
    task_completed = sum(1 for t in tasks if t.get('status') == 'Completed')

    context = {
        'total_projects': total_projects,
        'project_not_worked': project_not_worked,
        'project_in_progress': project_in_progress,
        'project_pending': project_pending,
        'project_completed': project_completed,
        'total_tasks': total_tasks,
        'task_not_worked': task_not_worked,
        'task_in_progress': task_in_progress,
        'task_pending': task_pending,
        'task_completed': task_completed,
        'recent_projects': projects[-5:],
        'recent_tasks': tasks[-5:]
    }

    return render(request, 'dashboard.html', context)