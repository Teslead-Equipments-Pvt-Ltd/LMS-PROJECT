import datetime
from django.db import connection

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

def add_task_service(task_name, project_name, due_date, status, employee_name, created_date=None):
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    if not created_date and status == "In Progress":
        created_date = today_str

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO tasks (task_name, project_name, created_date, due_date, status, employee_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [task_name, project_name, created_date, due_date, status, employee_name])
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
