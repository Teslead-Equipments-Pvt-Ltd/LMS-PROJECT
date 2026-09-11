from django.shortcuts import render, redirect
from LMSAPP.services.task_request_service import get_all_task_requests_service

def task_request_page(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('loginpage')

    user_role = request.session.get('role', '')
    user_type = request.session.get('user_type', '')
    is_admin = (user_role in ['ADMIN', 'SUPER_ADMIN']) or (user_type in ['Admin', 'Superadmin'])

    requests_list = get_all_task_requests_service(employee_name=user_name, is_admin=is_admin)

    # total_count = len(requests_list)
    # pending_count = sum(1 for r in requests_list if r['status'] == 'Pending')
    # approved_count = sum(1 for r in requests_list if r['status'] == 'Approved')
    # rejected_count = sum(1 for r in requests_list if r['status'] == 'Rejected')

    context = {
        'task_requests': requests_list,
        # 'total_count': total_count,
        # 'pending_count': pending_count,
        # 'approved_count': approved_count,
        # 'rejected_count': rejected_count,
        'is_admin': is_admin,
    }
    return render(request, "task_request.html", context)