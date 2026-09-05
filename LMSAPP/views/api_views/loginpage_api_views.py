import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from LMSAPP.services.login_service import authenticate_user_service

@require_POST
def login_api(request):

    try:
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON format in request.'
            }, status=400)
        # print("------------------------------",request.body)

        # 2. Extract and sanitize credentials
        username = str(body.get('username', '')).strip()
        password = str(body.get('password', '')).strip()
 
        if not username or not password:
            return JsonResponse({
                'status': 'error',
                'message': 'Username/Employee ID and password are required.'
            }, status=400)

        # 3. Authenticate against the users table
        user, error_message = authenticate_user_service(username, password)

        

        if not user:
            return JsonResponse({
                'status': 'error',
                'message': error_message or 'Invalid Username/Employee ID or Password.'
            }, status=401)

        # 4. Security: Cycle session key to prevent session fixation attacks
        request.session.cycle_key()

        # 5. Populate session storage
        request.session['user_id'] = user.get('user_id')
        request.session['employee_id'] = user.get('employee_id')
        request.session['user_name'] = user.get('user_name')
        request.session['user_type'] = user.get('user_type')
        request.session['role'] = user.get('role')
        # request.session['superuser'] = user.get('superuser', False)

        # 6. Success response
        return JsonResponse({
            'status': 'success',
            'message': 'Login successful',
            'redirect_url': '/dashboard/',
            'user_name': user.get('user_name'),
            'user_type': user.get('user_type')
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred during login.'
        }, status=500)
