from django.db import connection

def ensure_tasks_table():
    """
    Ensures the 'tasks' table exists in the database.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_name VARCHAR(200) NOT NULL,
                project_name VARCHAR(200) NOT NULL,
                due_date VARCHAR(50) DEFAULT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Not Worked',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

def get_all_tasks_service():
    """
    Fetches all tasks from the 'tasks' table.
    """
    ensure_tasks_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, task_name, project_name, due_date, status
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
            'due_date': row[3] or '',
            'status': row[4],
        })
    return tasks

def add_task_service(task_name, project_name, due_date, status):
    """
    Adds a new task into the 'tasks' table.
    """
    ensure_tasks_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO tasks (task_name, project_name, due_date, status)
            VALUES (%s, %s, %s, %s)
        """, [task_name, project_name, due_date or '', status or 'Not Worked'])
    return True

def update_task_service(task_id, task_name, project_name, due_date, status):
    """
    Updates an existing task in the 'tasks' table.
    """
    ensure_tasks_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE tasks
            SET task_name = %s, project_name = %s, due_date = %s, status = %s
            WHERE id = %s
        """, [task_name, project_name, due_date, status, task_id])
    return True

def delete_task_service(task_id):
    """
    Deletes a task from the 'tasks' table.
    """
    ensure_tasks_table()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM tasks WHERE id = %s", [task_id])
    return True

def bulk_delete_tasks_service(task_ids):
    """
    Deletes multiple tasks from the 'tasks' table by IDs list.
    """
    if not task_ids:
        return True
    ensure_tasks_table()
    format_strings = ','.join(['%s'] * len(task_ids))
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM tasks WHERE id IN ({format_strings})", task_ids)
    return True
