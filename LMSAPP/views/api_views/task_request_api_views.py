import json
from django.db import connection
from django.http import JsonResponse
from LMSAPP.views.api_views.notification_api_views import send_notification
from LMSAPP.services.task_request_service import (
    create_task_request_service,
    approve_task_request_service,
    reject_task_request_service,
    get_all_task_requests_service
)



def request_task_inprogress_api(request):
    """
    API endpoint for employee to request setting a second task to In Progress.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        task_id = body.get('task_id')
        task_name = body.get('task_name', '').strip()
        active_task_name = body.get('active_task_name', '').strip()
        reason = body.get('reason', '').strip()

        if not task_id or not reason:
            return JsonResponse({'status': 'error', 'message': 'Task ID and reason are required.'}, status=400)

        employee_name = request.session.get('user_name') or 'Employee'

        request_id, created, message = create_task_request_service(
            task_id=task_id,
            task_name=task_name,
            employee_name=employee_name,
            active_task_name=active_task_name,
            reason=reason
        )

        if not created:
            return JsonResponse({'status': 'error', 'message': message}, status=400)

        return JsonResponse({'status': 'success', 'message': message})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def action_task_request_api(request):
    """
    API endpoint for Admin to approve or reject a task request.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    try:
        user_role = request.session.get('role', '')
        user_type = request.session.get('user_type', '')
        is_admin = (user_role in ['ADMIN', 'SUPER_ADMIN']) or (user_type in ['Admin', 'Superadmin'])

        if not is_admin:
            return JsonResponse({'status': 'error', 'message': 'Only Admin can approve or reject requests.'}, status=403)

        body = json.loads(request.body)
        request_id = body.get('request_id')
        action = body.get('action', '').strip().lower()
        remarks = body.get('remarks', '').strip()
        admin_name = request.session.get('user_name') or 'Admin'

        if not request_id or action not in ['approve', 'reject']:
            return JsonResponse({'status': 'error', 'message': 'Valid request_id and action (approve/reject) are required.'}, status=400)

        if action == 'approve':
            success, message = approve_task_request_service(request_id, admin_name=admin_name)
        else:
            success, message = reject_task_request_service(request_id, admin_name=admin_name, remarks=remarks)

        if success:
            return JsonResponse({'status': 'success', 'message': message})
        else:
            return JsonResponse({'status': 'error', 'message': message}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_task_requests_live_api(request):
    """
    API endpoint to fetch task requests for live updates.
    """
    try:
        user_role = str(request.session.get('role', '')).upper()
        user_type = str(request.session.get('user_type', '')).upper()
        is_admin = (user_role in ['ADMIN', 'SUPER_ADMIN']) or (user_type in ['ADMIN', 'SUPERADMIN'])
        employee_name = request.session.get('user_name')

        requests_list = get_all_task_requests_service(employee_name=employee_name, is_admin=is_admin)
        return JsonResponse({
            'status': 'success',
            'data': requests_list,
            'is_admin': is_admin
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)