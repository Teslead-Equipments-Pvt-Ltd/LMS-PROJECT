from django.shortcuts import render
from LMSAPP.services.task_service import get_all_tasks_service
from LMSAPP.services.project_service import get_all_projects_service
from LMSAPP.services.employee_service import get_all_employees,get_employee_tasks

def task_page(request):

    user_name=request.session.get('user_name')
    user_type=str(request.session.get('user_type','')).lower()
    # role=str(request.session.get('role','')).upper()

    if user_type.lower() =='employee':
        tasks = get_employee_tasks(user_name)
    else:
        tasks=get_all_tasks_service()

    employee=get_all_employees()
    print(employee)
    # tasks = get_all_tasks_service()
    projects = get_all_projects_service()
    return render(request, "task.html", {"tasks": tasks, "projects": projects,"employee":employee})
