from django.db import connection
from django.contrib.auth.hashers import make_password
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


# 1. EDIT / UPDATE Employee Service
def update_employee_service(employee_id, username, role, password=None, is_super_admin=False):
  
    with connection.cursor() as cursor:
        # Non-superadmin cannot change roles
        if not is_super_admin:
            cursor.execute("SELECT role FROM users WHERE employee_id = %s", [employee_id])
            row = cursor.fetchone()
            if row:
                role = row[0]

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


# 2. DELETE Employee Service
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


# 3. ADD Employee Service
def add_employee_service(employee_id, username, role, password):
    hashed_pwd = make_password(password)
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE employee_id = %s", [employee_id])
        if cursor.fetchone():
            raise ValueError(f"Employee ID '{employee_id}' already exists.")

        cursor.execute("""
            INSERT INTO users (employee_id, username, role, password)
            VALUES (%s, %s, %s, %s)
        """, [employee_id, username, role, hashed_pwd])
    return True

