from functools import wraps
from flask import session, redirect, url_for, flash, request
from database import db
import logging

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('access_page'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('access_page'))
            
            user_role = session.get('user_role')
            if user_role not in allowed_roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current user information from session"""
    if 'user_id' not in session:
        return None
    
    query = """
    SELECT e.employee_id, e.first_name, e.last_name, e.email, e.department, 
           e.role_title, e.manager_id, e.photo_blob
    FROM employee e
    JOIN user_accounts ua ON e.employee_id = ua.employee_id
    WHERE e.employee_id = %s AND e.status = 'active'
    """
    
    result = db.execute_query(query, (session['user_id'],))
    return result[0] if result else None

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    query = """
    SELECT ua.employee_id, ua.email, ua.password, e.first_name, e.last_name, 
           e.department, e.role_title, e.status
    FROM user_accounts ua
    JOIN employee e ON ua.employee_id = e.employee_id
    WHERE ua.email = %s AND e.status = 'active'
    """
    
    result = db.execute_query(query, (email,))
    
    if result and len(result) > 0:
        user = result[0]
        # Simple password check (in production, use hashed passwords)
        if user['password'] == password:
            return {
                'employee_id': user['employee_id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'department': user['department'],
                'role_title': user['role_title']
            }
    
    return None

def create_user_session(user_data):
    """Create user session after successful authentication"""
    session['user_id'] = user_data['employee_id']
    session['user_email'] = user_data['email']
    session['user_name'] = f"{user_data['first_name']} {user_data['last_name']}"
    session['user_role'] = user_data['department'].lower()
    session['user_department'] = user_data['department']
    session['user_title'] = user_data['role_title']

def clear_user_session():
    """Clear user session on logout"""
    session.clear()

def get_user_permissions(department):
    """Get user permissions based on department"""
    permissions = {
        'ceo': ['admin', 'hr', 'employee', 'it', 'career'],
        'cto': ['admin', 'hr', 'employee', 'it', 'career'],
        'manager': ['hr', 'employee', 'career'],
        'hr': ['hr', 'employee', 'career'],
        'it': ['it', 'employee', 'career'],
        'employee': ['employee', 'career']
    }
    
    return permissions.get(department.lower(), ['employee', 'career'])

def has_permission(required_permission):
    """Check if current user has required permission"""
    if 'user_role' not in session:
        return False
    
    user_permissions = get_user_permissions(session['user_role'])
    return required_permission in user_permissions