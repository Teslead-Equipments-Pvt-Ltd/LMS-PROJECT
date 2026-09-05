from django.db import connection
from django.contrib.auth.hashers import check_password

def authenticate_user_service(username, password):

    if not username or not password:
        return None, 'Username/Employee ID and password are required.'

    username = username.strip()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, employee_id, username, password, role 
            FROM users 
            WHERE username = %s OR employee_id = %s
            LIMIT 1
            """,
            [username, username]
        )
        row = cursor.fetchone()

    if row:
        user_id, emp_id, db_username, db_password, db_role = row

        # Verify password (hashed or plain text fallback)
        is_valid_pwd = False
        if db_password:
            if check_password(password, db_password):
                is_valid_pwd = True
            elif db_password == password:
                is_valid_pwd = True

        if is_valid_pwd:
            # Map roles to user_type and superuser status
            if db_role == 'SUPER_ADMIN':
                user_type = 'Superadmin'
                superuser = True
            elif db_role == 'ADMIN':
                user_type = 'Admin'
                superuser = False
            else:
                user_type = 'Employee'
                superuser = False

            user_dict = {
                'user_id': user_id,
                'employee_id': emp_id,
                'user_name': db_username,
                'user_type': user_type,
                'superuser': superuser,
                'role': db_role
            }
            return user_dict, None
        else:
            return None, 'Invalid password. Please try again.'

    return None, 'Invalid Username/Employee ID or Password.'

