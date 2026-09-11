import datetime
from django.db import connection
from LMSAPP.services.task_service import tasks_table

def get_live_employee_inprogress_tasks():
    """
    Fetches all employees and their currently 'In Progress' tasks.
    If an employee has multiple In-Progress tasks, all of them are collected in a list
    so they can be displayed on the same line.
    """
    tasks_table()
    with connection.cursor() as cursor:
        # Fetch all users
        cursor.execute("""
            SELECT id, employee_id, username, role
            FROM users
            ORDER BY username ASC
        """)
        users_rows = cursor.fetchall()

        # Fetch all tasks that are currently In Progress
        cursor.execute("""
            SELECT id, task_name, project_name, created_date, due_date, status, employee_name
            FROM tasks
            WHERE LOWER(TRIM(status)) IN ('in progress', 'inprogress')
            ORDER BY id DESC
        """)
        task_rows = cursor.fetchall()

    in_progress_tasks = []
    for t in task_rows:
        in_progress_tasks.append({
            'id': t[0],
            'task_name': t[1],
            'project_name': t[2],
            'created_date': t[3] or '',
            'due_date': t[4] or '',
            'status': t[5],
            'assigned_raw': t[6] or ''
        })

    employees_data = []
    working_count = 0
    multitasking_count = 0

    for u in users_rows:
        user_id = u[0]
        employee_id = u[1] or ''
        username = (u[2] or '').strip()
        role = (u[3] or '').strip()

        # Split and normalize usernames for matching
        clean_user_lower = username.lower()

        # Filter out system administrators unless they are assigned tasks or marked as employee
        is_employee_role = role.upper() == 'EMPLOYEE'
        assigned_to_any_task = any(
            clean_user_lower in [x.strip().lower() for x in t['assigned_raw'].split(',') if x.strip()]
            for t in in_progress_tasks
        )

        if not is_employee_role and not assigned_to_any_task:
            continue

        emp_tasks = []
        for t in in_progress_tasks:
            assigned_names = [x.strip().lower() for x in t['assigned_raw'].split(',') if x.strip()]
            if clean_user_lower in assigned_names:
                emp_tasks.append({
                    'id': t['id'],
                    'task_name': t['task_name'],
                    'project_name': t['project_name'],
                    'created_date': t['created_date'],
                    'due_date': t['due_date'],
                    'status': t['status'],
                })

        task_count = len(emp_tasks)
        if task_count > 0:
            working_count += 1
        if task_count >= 2:
            multitasking_count += 1

        employees_data.append({
            'id': user_id,
            'employee_id': employee_id,
            'username': username,
            'role': role,
            'tasks': emp_tasks,
            'task_count': task_count,
            'is_working': task_count > 0
        })

    # Sort employees: employees with active in-progress tasks first (descending count), then alphabetically
    employees_data.sort(key=lambda x: (-x['task_count'], x['username'].lower()))

    stats = {
        'total_employees': len(employees_data),
        'working_count': working_count,
        'idle_count': len(employees_data) - working_count,
        'multitasking_count': multitasking_count,
        'total_active_tasks': len(in_progress_tasks),
        'server_time': datetime.datetime.now().strftime("%I:%M:%S %p")
    }

    return employees_data, stats
