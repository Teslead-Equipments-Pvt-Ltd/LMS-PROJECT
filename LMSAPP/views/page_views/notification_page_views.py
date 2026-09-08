from django.shortcuts import render
from LMSAPP.services.notification_service import get_notifications_by_user

def notification_page(request):
    current_user = request.session.get('user_name')
    user_role = request.session.get('role', '')
    is_admin = user_role in ['ADMIN', 'SUPER_ADMIN']
    
    notifications = get_notifications_by_user(recipient=current_user, is_admin=is_admin)
    return render(request, 'notification.html', {'notifications': notifications})
