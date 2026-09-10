import datetime
from django.db import connection
from LMSAPP.services.notification_service import create_notification_service


def ensure_task_requests_table():
    """
    Creates the task_requests table if it does not already exist.
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
    Saves a task approval request and notifies Admin.
    """
    ensure_task_requests_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO task_requests (task_id, task_name, employee_name, active_task_name, reason, status)
            VALUES (%s, %s, %s, %s, %s, 'Pending')
        """, [task_id, task_name, employee_name, active_task_name, reason])
        request_id = cursor.lastrowid

    # Send notification to Admin
    admin_message = f"{employee_name} requested to start '{task_name}' while '{active_task_name}' is in progress. Reason: {reason}"
    create_notification_service(
        recipient='Admin',
        title=f"Task Request: {task_name}",
        message=admin_message,
        notification_type='task_request',
        reference_id=request_id
    )

    return request_id


def approve_task_request_service(request_id, admin_name='Admin'):
    """
    Approves the task request:
    1. Updates task_requests status to 'Approved'.
    2. Updates the task's status to 'In Progress' and sets created_date if empty.
    3. Sends notification to the assigned employee.
    """
    ensure_task_requests_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, task_id, task_name, employee_name, status
            FROM task_requests
            WHERE id = %s
        """, [request_id])
        row = cursor.fetchone()

        if not row:
            return False, "Task request not found."

        req_id, task_id, task_name, employee_name, current_status = row

        if current_status != 'Pending':
            return False, f"Request has already been {current_status.lower()}."

        # 1. Update task_requests status to Approved
        cursor.execute("""
            UPDATE task_requests
            SET status = 'Approved', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, [request_id])

        # 2. Update task in tasks table to 'In Progress'
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("""
            UPDATE tasks
            SET status = 'In Progress',
                created_date = CASE 
                    WHEN created_date IS NULL OR created_date = '' THEN %s 
                    ELSE created_date 
                END
            WHERE id = %s
        """, [today_str, task_id])

    # 3. Notify the employee that their request was approved
    create_notification_service(
        recipient=employee_name,
        title=f"Task Request Approved: {task_name}",
        message=f"Admin has approved your request. Task '{task_name}' is now In Progress.",
        notification_type='request_approved',
        reference_id=task_id
    )

    return True, f"Request approved. Task '{task_name}' is now In Progress."


def reject_task_request_service(request_id, admin_name='Admin', remarks=''):
    """
    Rejects the task request:
    1. Updates task_requests status to 'Rejected'.
    2. Sends notification to the employee.
    """
    ensure_task_requests_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, task_id, task_name, employee_name, status
            FROM task_requests
            WHERE id = %s
        """, [request_id])
        row = cursor.fetchone()

        if not row:
            return False, "Task request not found."

        req_id, task_id, task_name, employee_name, current_status = row

        if current_status != 'Pending':
            return False, f"Request has already been {current_status.lower()}."

        # 1. Update task_requests status to Rejected
        cursor.execute("""
            UPDATE task_requests
            SET status = 'Rejected', admin_remarks = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, [remarks, request_id])

    # 2. Notify the employee that their request was rejected
    create_notification_service(
        recipient=employee_name,
        title=f"Task Request Rejected: {task_name}",
        message=f"Admin has rejected your request to set '{task_name}' to In Progress.",
        notification_type='request_rejected',
        reference_id=task_id
    )

    return True, f"Request rejected for task '{task_name}'."
