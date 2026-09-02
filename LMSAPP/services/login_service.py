from django.db import connection
from django.contrib.auth.hashers import make_password, check_password

def ensure_employee_table():
    """
    Executes raw SQL to create the 'employee' table if missing, ensures role_id column exists,
    and updates password and role_id for superadmin, admin, and employee users.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(150) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(254) NULL,
                role_id INT DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Add role_id column if table existed previously without it
        try:
            cursor.execute("ALTER TABLE employee ADD COLUMN role_id INT DEFAULT 3;")
        except Exception:
            pass

        # Insert or Update Superadmin (username: superadmin, password: superadmin123, role_id: 1)
        superadmin_pwd = make_password("superadmin123")
        cursor.execute("""
            INSERT INTO employee (username, password, email, role_id)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE password = %s, role_id = 1;
        """, ['superadmin', superadmin_pwd, 'superadmin@gmail.com', 1, superadmin_pwd])

        # Insert or Update Admin (username: admin, password: admin123, role_id: 2)
        admin_pwd = make_password("admin123")
        cursor.execute("""
            INSERT INTO employee (username, password, email, role_id)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE password = %s, role_id = 2;
        """, ['admin', admin_pwd, 'admin@gmail.com', 2, admin_pwd])

        # Insert or Update Employee (username: employee, password: employee123, role_id: 3)
        employee_pwd = make_password("employee123")
        cursor.execute("""
            INSERT INTO employee (username, password, email, role_id)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE password = %s, role_id = 3;
        """, ['employee', employee_pwd, 'employee@gmail.com', 3, employee_pwd])

def add_employee_to_db(username, password, email="", role_id=3):
    """
    Raw SQL helper function to manually store new Superadmin, Admin, or Employee details into 'employee' table.
    role_id: 1 = Superadmin, 2 = Admin, 3 = Employee
    """
    ensure_employee_table()
    hashed_password = make_password(password)
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO employee (username, password, email, role_id)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE password = %s, email = %s, role_id = %s;
        """, [username, hashed_password, email, role_id, hashed_password, email, role_id])
    return True

def authenticate_user_service(username, password):
    """
    Authenticates user credentials against the 'employee' database table using raw SQL.
    Returns tuple: (user_dict, error_message)
    """
    if not username or not password:
        return None, 'Username/Employee ID and password are required.'

    username = username.strip()

    try:
        ensure_employee_table()
    except Exception as e:
        print(f"Table initialization error: {e}")

    # Fetch user record by username from employee table using raw SQL
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, username, password, email, role_id FROM employee WHERE username = %s",
            [username]
        )
        row = cursor.fetchone()

    if row:
        emp_id, db_username, db_password, db_email, db_role_id = row
        db_role_id = db_role_id or 3

        # Verify password (hashed or plain text fallback)
        is_valid_pwd = False
        if db_password:
            if check_password(password, db_password):
                is_valid_pwd = True
            elif db_password == password:
                is_valid_pwd = True

        if is_valid_pwd:
            # Map role_id to user_type and superuser status
            if db_role_id == 1:
                user_type = 'Superadmin'
                superuser = True
            elif db_role_id == 2:
                user_type = 'Admin'
                superuser = False
            else:
                user_type = 'Employee'
                superuser = False

            user_dict = {
                'user_id': emp_id,
                'user_name': db_username,
                'user_type': user_type,
                'superuser': superuser,
                'email': db_email
            }
            return user_dict, None
        else:
            return None, 'Invalid password. Please try again.'

    return None, 'Invalid Username/Employee ID or Password.'
