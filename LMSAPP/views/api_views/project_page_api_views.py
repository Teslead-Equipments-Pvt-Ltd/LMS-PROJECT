import json
from django.http import JsonResponse
from LMSAPP.services.project_service import (
    get_all_projects_service,
    add_project_service,
    update_project_service,
    delete_project_service,
    bulk_delete_projects_service
)

def get_projects_api(request):
    
    try:
        projects = get_all_projects_service()
        return JsonResponse({'status': 'success', 'data': projects})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def add_project_api(request):
   
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        project_name = body.get('project_name', '').strip()
        project_type = body.get('project_type', '').strip()
        status = body.get('status', 'Not Worked').strip()
        due_date = body.get('due_date', '').strip()

        if not project_name or not project_type:
            return JsonResponse({'status': 'error', 'message': 'Project Name and Type are required.'}, status=400)

        add_project_service(project_name, project_type, status, due_date)
        return JsonResponse({'status': 'success', 'message': 'Project created successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def update_project_api(request):
   
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        project_id = body.get('id')
        project_name = body.get('project_name', '').strip()
        project_type = body.get('project_type', '').strip()
        status = body.get('status', 'Not Worked').strip()
        created_date = body.get('created_date', '').strip()
        completion_date = body.get('completion_date', '').strip()
        due_date = body.get('due_date', '').strip()

        if not project_id:
            return JsonResponse({'status': 'error', 'message': 'Project ID is required.'}, status=400)

        update_project_service(project_id, project_name, project_type, status, created_date, completion_date, due_date)
        return JsonResponse({'status': 'success', 'message': 'Project updated successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def delete_project_api(request):
    
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        project_id = body.get('id')
        if not project_id:
            return JsonResponse({'status': 'error', 'message': 'Project ID is required.'}, status=400)
        delete_project_service(project_id)
        return JsonResponse({'status': 'success', 'message': 'Project deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def bulk_delete_projects_api(request):
    
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        project_ids = body.get('ids', [])
        if not project_ids:
            return JsonResponse({'status': 'error', 'message': 'No project IDs provided.'}, status=400)
        bulk_delete_projects_service(project_ids)
        return JsonResponse({'status': 'success', 'message': f'{len(project_ids)} project(s) deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
