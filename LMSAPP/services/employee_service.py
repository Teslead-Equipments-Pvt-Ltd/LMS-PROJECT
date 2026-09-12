from django.db import connection
from django.contrib.auth.hashers import make_password  
from LMSAPP.services.task_service import tasks_table

def get_all_employees():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, employee_id, username, role
            FROM users
        """)
        employees = cursor.fetchall()
        
        employees_list = []
        for emp in employees:
            employees_list.append({
                'id': emp[0],
                'employee_id': emp[1],
                'username': emp[2],
                'role': emp[3]
            })

    return employees_list



def update_employee_service(employee_id, username, role, password=None):
    """
    Updates the username and role for an employee in the 'users' table.
    """
    with connection.cursor() as cursor:
        if password:
            hashed_pwd = make_password(password)
            cursor.execute("""
            UPDATE users
            SET username = %s, role = %s, password = %s
            WHERE employee_id = %s
        """, [username, role, hashed_pwd, employee_id])
        else:
            cursor.execute("""
            UPDATE users
            SET username = %s, role = %s
            WHERE employee_id = %s
        """, [username, role, employee_id])
    return True



def delete_employee_service(employee_id):
    """
    Permanently removes an employee from the 'users' table using their employee_id.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM users
            WHERE employee_id = %s
        """, [employee_id])
    return True


def add_employee_service(employee_id, username, role, password):
    """
    Inserts a new employee record into the 'users' table.
    """
    hashed_pwd = make_password(password)
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO users (employee_id, username, role, password)
            VALUES (%s, %s, %s, %s)
        """, [employee_id, username, role, hashed_pwd])
    return True


def get_employee_tasks(username=None, employee_id=None):
    tasks_table()

    if employee_id and not username:
        with connection.cursor() as cursor:
            cursor.execute("SELECT username FROM users WHERE employee_id = %s LIMIT 1", [employee_id])
            user_row = cursor.fetchone()
            if user_row:
                username = user_row[0]

    if not username:
        return []

    clean_user = username.strip().lower()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, task_name, project_name, created_date, due_date, status, employee_name
            FROM tasks 
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        
        tasks = []
        for row in rows:
            emp_str = (row[6] or '').strip()
            assigned_names = [e.strip().lower() for e in emp_str.split(',') if e.strip()]
            if clean_user in assigned_names or clean_user == emp_str.lower() or (clean_user and clean_user in emp_str.lower()):
                tasks.append({
                    's_no': len(tasks) + 1,
                    'id': row[0],
                    'task_name': row[1],
                    'project_name': row[2],
                    'created_date': row[3] or '',
                    'due_date': row[4] or '',
                    'status': row[5] or 'Not Worked',
                    'employee_name': row[6] or ''
                })
    return tasks



