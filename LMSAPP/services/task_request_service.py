import datetime
from django.db import connection
from LMSAPP.services.notification_service import create_notification_service


def ensure_task_requests_table():
    """
    Creates the 'task_requests' table in database if it does not already exist.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT NOT NULL,
                task_name VARCHAR(255) NOT NULL,
                employee_name VARCHAR(200) NOT NULL,
                active_task_name VARCHAR(255) DEFAULT NULL,
                reason TEXT NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Pending',
                admin_remarks TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)


def create_task_request_service(task_id, task_name, employee_name, active_task_name, reason):
    """
    Saves a task request from an employee and sends a notification to Admin.
    """
    ensure_task_requests_table()

    with connection.cursor() as cursor:
        # 1. Check if the task is already In Progress
        cursor.execute("SELECT status FROM tasks WHERE id = %s", [task_id])
        task_row = cursor.fetchone()
        if task_row and task_row[0] == 'In Progress':
            return None, False, f"Task '{task_name}' is already In Progress."

        # 2. Check if a Pending request already exists for this task
        cursor.execute("""
            SELECT id FROM task_requests 
            WHERE task_id = %s AND status = 'Pending'
            LIMIT 1
        """, [task_id])
        existing = cursor.fetchone()

        if existing:
            request_id = existing[0]
            # Update the existing pending request
            cursor.execute("""
                UPDATE task_requests
                SET reason = %s, active_task_name = %s, employee_name = %s
                WHERE id = %s
            """, [reason, active_task_name, employee_name, request_id])
        else:
            # Insert a new pending request
            cursor.execute("""
                INSERT INTO task_requests (task_id, task_name, employee_name, active_task_name, reason, status)
                VALUES (%s, %s, %s, %s, %s, 'Pending')
            """, [task_id, task_name, employee_name, active_task_name, reason])
            request_id = cursor.lastrowid

    # 3. Notify Admin about the new request
    admin_msg = f"{employee_name} requested to start '{task_name}' (Current active: '{active_task_name}'). Reason: {reason}"
    create_notification_service(
        recipient='Admin',
        title=f"Task Request: {task_name}",
        message=admin_msg,
        notification_type='task_request',
        reference_id=request_id
    )

    return request_id, True, "Approval request sent to Admin."


def approve_task_request_service(request_id, admin_name='Admin'):
    """
    Approves a task request:
    1. Sets task request status to 'Approved'
    2. Updates the task in 'tasks' table to 'In Progress'
    3. Sends notification to employee
    """
    ensure_task_requests_table()

    with connection.cursor() as cursor:
        # Find the request
        cursor.execute("SELECT task_id, task_name, employee_name, status FROM task_requests WHERE id = %s", [request_id])
        row = cursor.fetchone()

        if not row:
            return False, "Task request not found."

        task_id, task_name, employee_name, current_status = row

        if current_status != 'Pending':
            return False, f"Request is already {current_status.lower()}."

        # 1. Mark request as Approved
        cursor.execute("UPDATE task_requests SET status = 'Approved' WHERE id = %s", [request_id])

        # 2. Set task to In Progress in tasks table
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("""
            UPDATE tasks
            SET status = 'In Progress',
                created_date = CASE 
                    WHEN created_date IS NULL OR created_date = '' THEN %s 
                    ELSE created_date 
                END
            WHERE id = %s
        """, [today_date, task_id])

    # 3. Notify the employee that request was approved
    create_notification_service(
        recipient=employee_name,
        title=f"Task Request Approved: {task_name}",
        message=f"Admin approved your request. Task '{task_name}' is now In Progress.",
        notification_type='request_approved',
        reference_id=task_id
    )

    return True, f"Request approved. Task '{task_name}' is now In Progress."


def reject_task_request_service(request_id, admin_name='Admin', remarks=''):
    """
    Rejects a task request:
    1. Sets task request status to 'Rejected' with admin remarks
    2. Sends notification to employee
    """
    ensure_task_requests_table()

    with connection.cursor() as cursor:
        # Find the request
        cursor.execute("SELECT task_id, task_name, employee_name, status FROM task_requests WHERE id = %s", [request_id])
        row = cursor.fetchone()

        if not row:
            return False, "Task request not found."

        task_id, task_name, employee_name, current_status = row

        if current_status != 'Pending':
            return False, f"Request is already {current_status.lower()}."

        # 1. Mark request as Rejected
        cursor.execute("""
            UPDATE task_requests 
            SET status = 'Rejected', admin_remarks = %s 
            WHERE id = %s
        """, [remarks, request_id])

    # 2. Notify the employee that request was rejected
    create_notification_service(
        recipient=employee_name,
        title=f"Task Request Rejected: {task_name}",
        message=f"Admin rejected your request for task '{task_name}'. Reason: {remarks or 'No remarks'}",
        notification_type='request_rejected',
        reference_id=task_id
    )

    return True, f"Request rejected for task '{task_name}'."


def get_all_task_requests_service(employee_name=None, is_admin=True):
    """
    Fetches all task requests for display in the table:
    - Admins see all requests
    - Employees see only their own requests
    """
    ensure_task_requests_table()

    with connection.cursor() as cursor:
        if is_admin:
            cursor.execute("""
                SELECT task_requests.id, 
                       task_requests.task_id, 
                       task_requests.task_name, 
                       task_requests.employee_name, 
                       task_requests.active_task_name, 
                       task_requests.reason, 
                       task_requests.status, 
                       task_requests.admin_remarks, 
                       task_requests.created_at, 
                       tasks.project_name
                FROM task_requests
                LEFT JOIN tasks ON task_requests.task_id = tasks.id
                ORDER BY task_requests.id DESC
            """)
        else:
            cursor.execute("""
                SELECT task_requests.id, 
                       task_requests.task_id, 
                       task_requests.task_name, 
                       task_requests.employee_name, 
                       task_requests.active_task_name, 
                       task_requests.reason, 
                       task_requests.status, 
                       task_requests.admin_remarks, 
                       task_requests.created_at, 
                       tasks.project_name
                FROM task_requests
                LEFT JOIN tasks ON task_requests.task_id = tasks.id
                WHERE task_requests.employee_name = %s
                ORDER BY task_requests.id DESC
            """, [employee_name])

        rows = cursor.fetchall()

    requests_list = []
    for index, row in enumerate(rows, start=1):
        created_date_str = row[8].strftime("%Y-%m-%d %H:%M") if row[8] else ""
        
        requests_list.append({
            's_no': index,
            'id': row[0],
            'task_id': row[1],
            'task_name': row[2] or '',
            'employee_name': row[3] or 'Unknown',
            'active_task_name': row[4] or '-',
            'reason': row[5] or '',
            'status': row[6] or 'Pending',
            'admin_remarks': row[7] or '',
            'created_at': created_date_str,
            'project_name': row[9] or 'General'
        })

    return requests_list
