from django.shortcuts import render, redirect
from LMSAPP.services.assigned_task_service import get_live_employee_inprogress_tasks

def assigned_task_page(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('loginpage')

    user_role = request.session.get('role', '')
    user_type = request.session.get('user_type', '')
    is_admin = (user_role in ['ADMIN', 'SUPER_ADMIN']) or (user_type in ['Admin', 'Superadmin'])

    employees_data, stats = get_live_employee_inprogress_tasks()

    context = {
        'employees': employees_data,
        'stats': stats,
        'is_admin': is_admin,
        'current_user': user_name
    }
    return render(request, 'assigned_task.html', context)