from django.db import connection

def ensure_notifications_table():
    """
    Creates the notifications table if it doesn't exist.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                recipient VARCHAR(200) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                notification_type VARCHAR(50) DEFAULT 'task_created',
                reference_id INT DEFAULT NULL,
                is_read TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

def create_notification_service(recipient, title, message, notification_type='task_created', reference_id=None):
    """
    Inserts a new notification into the notifications table.
    """
    ensure_notifications_table()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO notifications (recipient, title, message, notification_type, reference_id, is_read)
            VALUES (%s, %s, %s, %s, %s, 0)
        """, [recipient, title, message, notification_type, reference_id])
    return True

# def get_request_status_by_id(request_id):
#     """
#     Helper function to get the current status of a task request (Pending, Approved, Rejected).
#     """
#     if not request_id:
#         return None
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT status FROM task_requests WHERE id = %s", [request_id])
#             row = cursor.fetchone()
#             return row[0] if row else None
#     except Exception:
#         return None


def get_notifications_by_user(recipient=None, is_admin=False):
    """
    Fetches all notifications for Admin or for a specific employee.
    Deduplicates task_request notifications so that each task shows only once.
    """
    ensure_notifications_table()

    # Step 1: Decide who we are fetching notifications for
    target_user = 'Admin' if is_admin else recipient

    # Step 2: Fetch notifications with joined task_requests to get task_id and current status
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                n.id, 
                n.recipient, 
                n.title, 
                n.message, 
                n.notification_type, 
                n.reference_id, 
                n.is_read, 
                n.created_at,
                tr.task_id,
                tr.status AS request_status
            FROM notifications n
            LEFT JOIN task_requests tr ON n.notification_type = 'task_request' AND n.reference_id = tr.id
            WHERE n.recipient = %s
            ORDER BY n.created_at DESC
        """, [target_user])
        rows = cursor.fetchall()

    # Step 3: Loop through each row and deduplicate task_request notifications for the same task
    notifications = []
    seen_task_request_tasks = set()

    for row in rows:
        notif_type = row[4]
        ref_id = row[5]
        task_id = row[8]
        request_status = row[9]

        # For task requests, ensure each task shows only once (latest notification)
        if notif_type == 'task_request':
            dedup_key = task_id if task_id else f"ref_{ref_id}"
            if dedup_key in seen_task_request_tasks:
                continue
            seen_task_request_tasks.add(dedup_key)

        notifications.append({
            's_no': len(notifications) + 1,
            'id': row[0],
            'recipient': row[1],
            'title': row[2],
            'message': row[3],
            'notification_type': notif_type,
            'reference_id': ref_id,
            'is_read': bool(row[6]),
            'created_at': row[7].strftime("%Y-%m-%d %H:%M") if row[7] else '',
            'request_status': request_status
        })

    return notifications


