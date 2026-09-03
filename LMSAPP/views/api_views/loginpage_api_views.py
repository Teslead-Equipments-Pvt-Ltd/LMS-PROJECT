import json
from django.http import JsonResponse
from LMSAPP.services.login_service import authenticate_user_service

def login_api(request):
    """
    """
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
        
    try:
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        
        if not username or not password:
            return JsonResponse({'message': 'Username/Employee ID and password are required.'}, status=400)
            
        user, error_message = authenticate_user_service(username, password)
        
        if user:
           
            request.session['user_id'] = user['user_id']
            request.session['user_name'] = user['user_name']
            request.session['user_type'] = user['user_type']
            request.session['superuser'] = user['superuser']
            
            return JsonResponse({
                'message': 'Login successful',
                'redirect_url': '/base/',
                'user_name': user['user_name'],
                'user_type': user['user_type'],
             
            })
        else:
            return JsonResponse({'message': error_message or 'Invalid Username/Employee ID or Password.'}, status=401)
            
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
