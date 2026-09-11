from django.shortcuts import render
from LMSAPP.services.project_service import get_all_projects_service
from LMSAPP.services.task_service import get_all_tasks_service


def dashboard_page(request):

    projects = get_all_projects_service()
    tasks = get_all_tasks_service()

    # Project counts
    total_projects = len(projects)

    project_not_worked = 0
    project_in_progress = 0
    project_on_hold = 0
    project_completed = 0

    for project in projects:
        if project.get('status') == 'Not Worked':
            project_not_worked= project_not_worked + 1
        elif project.get('status') == 'In Progress':
            project_in_progress = project_in_progress + 1
        elif project.get('status') == 'On Hold':
            project_on_hold = project_on_hold + 1
        elif project.get('status') == 'Completed':
            project_completed = project_completed + 1

    # Task counts
    total_tasks = len(tasks)

    task_not_worked = 0
    task_in_progress = 0
    task_on_hold = 0
    task_completed = 0

    for task in tasks:
        if task.get('status') == 'Not Worked':
            task_not_worked = task_not_worked + 1
        elif task.get('status') == 'In Progress':
            task_in_progress = task_in_progress + 1
        elif task.get('status') == 'On Hold':
            task_on_hold = task_on_hold + 1
        elif task.get('status') == 'Completed':
            task_completed = task_completed + 1

    return render(request, 'dashboard.html', {
        'total_projects': total_projects,
        'project_not_worked': project_not_worked,
        'project_in_progress': project_in_progress,
        'project_on_hold': project_on_hold,
        'project_completed': project_completed,

        'total_tasks': total_tasks,
        'task_not_worked': task_not_worked,
        'task_in_progress': task_in_progress,
        'task_on_hold': task_on_hold,
        'task_completed': task_completed,
    })