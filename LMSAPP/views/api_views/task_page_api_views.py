import json
from django.db import connection
from django.http import JsonResponse
from LMSAPP.services.task_service import (
    get_all_tasks_service,
    add_task_service,
    update_task_service,
    delete_task_service,
    bulk_delete_tasks_service
)
from LMSAPP.services.employee_service import get_employee_tasks
from LMSAPP.views.api_views.notification_api_views import send_notification
from LMSAPP.services.task_request_service import (
    create_task_request_service,
    approve_task_request_service,
    reject_task_request_service
)

def get_tasks_api(request):
    try:
        user_name = request.session.get('user_name')
        user_type = str(request.session.get('user_type', '')).lower()
        user_role = str(request.session.get('role', '')).lower()
        if user_type == 'employee' or user_role == 'employee':
            tasks = get_employee_tasks(user_name)
        else:
            tasks = get_all_tasks_service()
        return JsonResponse({'status': 'success', 'data': tasks})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def add_task_api(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        task_name = body.get('task_name', '').strip()
        project_name = body.get('project_name', '').strip()
        created_date = body.get('created_date', '').strip()
        due_date = body.get('due_date', '').strip()
        status = body.get('status', 'Not Worked').strip()
        employee_name = body.get('employee_name', '').strip()
        if not task_name or not project_name:
            return JsonResponse({'status': 'error', 'message': 'Task Name and Project Name are required.'}, status=400)

        add_task_service(task_name, project_name, due_date, status, employee_name, created_date=created_date)
        return JsonResponse({'status': 'success', 'message': 'Task created successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def update_task_api(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        task_id = body.get('id')
        task_name = body.get('task_name', '').strip()
        project_name = body.get('project_name', '').strip()
        created_date = body.get('created_date', '').strip()
        due_date = body.get('due_date', '').strip()
        status = body.get('status', '').strip()
        employee_name = body.get('employee_name', '').strip()
       
        if not task_id:
            return JsonResponse({'status': 'error', 'message': 'Task ID is required.'}, status=400)

        updated_by = request.session.get('user_name') or 'Admin'
        user_role = str(request.session.get('role', '')).lower()
        user_type = str(request.session.get('user_type', '')).lower()
        is_employee = (user_role == 'employee' or user_type == 'employee')

        with connection.cursor() as cursor:
            cursor.execute("SELECT task_name, project_name, due_date, status, employee_name, created_date FROM tasks WHERE id = %s", [task_id])
            row = cursor.fetchone()

        if row:
            if not task_name: task_name = row[0]
            if not project_name: project_name = row[1]
            if not due_date: due_date = row[2]
            if not status: status = row[3]
            if not employee_name: employee_name = row[4]
            if not created_date: created_date = row[5]
            current_status = row[3]
        else:
            current_status = status or 'Not Worked'

        if is_employee and current_status == 'Completed':
            return JsonResponse({'status': 'error', 'message': 'Completed tasks are only changed by Admin.'}, status=400)

        # 1. Update task details in DB
        update_task_service(
            task_id, task_name, project_name, due_date, status, employee_name,
            created_date=created_date, updated_by=updated_by, user_role=user_role
        )

        # 2. Send notification
        send_notification(
            task_id=task_id,
            task_name=task_name,
            status=status,
            employee_name=employee_name,
            updated_by=updated_by,
            user_role=user_role
        )

        return JsonResponse({'status': 'success', 'message': 'Task updated successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def delete_task_api(request):
   
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        task_id = body.get('id')
        if not task_id:
            return JsonResponse({'status': 'error', 'message': 'Task ID is required.'}, status=400)
        delete_task_service(task_id)
        return JsonResponse({'status': 'success', 'message': 'Task deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def bulk_delete_tasks_api(request):
  
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        task_ids = body.get('ids') or body.get('task_ids') or body.get('count') or []
        if not task_ids:
            return JsonResponse({'status': 'error', 'message': 'No task IDs provided.'}, status=400)
        bulk_delete_tasks_service(task_ids)
        return JsonResponse({'status': 'success', 'message': f'{len(task_ids)} task(s) deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# def request_task_inprogress_api(request):
#     """
#     API endpoint for employee to request setting a second task to In Progress.
#     """
#     if request.method != 'POST':
#         return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
#     try:
#         body = json.loads(request.body)
#         task_id = body.get('task_id')
#         task_name = body.get('task_name', '').strip()
#         active_task_name = body.get('active_task_name', '').strip()
#         reason = body.get('reason', '').strip()

#         if not task_id or not reason:
#             return JsonResponse({'status': 'error', 'message': 'Task ID and reason are required.'}, status=400)

#         employee_name = request.session.get('user_name') or 'Employee'

#         request_id, created, message = create_task_request_service(
#             task_id=task_id,
#             task_name=task_name,
#             employee_name=employee_name,
#             active_task_name=active_task_name,
#             reason=reason
#         )

#         if not created:
#             return JsonResponse({'status': 'error', 'message': message}, status=400)

#         return JsonResponse({'status': 'success', 'message': message})
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# def action_task_request_api(request):
#     """
#     API endpoint for Admin to approve or reject a task request.
#     """
#     if request.method != 'POST':
#         return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
#     try:
#         user_role = request.session.get('role', '')
#         user_type = request.session.get('user_type', '')
#         is_admin = (user_role in ['ADMIN', 'SUPER_ADMIN']) or (user_type in ['Admin', 'Superadmin'])

#         if not is_admin:
#             return JsonResponse({'status': 'error', 'message': 'Only Admin can approve or reject requests.'}, status=403)

#         body = json.loads(request.body)
#         request_id = body.get('request_id')
#         action = body.get('action', '').strip().lower()
#         remarks = body.get('remarks', '').strip()
#         admin_name = request.session.get('user_name') or 'Admin'

#         if not request_id or action not in ['approve', 'reject']:
#             return JsonResponse({'status': 'error', 'message': 'Valid request_id and action (approve/reject) are required.'}, status=400)

#         if action == 'approve':
#             success, message = approve_task_request_service(request_id, admin_name=admin_name)
#         else:
#             success, message = reject_task_request_service(request_id, admin_name=admin_name, remarks=remarks)

#         if success:
#             return JsonResponse({'status': 'success', 'message': message})
#         else:
#             return JsonResponse({'status': 'error', 'message': message}, status=400)
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
