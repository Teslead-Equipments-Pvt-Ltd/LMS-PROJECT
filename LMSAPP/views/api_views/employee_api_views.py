import json
from django.http import JsonResponse
from LMSAPP.services.employee_service import update_employee_service, delete_employee_service,add_employee_service

def update_employee_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        print(data)
        employee_id = data.get('employee_id')
        username = data.get('username')
        role = data.get('role')
        
        update_employee_service(employee_id, username, role)
        return JsonResponse({'status': 'success', 'message': 'Employee updated successfully'})

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
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
