import json
import datetime
from django.db import connection
from LMSAPP.services.notification_service import create_notification_service

def tasks_table():
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_name VARCHAR(200) NOT NULL,
                project_name VARCHAR(200) NOT NULL,
                created_date VARCHAR(50) DEFAULT NULL,
                due_date VARCHAR(50) DEFAULT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Not Worked',
                employee_name VARCHAR(200) DEFAULT NULL,
                employee_status TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN employee_name VARCHAR(200) DEFAULT NULL;")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN created_date VARCHAR(50) DEFAULT NULL;")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN employee_status TEXT DEFAULT NULL;")
        except Exception:
            pass

def calculate_overall_status(emp_status_dict):
    if not emp_status_dict:
        return 'Not Worked'
    statuses = [str(v).strip() for v in emp_status_dict.values()]
    # If all assigned employees marked Completed -> Completed
    if all(s.lower() == 'completed' for s in statuses):
        return 'Completed'
    # If any is In Progress -> In Progress
    if any(s.lower() in ['in progress', 'inprogress'] for s in statuses):
        return 'In Progress'
    # If any is On Hold -> On Hold
    if any(s.lower() in ['on hold', 'onhold'] for s in statuses):
        return 'On Hold'
    return 'Not Worked'

def parse_employee_status(employee_name, employee_status_raw, default_status='Not Worked'):
    emp_list = [e.strip() for e in (employee_name or '').split(',') if e.strip()]
    emp_status_dict = {}
    if employee_status_raw:
        try:
            if isinstance(employee_status_raw, dict):
                emp_status_dict = employee_status_raw
            else:
                emp_status_dict = json.loads(employee_status_raw)
        except Exception:
            emp_status_dict = {}
    
    final_dict = {}
    for emp in emp_list:
        final_dict[emp] = emp_status_dict.get(emp, default_status)
    return final_dict

def get_all_tasks_service():
    tasks_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, task_name, project_name, created_date, due_date, status, employee_name, employee_status
            FROM tasks ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        
    tasks = []
    for index, row in enumerate(rows, start=1):
        emp_name = row[6]
        raw_emp_status = row[7]
        overall_status_db = row[5]
        
        emp_status_dict = parse_employee_status(emp_name, raw_emp_status, default_status=overall_status_db or 'Not Worked')
        computed_overall_status = calculate_overall_status(emp_status_dict) if emp_status_dict else (overall_status_db or 'Not Worked')
        
        tasks.append({
            's_no': index,
            'id': row[0],
            'task_name': row[1],
            'project_name': row[2],
            'created_date': row[3],
            'due_date': row[4],
            'status': computed_overall_status,
            'employee_name': emp_name,
            'employee_status': emp_status_dict,
            'employee_status_json': json.dumps(emp_status_dict),
        })
    return tasks

def add_task_service(task_name, project_name, due_date, status, employee_name, created_date=None):
    tasks_table()
    emp_status_dict = parse_employee_status(employee_name, {}, default_status=status or 'Not Worked')
    overall_status = calculate_overall_status(emp_status_dict) if emp_status_dict else (status or 'Not Worked')
    emp_status_json = json.dumps(emp_status_dict)

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO tasks (task_name, project_name, due_date, status, employee_name, created_date, employee_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [task_name, project_name, due_date, overall_status, employee_name, created_date, emp_status_json])
        task_id = cursor.lastrowid

    # 1. Notify assigned employee
    if employee_name:
        create_notification_service(
            recipient=employee_name,
            title=f"New Task Assigned: {task_name}",
            message=f"You have been assigned to task '{task_name}' in project '{project_name}'. Due date: {due_date or 'Not specified'}.",
            notification_type='task_created',
            reference_id=task_id
        )

    # 2. Notify Admin
    create_notification_service(
        recipient='Admin',
        title=f"New Task Created: {task_name}",
        message=f"Task '{task_name}' was created for project '{project_name}' and assigned to '{employee_name or 'Unassigned'}'.",
        notification_type='task_created',
        reference_id=task_id
    )

    return True

def update_task_service(task_id, task_name, project_name, due_date, status, employee_name, created_date=None, updating_employee=None):
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    tasks_table()

    with connection.cursor() as cursor:
        cursor.execute("SELECT employee_status, status, created_date FROM tasks WHERE id = %s", [task_id])
        row = cursor.fetchone()
        existing_emp_status_raw = row[0] if row else None
        existing_status_db = row[1] if row else 'Not Worked'
        db_created_date = row[2] if row else None

    emp_status_dict = parse_employee_status(employee_name, existing_emp_status_raw, default_status=existing_status_db)
    
    if updating_employee and updating_employee in emp_status_dict:
        emp_status_dict[updating_employee] = status
    elif not updating_employee and status:
        # If Admin explicitly selected a status, apply to employees
        for emp in emp_status_dict:
            emp_status_dict[emp] = status

    overall_status = calculate_overall_status(emp_status_dict) if emp_status_dict else (status or 'Not Worked')
    
    if (overall_status == "In Progress" or status == "In Progress") and not created_date and not db_created_date:
        created_date = today_str
    elif not created_date:
        created_date = db_created_date

    emp_status_json = json.dumps(emp_status_dict)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE tasks
            SET task_name = %s, project_name = %s, created_date = %s, due_date = %s, status = %s, employee_name = %s, employee_status = %s
            WHERE id = %s
        """, [task_name, project_name, created_date, due_date, overall_status, employee_name, emp_status_json, task_id])

        if overall_status.lower() == 'completed':
            cursor.execute("SELECT employee_name, task_name FROM tasks WHERE id = %s", [task_id])
            row = cursor.fetchone()
            if row:
                emp_name = row[0]
                t_name = row[1]
                create_notification_service(
                    recipient=emp_name,
                    title=f"Task Completed: {t_name}",
                    message=f"Task '{t_name}' has been completed by all assigned employees.",
                    notification_type='task_completed',
                    reference_id=task_id
                )

    return True

def update_employee_task_status_service(task_id, username, new_status):
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    tasks_table()

    with connection.cursor() as cursor:
        cursor.execute("SELECT task_name, project_name, due_date, created_date, status, employee_name, employee_status FROM tasks WHERE id = %s", [task_id])
        row = cursor.fetchone()
        if not row:
            return False, "Task not found"

        task_name, project_name, due_date, created_date, current_overall_status, employee_name, employee_status_raw = row
        emp_status_dict = parse_employee_status(employee_name, employee_status_raw, default_status=current_overall_status)

        emp_status_dict[username] = new_status

        overall_status = calculate_overall_status(emp_status_dict)

        if (overall_status == "In Progress" or new_status == "In Progress") and not created_date:
            created_date = today_str

        emp_status_json = json.dumps(emp_status_dict)

        cursor.execute("""
            UPDATE tasks
            SET status = %s, created_date = %s, employee_status = %s
            WHERE id = %s
        """, [overall_status, created_date, emp_status_json, task_id])

        if overall_status.lower() == 'completed':
            create_notification_service(
                recipient='Admin',
                title=f"Task Completed: {task_name}",
                message=f"All assigned employees completed task '{task_name}'.",
                notification_type='task_completed',
                reference_id=task_id
            )

        return True, overall_status

def delete_task_service(task_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM tasks WHERE id = %s", [task_id])
    return True

def bulk_delete_tasks_service(task_ids):
    if not task_ids:
        return True
    tasks_table()
    format_strings = ','.join(['%s'] * len(task_ids))
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM tasks WHERE id IN ({format_strings})", task_ids)
    return True

