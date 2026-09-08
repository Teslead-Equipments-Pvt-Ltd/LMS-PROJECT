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

def get_notifications_by_user(recipient=None, is_admin=False):
    """
    Fetches notifications. If admin, fetches all; otherwise fetches for the specific recipient.
    """
    ensure_notifications_table()
    with connection.cursor() as cursor:
        if is_admin:
            cursor.execute("""
                SELECT id, recipient, title, message, notification_type, reference_id, is_read, created_at
                FROM notifications
                ORDER BY created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT id, recipient, title, message, notification_type, reference_id, is_read, created_at
                FROM notifications
                WHERE recipient = %s
                ORDER BY created_at DESC
            """, [recipient])
        rows = cursor.fetchall()

    notifications = []
    for index, row in enumerate(rows, start=1):
        notifications.append({
            's_no': index,
            'id': row[0],
            'recipient': row[1],
            'title': row[2],
            'message': row[3],
            'notification_type': row[4],
            'reference_id': row[5],
            'is_read': bool(row[6]),
            'created_at': row[7].strftime("%Y-%m-%d %H:%M") if row[7] else ''
        })
    return notifications

# def mark_notification_as_read(notification_id):
#     """
#     Marks a notification as read.
#     """
#     with connection.cursor() as cursor:
#         cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = %s", [notification_id])
#     return True
