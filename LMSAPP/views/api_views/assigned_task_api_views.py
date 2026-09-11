from django.http import JsonResponse
from LMSAPP.services.assigned_task_service import get_live_employee_inprogress_tasks

def live_assigned_tasks_api(request):
    """
    Real-time API endpoint returning all employees and their currently In-Progress tasks.
    Used by assigned_task.html for live polling and instant auto-update.
    """
    try:
        employees_data, stats = get_live_employee_inprogress_tasks()
        return JsonResponse({
            'status': 'success',
            'employees': employees_data,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
