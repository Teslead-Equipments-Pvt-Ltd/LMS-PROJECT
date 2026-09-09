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
from LMSAPP.views.api_views.notification_api_views import send_notification

def get_tasks_api(request):
    
    try:
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
        status = body.get('status', 'Not Worked').strip()
        employee_name = body.get('employee_name', '').strip()
       
        if not task_id:
            return JsonResponse({'status': 'error', 'message': 'Task ID is required.'}, status=400)

        updated_by = request.session.get('user_name') or 'Admin'
        user_role = str(request.session.get('role', '')).lower()
        user_type = str(request.session.get('user_type', '')).lower()

        if user_role == 'employee' or user_type == 'employee':
            # from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT status FROM tasks WHERE id = %s", [task_id])
                row = cursor.fetchone()
                if row and row[0] == 'Completed':
                    return JsonResponse({'status': 'error', 'message': 'Completed tasks are only changed by Admin.'}, status=400)

        # 1. Update task details in DB
        update_task_service(
            task_id, task_name, project_name, due_date, status, employee_name,
            created_date=created_date
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
        task_ids = body.get('ids', [])
        if not task_ids:
            return JsonResponse({'status': 'error', 'message': 'No task IDs provided.'}, status=400)
        bulk_delete_tasks_service(task_ids)
        return JsonResponse({'status': 'success', 'message': f'{len(task_ids)} task(s) deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
