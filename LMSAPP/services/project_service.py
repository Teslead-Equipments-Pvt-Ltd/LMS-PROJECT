import datetime
from django.db import connection

def ensure_projects_table():
    """
    Ensures the 'projects' table exists in the database.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_name VARCHAR(200) NOT NULL,
                project_type VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Not Worked',
                created_date VARCHAR(50) DEFAULT NULL,
                completion_date VARCHAR(50) DEFAULT NULL,
                due_date VARCHAR(50) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

def get_all_projects_service():
    """
    
    """
    ensure_projects_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, project_name, project_type, status, created_date, completion_date, due_date
            FROM projects ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        
    projects = []
    for index, row in enumerate(rows, start=1):
        projects.append({
            's_no': index,
            'id': row[0],
            'project_name': row[1],
            'project_type': row[2],
            'status': row[3],
            'created_date': row[4] or '',
            'completion_date': row[5] or '',
            'due_date': row[6] or '',
        })
    return projects

def add_project_service(project_name, project_type, status, due_date):
    """
    Adds a new project into the 'projects' table.
    Automatically sets created_date if status is 'In Progress' or completion_date if status is 'Completed'.
    """
    ensure_projects_table()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    created_date = today_str if status == "In Progress" else ""
    completion_date = today_str if status == "Completed" else ""
    
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO projects (project_name, project_type, status, created_date, completion_date, due_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [project_name, project_type, status, created_date, completion_date, due_date or ''])
    return True

def update_project_service(project_id, project_name, project_type, status, created_date, completion_date, due_date):
    """
    Updates an existing project record in the 'projects' table.
    """
    ensure_projects_table()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # Auto logic if status changes
    if status == "In Progress" and not created_date:
        created_date = today_str
    if status == "Completed" and not completion_date:
        completion_date = today_str

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE projects
            SET project_name = %s, project_type = %s, status = %s, created_date = %s, completion_date = %s, due_date = %s
            WHERE id = %s
        """, [project_name, project_type, status, created_date, completion_date, due_date, project_id])
    return True

def delete_project_service(project_id):
    """
    Deletes a project record from the 'projects' table permanently.
    """
    ensure_projects_table()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM projects WHERE id = %s", [project_id])
    return True

def bulk_delete_projects_service(project_ids):
    """
    Deletes multiple project records from the 'projects' table permanently by IDs list.
    """
    if not project_ids:
        return True
    ensure_projects_table()
    format_strings = ','.join(['%s'] * len(project_ids))
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM projects WHERE id IN ({format_strings})", project_ids)
    return True
