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


def get_all_tasks_service():
    
    tasks_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, task_name, project_name, created_date, due_date, status, employee_name
            FROM tasks ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        
    tasks = []
    for index, row in enumerate(rows, start=1):
        tasks.append({
            's_no': index,
            'id': row[0],
            'task_name': row[1],
            'project_name': row[2],
            'created_date': row[3],
            'due_date': row[4],
            'status': row[5],
            'employee_name': row[6],
        })
    return tasks

def add_task_service(task_name, project_name, due_date, status, employee_name,created_date=None):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO tasks (task_name, project_name, due_date, status, employee_name,created_date)
            VALUES (%s, %s, %s, %s, %s,%s)
        """, [task_name, project_name, due_date, status, employee_name,created_date])
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

def update_task_service(task_id, task_name, project_name, due_date, status, employee_name, created_date=None):
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    if status == "In Progress" and not created_date:
        created_date = today_str
    
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE tasks
            SET task_name = %s, project_name = %s, created_date = %s, due_date = %s, status = %s, employee_name = %s
            WHERE id = %s
        """, [task_name, project_name, created_date, due_date, status, employee_name, task_id])

        if status.lower() == 'completed' :
            cursor.execute("SELECT employee_name, task_name FROM tasks WHERE id = %s", [task_id])
            row = cursor.fetchone()
            if row:
                employee_name = row[0]
                task_name = row[1]
                create_notification_service(
                    recipient=employee_name,
                    title=f"Task Completed: {task_name}",
                    message=f"{employee_name} has completed the task",
                    notification_type='task_completed',
                    reference_id=task_id
                )

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
