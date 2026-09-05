import json
from django.http import JsonResponse
from LMSAPP.services.employee_service import update_employee_service, delete_employee_service,add_employee_service

def update_employee_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        employee_id = str(data.get('employee_id', '')).strip()
        username = str(data.get('username', '')).strip()
        role = str(data.get('role', '')).strip()
        password = str(data.get('password', '')).strip()

        if not employee_id or not username:
            return JsonResponse({'status': 'error', 'message': 'Employee ID and Name are required.'}, status=400)

        current_role = request.session.get('role')
        current_emp_id = request.session.get('employee_id')
        is_super_admin = (current_role == 'SUPER_ADMIN')

        # Super Admin can change password for all; Employee can only change their own
        if password:
            if not is_super_admin and current_emp_id != employee_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Permission denied: You can only change your own password.'
                }, status=403)

        update_employee_service(
            employee_id=employee_id,
            username=username,
            role=role,
            password=password if password else None,
            is_super_admin=is_super_admin
        )
        return JsonResponse({'status': 'success', 'message': 'Employee updated successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def delete_employee_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        
        delete_employee_service(employee_id)
        return JsonResponse({'status': 'success', 'message': 'Employee deleted successfully'})

def add_employee_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id', '').strip()
        username = data.get('username', '').strip()
        role = data.get('role', 'EMPLOYEE').strip()
        password = data.get('password', '').strip()  # <-- 1. EXTRACT PASSWORD

        if not employee_id or not username:
            return JsonResponse({'status': 'error', 'message': 'Employee ID and Name are required.'}, status=400)
        
        if not password:
            return JsonResponse({'status': 'error', 'message': 'Password is required.'}, status=400)

        # 2. PASS PASSWORD TO SERVICE
        add_employee_service(employee_id, username, role, password)
        
        return JsonResponse({'status': 'success', 'message': 'Employee added successfully!'})
    except ValueError as ve:
        return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Failed to add employee.'}, status=500)

