import json
from django.contrib import admin
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


def get_all_tasks_service():
    tasks_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, task_name, project_name, created_date, due_date, status, employee_name, employee_status
            FROM tasks ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        
    tasks = []
    for index, row in enumerate(rows, start=1):
        emp_names_str = row[6] 
        emp_status_raw = row[7]
        emp_status_dict = {}
        if emp_status_raw:
            try:
                emp_status_dict = json.loads(emp_status_raw)
            except Exception:
                emp_status_dict = {}

        assigned_list = [e.strip() for e in emp_names_str.split(',') if e.strip()]
        for emp in assigned_list:
            if emp not in emp_status_dict:
                emp_status_dict[emp] = row[5] or 'Not Worked'

        tasks.append({
            's_no': index,
            'id': row[0],
            'task_name': row[1],
            'project_name': row[2],
            'created_date': row[3],
            'due_date': row[4],
            'status': row[5],
            'employee_name': row[6],
            'employee_status': emp_status_dict,
            'employee_status_json': json.dumps(emp_status_dict)
        })
    return tasks

def add_task_service(task_name, project_name, due_date, status, employee_name, created_date=None):
    tasks_table()
    assigned_list = [e.strip() for e in (employee_name or '').split(',') if e.strip()]
    emp_status_dict = {emp: status for emp in assigned_list}
    emp_status_json = json.dumps(emp_status_dict)

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO tasks (task_name, project_name, due_date, status, employee_name, created_date, employee_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [task_name, project_name, due_date, status, employee_name, created_date, emp_status_json])
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

def update_task_service(task_id, task_name, project_name, due_date, status, employee_name, created_date=None, updated_by=None, user_role=None, employee_status=None):
    if status == "In Progress" and not created_date:
        created_date = datetime.date.today().strftime("%Y-%m-%d")

    tasks_table()
    with connection.cursor() as cursor:
        cursor.execute("SELECT status, employee_name, employee_status FROM tasks WHERE id = %s", [task_id])
        current_row = cursor.fetchone()

    current_status = current_row[0] if current_row else status
    current_emp_name = current_row[1] if current_row else employee_name
    current_emp_status_raw = current_row[2] if current_row else None

    existing_emp_status_dict = {}
    if current_emp_status_raw:
        try:
            existing_emp_status_dict = json.loads(current_emp_status_raw)
        except Exception:
            existing_emp_status_dict = {}

    assigned_list = [e.strip() for e in (employee_name or '').split(',') if e.strip()]

    if employee_status is not None:
        if isinstance(employee_status, str):
            try:
                emp_status_dict = json.loads(employee_status)
            except Exception:
                emp_status_dict = existing_emp_status_dict
        elif isinstance(employee_status, dict):
            emp_status_dict = employee_status
        else:
            emp_status_dict = existing_emp_status_dict
    else:
        emp_status_dict = {}
        for emp in assigned_list:
            if emp in existing_emp_status_dict:
            
                if status != current_status:
                    emp_status_dict[emp] = status
                else:
                    emp_status_dict[emp] = existing_emp_status_dict[emp]
            else:
                emp_status_dict[emp] = status

    statuses = list(emp_status_dict.values())
    if statuses:
        if all(s == 'Completed' for s in statuses):
            status = 'Completed'
        elif any(s in ['In Progress', 'InProgress', 'Completed'] for s in statuses):
            status = 'In Progress'
        elif any(s == 'On Hold' for s in statuses):
            status = 'On Hold'

    emp_status_json = json.dumps(emp_status_dict)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE tasks
            SET task_name = %s, project_name = %s, created_date = %s, due_date = %s, status = %s, employee_name = %s, employee_status = %s
            WHERE id = %s
        """, [task_name, project_name, created_date, due_date, status, employee_name, emp_status_json, task_id])

    return True


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

