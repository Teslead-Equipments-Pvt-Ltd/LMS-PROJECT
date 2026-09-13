from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Middleware to ensure users are authenticated before accessing protected pages or APIs.
    If an unauthenticated user tries to access a protected URL directly, they are redirected to the login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Allowed paths for unauthenticated users (exempt list)
        exempt_exact_paths = [
            '/login/',
            '/logout/',
            '/api/login/',
            '/',
        ]

        # Check if the path is exempt (e.g. static files, admin, media, or login endpoints)
        is_exempt = (
            path in exempt_exact_paths or
            path.startswith('/static/') or
            path.startswith('/admin/') or
            path.startswith('/media/')
        )

        user_id = request.session.get('user_id')

        # 1. If user is NOT logged in and trying to access a protected route
        if not user_id and not is_exempt:
            # If it is an API call, return JSON 401 Unauthorized
            if path.startswith('/api/'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Authentication required. Please log in.'
                }, status=401)
            
            # If it is a page request, redirect directly to login page
            return redirect('loginpage')

        # 2. If user IS logged in and visits the login page or root '/', redirect to their home
        if user_id and path in ['/login/', '/']:
            user_type = str(request.session.get('user_type', '')).lower()
            role = str(request.session.get('role', '')).lower()

            if user_type == 'employee' or role == 'employee':
                return redirect('task_page')
            else:
                return redirect('dashboard_page')

        response = self.get_response(request)

        # Prevent caching of sensitive authenticated pages in the browser back/forward cache
        if user_id and not path.startswith('/static/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response
