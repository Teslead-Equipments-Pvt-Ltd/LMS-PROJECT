import json
from django.http import JsonResponse
from LMSAPP.services.notification_service import (
    create_notification_service,
    get_notifications_by_user
)

def send_notification(task_id, task_name, status, employee_name, updated_by=None, user_role=None):
    """
    Sends task update notifications based on task status and user role:
    - Status 'completed' -> Notifies Admin only.
    - Status 'on hold' / 'hold' / 'pending' -> Notifies both Admin and assigned Employee.
    """
    # 1. Identify who made the update
    if user_role in ['ADMIN', 'SUPER_ADMIN']:
        changed_by = "Admin"
    else:
        changed_by = updated_by or employee_name

    current_status = (status or "").lower()

    # 2. If status is Completed -> Notify Admin only
    if current_status == 'completed':
        create_notification_service(
            recipient='Admin',
            title=f"Task Completed: {task_name}",
            message=f"{changed_by} has completed the task",
            notification_type='task_completed',
            reference_id=task_id
        )

    # 3. If status is On Hold or Pending -> Notify both Admin and Employee
    elif current_status in ['on hold', 'hold', 'pending']:
        status_text = "on hold"

        # (a) Send notification to Admin
        create_notification_service(
            recipient='Admin',
            title=f"Task {status_text}: {task_name}",
            message=f"{changed_by} has put the task {status_text}",
            notification_type=f"task_{current_status.replace(' ', '_')}",
            reference_id=task_id
        )

        # (b) Send notification to assigned Employee
        if employee_name and employee_name != 'Admin':
            create_notification_service(
                recipient=employee_name,
                title=f"Task {status_text}: {task_name}",
                message=f"{changed_by} has put the task {status_text}",
                notification_type=f"task_{current_status.replace(' ', '_')}",
                reference_id=task_id
            )

    return True

def get_notifications_api(request):
    """
    API view to fetch all notifications for the current logged-in user or admin.
    """
    try:
        current_user = request.session.get('user_name')
        current_role = request.session.get('role', '')
        is_admin = current_role in ['ADMIN', 'SUPER_ADMIN']

        notifications = get_notifications_by_user(recipient=current_user, is_admin=is_admin)
        return JsonResponse({'status': 'success', 'data': notifications})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
