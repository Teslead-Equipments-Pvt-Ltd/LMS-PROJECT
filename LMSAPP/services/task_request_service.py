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
    Allows sending approval request whenever task is not In Progress.
    If a pending request already exists for this task, updates it and notifies Admin.
    """
    ensure_task_requests_table()
    with connection.cursor() as cursor:
        # 1. Check if task is already In Progress
        cursor.execute("SELECT status FROM tasks WHERE id = %s", [task_id])
        task_row = cursor.fetchone()
        if task_row and task_row[0] == 'In Progress':
            return None, False, f"Task '{task_name}' is already In Progress."

        # 2. Check if there is already a Pending request for this task
        cursor.execute("""
            SELECT id FROM task_requests 
            WHERE task_id = %s AND status = 'Pending'
            ORDER BY id DESC LIMIT 1
        """, [task_id])
        existing = cursor.fetchone()

        if existing:
            request_id = existing[0]
            # Update existing pending request with new reason and conflict task
            cursor.execute("""
                UPDATE task_requests
                SET reason = %s, active_task_name = %s, employee_name = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, [reason, active_task_name, employee_name, request_id])
        else:
            # Insert a new Pending request
            cursor.execute("""
                INSERT INTO task_requests (task_id, task_name, employee_name, active_task_name, reason, status)
                VALUES (%s, %s, %s, %s, %s, 'Pending')
            """, [task_id, task_name, employee_name, active_task_name, reason])
            request_id = cursor.lastrowid

    # 3. Always send notification to Admin so Admin is alerted
    admin_message = f"{employee_name} requested to start '{task_name}' while '{active_task_name}' is in progress. Reason: {reason}"
    create_notification_service(
        recipient='Admin',
        title=f"Task Request: {task_name}",
        message=admin_message,
        notification_type='task_request',
        reference_id=request_id
    )

    return request_id, True, "Approval request sent to Admin."


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

        # 1. Update task_requests status to Approved for this task
        cursor.execute("""
            UPDATE task_requests
            SET status = 'Approved', updated_at = CURRENT_TIMESTAMP
            WHERE task_id = %s AND status = 'Pending'
        """, [task_id])

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


def get_all_task_requests_service(employee_name=None, is_admin=True):
    """
    Fetches task approval requests with only one record per task.
    Prioritizes 'Pending' status if any exists, otherwise picks the latest request.
    Admins see all requests; employees see only their own requests.
    """
    ensure_task_requests_table()
    with connection.cursor() as cursor:
        if is_admin:
            cursor.execute("""
                SELECT 
                    tr.id, 
                    tr.task_id, 
                    tr.task_name, 
                    tr.employee_name, 
                    tr.active_task_name, 
                    tr.reason, 
                    tr.status, 
                    tr.admin_remarks, 
                    tr.created_at, 
                    tr.updated_at,
                    t.project_name
                FROM task_requests tr
                INNER JOIN (
                    SELECT 
                        task_id,
                        COALESCE(
                            MAX(CASE WHEN status = 'Pending' THEN id END),
                            MAX(id)
                        ) AS chosen_id
                    FROM task_requests
                    GROUP BY task_id
                ) latest_tr ON tr.id = latest_tr.chosen_id
                LEFT JOIN tasks t ON tr.task_id = t.id
                ORDER BY tr.created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT 
                    tr.id, 
                    tr.task_id, 
                    tr.task_name, 
                    tr.employee_name, 
                    tr.active_task_name, 
                    tr.reason, 
                    tr.status, 
                    tr.admin_remarks, 
                    tr.created_at, 
                    tr.updated_at,
                    t.project_name
                FROM task_requests tr
                INNER JOIN (
                    SELECT 
                        task_id,
                        COALESCE(
                            MAX(CASE WHEN status = 'Pending' THEN id END),
                            MAX(id)
                        ) AS chosen_id
                    FROM task_requests
                    WHERE employee_name = %s
                    GROUP BY task_id
                ) latest_tr ON tr.id = latest_tr.chosen_id
                LEFT JOIN tasks t ON tr.task_id = t.id
                WHERE tr.employee_name = %s
                ORDER BY tr.created_at DESC
            """, [employee_name, employee_name])
        rows = cursor.fetchall()

    requests_list = []
    for index, row in enumerate(rows, start=1):
        created_at_val = row[8]
        updated_at_val = row[9]
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
            'created_at': created_at_val.strftime("%Y-%m-%d %H:%M") if created_at_val else '',
            'updated_at': updated_at_val.strftime("%Y-%m-%d %H:%M") if updated_at_val else '',
            'project_name': row[10] or 'General'
        })
    return requests_list

