import os
import uuid
from werkzeug.utils import secure_filename
from config import Config
from datetime import datetime, timedelta
import jwt
import logging

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Generate a unique filename while preserving the extension"""
    if filename:
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
    return str(uuid.uuid4())

def generate_reset_token(email):
    """Generate a password reset token"""
    payload = {
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def verify_reset_token(token):
    """Verify and decode a password reset token"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload['email']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return ''

def calculate_work_days(start_date, end_date):
    """Calculate number of work days between two dates"""
    if not start_date or not end_date:
        return 0
    
    # Convert strings to datetime if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate total days
    total_days = (end_date - start_date).days + 1
    return max(0, total_days)

def get_employee_hierarchy(employee_id, db):
    """Get the organizational hierarchy for an employee"""
    hierarchy = []
    current_id = employee_id
    
    while current_id:
        query = """
        SELECT e.employee_id, e.first_name, e.last_name, e.role_title, 
               e.department, e.manager_id
        FROM employee e 
        WHERE e.employee_id = %s AND e.status = 'active'
        """
        result = db.execute_query(query, (current_id,))
        
        if result:
            employee = result[0]
            hierarchy.append(employee)
            current_id = employee['manager_id']
        else:
            break
    
    return hierarchy

def validate_timesheet_date(date_str):
    """Validate that timesheet date is not in the future"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return date_obj <= today
    except ValueError:
        return False

def calculate_comp_off_eligibility(employee_id, work_date, hours_worked, db):
    """Check if employee is eligible for comp-off based on weekend work"""
    try:
        work_date_obj = datetime.strptime(work_date, '%Y-%m-%d').date()
        
        # Check if it's weekend (Saturday = 5, Sunday = 6)
        if work_date_obj.weekday() not in [5, 6]:
            return False
        
        # Check if total hours >= 8 for the day
        if hours_worked >= 8:
            return True
            
        return False
    except ValueError:
        return False

def get_notification_count(employee_id, db):
    """Get count of unread notifications for an employee"""
    query = """
    SELECT COUNT(*) as count FROM notifications 
    WHERE employee_id = %s AND is_read = 0
    """
    result = db.execute_query(query, (employee_id,))
    return result[0]['count'] if result else 0

def log_user_activity(employee_id, action, details, db):
    """Log user activity for audit purposes"""
    query = """
    INSERT INTO user_activity_log (employee_id, action, details, timestamp)
    VALUES (%s, %s, %s, NOW())
    """
    db.execute_query(query, (employee_id, action, details))