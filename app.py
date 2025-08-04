# -*- coding: utf-8 -*-

from flask import Flask, request, Response, stream_with_context, render_template, redirect, url_for, session, flash
import requests, json
import psycopg2
from flask_cors import CORS
from werkzeug.security import check_password_hash
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode
from itsdangerous import URLSafeTimedSerializer


app = Flask(__name__)
app.secret_key = '2169ae279691918b3b5c54641f2efb9e17de8ac4e4722e376ea6475085828918'
CORS(app)

s = URLSafeTimedSerializer(app.secret_key)

# 🔐 OAuth Setup
oauth = OAuth(app)
 

# Google OAuth
oauth.register(
    name='google',
    client_id='1015957394002-k2nebl44o2p82ige6dgpc125gepc7ntn.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


# Microsoft OAuth
oauth.register(
    name='microsoft',
    client_id='YOUR_MICROSOFT_CLIENT_ID',
    client_secret='YOUR_MICROSOFT_CLIENT_SECRET',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    api_base_url='https://graph.microsoft.com/v1.0/',
    client_kwargs={'scope': 'User.Read openid email profile'},
)

# 🔁 Auth Routes
@app.route('/login/<provider>')
def login(provider):
    redirect_uri = url_for('authorize', provider=provider, _external=True)
    return oauth.create_client(provider).authorize_redirect(redirect_uri)


@app.route('/authorize/<provider>')
def authorize(provider):
    client = oauth.create_client(provider)
    token = client.authorize_access_token()
    user_info = client.userinfo()


    email = user_info.get('email')

    # ✅ Check if Gmail exists in `gmail_users` table
    try:
        conn = psycopg2.connect(
            dbname="NexIQon",
            user="sanjay",
            password="",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT gmail FROM gmail_users WHERE gmail = %s", (email,))
        result = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('signin'))

    if not result:
        flash("Access denied: your Gmail is not authorized", "error")
        return redirect(url_for('signin'))

    # ✅ Success: login
    session['user'] = {
        'email': email
    }
    session['user_role'] = 'employee'  # Optional
    return redirect(url_for('access_page'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# 📄 Routes
@app.route('/')
def home():
    return render_template('home.html')

import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="quadprserver.mysql.database.azure.com",
        user="adminuser",
        password="Quad@2025",
        database="nexiqon",
        port=3306

    )

conn = get_db_connection()
cur = conn.cursor(dictionary=True)  # 👈 this is what enables dict access

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Mail, Message

import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import logging

# Import our custom modules
from config import Config
from database import db
from azure_storage import azure_storage
from auth import (login_required, role_required, authenticate_user, 
                 create_user_session, clear_user_session, get_current_user, has_permission)
from utils import (allowed_file, generate_unique_filename, calculate_work_days,
                  get_employee_hierarchy, validate_timesheet_date, 
                  calculate_comp_off_eligibility, get_notification_count)

# Configure logging
logging.basicConfig(level=logging.INFO)
# Following routes are for the induction kit file - Samvedha
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)

# Initialize Flask-Mail
mail = Mail(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# I think it might be because I used the following line instead of line 11.
# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/access')
def access_page():
    return render_template('access.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('access.html')
        
        user = authenticate_user(email, password)
        if user:
            create_user_session(user)
            
            # Redirect based on user role
            role = user['department'].lower()
            if role in ['ceo', 'cto']:
                return redirect(url_for('admin_dashboard'))
            elif role == 'hr':
                return redirect(url_for('hr_portal'))
            elif role == 'it':
                return redirect(url_for('it_portal'))
            else:
                return redirect(url_for('employee_portal'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('access.html')

@app.route('/logout')
@login_required
def logout():
    clear_user_session()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@app.route('/admin-dashboard')
@login_required
@role_required(['CEO', 'CTO'])
def admin_dashboard():
    user = get_current_user()
    return render_template('admin_dashboard.html', user_name=user['first_name'] + ' ' + user['last_name'])

@app.route('/employee-portal')
@login_required
def employee_portal():
    user = get_current_user()
    return render_template('employee_portal.html', 
                         user_name=user['first_name'] + ' ' + user['last_name'],
                         user_role=user['role_title'],
                         user_email=user['email'],
                         user_department=user['department'])

@app.route('/hr-portal')
@login_required
@role_required(['HR', 'Manager', 'CEO', 'CTO'])
def hr_portal():
    user = get_current_user()
    return render_template('hr_portal.html', user_name=user['first_name'] + ' ' + user['last_name'])

@app.route('/it-portal')
@login_required
@role_required(['IT', 'CEO', 'CTO'])
def it_portal():
    user = get_current_user()
    return render_template('it_portal.html', user_name=user['first_name'] + ' ' + user['last_name'])

@app.route('/career-portal')
@login_required
def career_portal():
    user = get_current_user()
    return render_template('career_portal.html', user_name=user['first_name'] + ' ' + user['last_name'])

# ============================================================================
# EMPLOYEE PORTAL API ROUTES
# ============================================================================

@app.route('/api/employee/profile')
@login_required
def get_employee_profile():
    user_id = session['user_id']
    query = """
    SELECT employee_id, first_name, last_name, email, contact_number, 
           department, role_title, location, leaves_sick, leaves_personal, 
           comp_off, joined_date
    FROM employee 
    WHERE employee_id = %s AND status = 'active'
    """
    
    result = db.execute_query(query, (user_id,))
    if result:
        profile = result[0]
        # Format joined_date
        if profile['joined_date']:
            profile['joined_date'] = profile['joined_date'].strftime('%Y-%m-%d')
        return jsonify({'profile': profile})
    
    return jsonify({'error': 'Profile not found'}), 404

@app.route('/api/employee/my-tickets')
@login_required
def get_my_tickets():
    user_id = session['user_id']
    query = """
    SELECT ticket_id, department, description as subject, description, 
           severity_level as severity, status, submitted_on as created_date
    FROM tickets 
    WHERE employee_id = %s 
    ORDER BY submitted_on DESC
    """
    
    result = db.execute_query(query, (user_id,))
    tickets = []
    
    if result:
        for ticket in result:
            tickets.append({
                'ticket_id': ticket['ticket_id'],
                'subject': ticket['subject'][:50] + '...' if len(ticket['subject']) > 50 else ticket['subject'],
                'description': ticket['description'],
                'department': ticket['department'],
                'severity': f"Level {ticket['severity']}",
                'status': ticket['status'],
                'created_date': ticket['created_date'].strftime('%Y-%m-%d %H:%M')
            })
    
    return jsonify({'tickets': tickets})

@app.route('/employee/submit-ticket', methods=['POST'])
@login_required
def submit_employee_ticket():
    user_id = session['user_id']
    user = get_current_user()
    
    department = request.form.get('department')
    severity = request.form.get('severity')
    subject = request.form.get('subject')
    description = request.form.get('description')
    women_safety = 1 if request.form.get('women_safety') else 0
    
    if not all([department, severity, subject, description]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('employee_portal'))
    
    # Map severity to level
    severity_map = {'Low': '1', 'Medium': '2', 'High': '3', 'Critical': '3'}
    severity_level = severity_map.get(severity, '2')
    
    query = """
    INSERT INTO tickets (employee_id, email, department, gender, women_safety, 
                        description, severity_level, status, submitted_on)
    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Open', NOW())
    """
    
    # Get user gender from employee table
    gender_query = "SELECT gender FROM employee WHERE employee_id = %s"
    gender_result = db.execute_query(gender_query, (user_id,))
    gender = gender_result[0]['gender'] if gender_result else 'Other'
    
    full_description = f"Subject: {subject}\n\nDescription: {description}"
    
    result = db.execute_query(query, (
        user_id, user['email'], department, gender, women_safety,
        full_description, severity_level
    ))
    
    if result:
        flash('Ticket submitted successfully!', 'success')
    else:
        flash('Error submitting ticket. Please try again.', 'error')
    
    return redirect(url_for('employee_portal'))

@app.route('/employee/submit-feedback', methods=['POST'])
@login_required
def submit_employee_feedback():
    user_id = session['user_id']
    
    feedback_type = request.form.get('feedback_type')
    target_role = request.form.get('target_role')
    feedback_text = request.form.get('feedback_text')
    
    if not all([feedback_type, feedback_text]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('employee_portal'))
    
    # For anonymous feedback, we'll store it in a feedback table
    query = """
    INSERT INTO anonymous_feedback (employee_id, feedback_type, target_role, 
                                  feedback_text, submitted_on)
    VALUES (%s, %s, %s, %s, NOW())
    """
    
    result = db.execute_query(query, (user_id, feedback_type, target_role, feedback_text))
    
    if result:
        flash('Feedback submitted successfully!', 'success')
    else:
        flash('Error submitting feedback. Please try again.', 'error')
    
    return redirect(url_for('employee_portal'))

@app.route('/employee/submit-timesheet', methods=['POST'])
@login_required
def submit_timesheet():
    user_id = session['user_id']
    
    # Get form data
    week_start = request.form.get('week_start')
    project_id = request.form.get('project_id')
    work_description = request.form.get('work_description')
    
    # Get hours for each day
    hours_data = {
        'hours_mon': float(request.form.get('hours_mon', 0) or 0),
        'hours_tue': float(request.form.get('hours_tue', 0) or 0),
        'hours_wed': float(request.form.get('hours_wed', 0) or 0),
        'hours_thu': float(request.form.get('hours_thu', 0) or 0),
        'hours_fri': float(request.form.get('hours_fri', 0) or 0),
        'hours_sat': float(request.form.get('hours_sat', 0) or 0),
        'hours_sun': float(request.form.get('hours_sun', 0) or 0)
    }
    
    if not week_start:
        flash('Please select a week start date.', 'error')
        return redirect(url_for('employee_portal'))
    
    # Calculate dates for the week
    start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
    
    # Insert timesheet entries for each day
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    for i, day in enumerate(days):
        hours = hours_data[f'hours_{day}']
        if hours > 0:
            work_date = start_date + timedelta(days=i)
            
            # Validate date is not in future
            if not validate_timesheet_date(work_date.strftime('%Y-%m-%d')):
                flash(f'Cannot submit timesheet for future dates: {work_date}', 'error')
                return redirect(url_for('employee_portal'))
            
            query = """
            INSERT INTO timesheet (employee_id, project_id, work_date, hours_logged, description)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            hours_logged = VALUES(hours_logged), 
            description = VALUES(description)
            """
            
            db.execute_query(query, (user_id, project_id, work_date, hours, work_description))
            
            # Check for comp-off eligibility
            if calculate_comp_off_eligibility(user_id, work_date.strftime('%Y-%m-%d'), hours, db):
                comp_query = """
                INSERT INTO comp_off_log (employee_id, work_date, hours_worked, status)
                VALUES (%s, %s, %s, 'pending')
                """
                db.execute_query(comp_query, (user_id, work_date, hours))
    
    flash('Timesheet submitted successfully!', 'success')
    return redirect(url_for('employee_portal'))

# ============================================================================
# LEAVE MANAGEMENT ROUTES
# ============================================================================

@app.route('/submit-leave', methods=['POST'])
@login_required
def submit_leave():
    user_id = session['user_id']
    
    leave_type = request.form.get('leave_type')
    sub_type = request.form.get('sub_type')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    reason = request.form.get('reason')
    
    if not all([leave_type, start_date, end_date, reason]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('employee_portal'))
    
    # Validate dates
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_dt > end_dt:
            flash('Start date cannot be after end date.', 'error')
            return redirect(url_for('employee_portal'))
        
        if start_dt < datetime.now().date():
            flash('Cannot apply for leave in the past.', 'error')
            return redirect(url_for('employee_portal'))
            
    except ValueError:
        flash('Invalid date format.', 'error')
        return redirect(url_for('employee_portal'))
    
    query = """
    INSERT INTO leave_requests (employee_id, leave_type, sub_type, start_date, 
                               end_date, reason, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, 'Pending', NOW())
    """
    
    result = db.execute_query(query, (user_id, leave_type, sub_type, start_date, end_date, reason))
    
    if result:
        # Get the inserted leave request for confirmation
        leave_query = """
        SELECT * FROM leave_requests 
        WHERE employee_id = %s 
        ORDER BY created_at DESC 
        LIMIT 1
        """
        leave_result = db.execute_query(leave_query, (user_id,))
        
        if leave_result:
            leave_request = leave_result[0]
            return render_template('leave_confirmation.html', leave_request=leave_request)
    
    flash('Error submitting leave request. Please try again.', 'error')
    return redirect(url_for('employee_portal'))

@app.route('/leave-status')
@login_required
def leave_status():
    user_id = session['user_id']
    
    query = """
    SELECT leave_id, leave_type, sub_type, start_date, end_date, total_days,
           reason, status, rejection_reason, created_at
    FROM leave_requests 
    WHERE employee_id = %s 
    ORDER BY created_at DESC
    """
    
    result = db.execute_query(query, (user_id,))
    leave_requests = result if result else []
    
    return render_template('leave_status.html', leave_requests=leave_requests)

# ============================================================================
# HR PORTAL API ROUTES
# ============================================================================

@app.route('/api/hr/dashboard-stats')
@login_required
@role_required(['HR', 'Manager', 'CEO', 'CTO'])
def hr_dashboard_stats():
    # Get total employees
    total_employees_query = "SELECT COUNT(*) as count FROM employee WHERE status = 'active'"
    total_employees = db.execute_query(total_employees_query)[0]['count']
    
    # Get pending leaves
    pending_leaves_query = "SELECT COUNT(*) as count FROM leave_requests WHERE status = 'Pending'"
    pending_leaves = db.execute_query(pending_leaves_query)[0]['count']
    
    # Get pending timesheets (assuming we need approval)
    pending_timesheets_query = """
    SELECT COUNT(DISTINCT employee_id) as count FROM timesheet 
    WHERE work_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    """
    pending_timesheets = db.execute_query(pending_timesheets_query)[0]['count']
    
    # Get active job postings
    active_jobs_query = "SELECT COUNT(*) as count FROM job_postings"
    active_jobs = db.execute_query(active_jobs_query)[0]['count']
    
    return jsonify({
        'total_employees': total_employees,
        'pending_leaves': pending_leaves,
        'pending_timesheets': pending_timesheets,
        'active_jobs': active_jobs
    })

@app.route('/api/hr/employees')
@login_required
@role_required(['HR', 'Manager', 'CEO', 'CTO'])
def get_employees():
    query = """
    SELECT employee_id, first_name, last_name, email, department, role_title, 
           contact_number, location, status
    FROM employee 
    WHERE status = 'active'
    ORDER BY first_name, last_name
    """
    
    result = db.execute_query(query)
    employees = result if result else []
    
    return jsonify({'employees': employees})

@app.route('/hr/add-employee', methods=['POST'])
@login_required
@role_required(['HR', 'Manager', 'CEO', 'CTO'])
def add_employee():
    # Get form data
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    contact_number = request.form.get('contact_number')
    department = request.form.get('department')
    role_title = request.form.get('role_title')
    salary = request.form.get('salary')
    location = request.form.get('location')
    
    if not all([first_name, last_name, email, contact_number, department, role_title, salary, location]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('hr_portal'))
    
    # Check if email already exists
    check_query = "SELECT employee_id FROM employee WHERE email = %s"
    existing = db.execute_query(check_query, (email,))
    
    if existing:
        flash('Employee with this email already exists.', 'error')
        return redirect(url_for('hr_portal'))
    
    # Insert new employee
    insert_query = """
    INSERT INTO employee (first_name, last_name, email, contact_number, department, 
                         role_title, salary, location, status, joined_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', NOW())
    """
    
    result = db.execute_query(insert_query, (
        first_name, last_name, email, contact_number, department, 
        role_title, salary, location
    ))
    
    if result:
        # Get the new employee ID
        employee_id_query = "SELECT LAST_INSERT_ID() as employee_id"
        employee_id_result = db.execute_query(employee_id_query)
        employee_id = employee_id_result[0]['employee_id']
        
        # Create user account with temporary password
        temp_password = f"{first_name}@123"
        user_account_query = """
        INSERT INTO user_accounts (employee_id, email, password, is_temp_password)
        VALUES (%s, %s, %s, 1)
        """
        db.execute_query(user_account_query, (employee_id, email, temp_password))
        
        flash(f'Employee added successfully! Temporary password: {temp_password}', 'success')
    else:
        flash('Error adding employee. Please try again.', 'error')
    
    return redirect(url_for('hr_portal'))

# ============================================================================
# CAREER PORTAL API ROUTES
# ============================================================================

@app.route('/api/career/courses')
@login_required
def get_courses():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = """
    SELECT c.course_id, c.course_name, c.description, c.skill_category, 
           c.difficulty_level, c.duration_hours, c.passing_score,
           b.badge_name
    FROM course_catalog c
    LEFT JOIN badge_catalog b ON c.badge_id = b.badge_id
    WHERE c.is_active = 1
    """
    params = []
    
    if search:
        query += " AND (c.course_name LIKE %s OR c.description LIKE %s OR c.skill_category LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    if category:
        query += " AND c.skill_category = %s"
        params.append(category)
    
    query += " ORDER BY c.course_name"
    
    courses = db.execute_query(query, params) if params else db.execute_query(query)
    
    # Get unique categories
    categories_query = "SELECT DISTINCT skill_category FROM course_catalog WHERE is_active = 1"
    categories_result = db.execute_query(categories_query)
    categories = [cat['skill_category'] for cat in categories_result] if categories_result else []
    
    # Add attempt information for current user
    user_id = session['user_id']
    if courses:
        for course in courses:
            attempts_query = """
            SELECT COUNT(*) as total_attempts, MAX(score) as best_score,
                   MAX(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as has_passed
            FROM course_attempts 
            WHERE employee_id = %s AND course_id = %s
            """
            attempts = db.execute_query(attempts_query, (user_id, course['course_id']))
            if attempts:
                course.update(attempts[0])
            else:
                course.update({'total_attempts': 0, 'best_score': None, 'has_passed': 0})
    
    return jsonify({
        'courses': courses or [],
        'categories': categories
    })

@app.route('/api/career/course/<int:course_id>')
@login_required
def get_course_details(course_id):
    user_id = session['user_id']
    
    # Get course details
    course_query = """
    SELECT c.course_id, c.course_name, c.description, c.skill_category, 
           c.difficulty_level, c.duration_hours, c.passing_score,
           b.badge_name
    FROM course_catalog c
    LEFT JOIN badge_catalog b ON c.badge_id = b.badge_id
    WHERE c.course_id = %s AND c.is_active = 1
    """
    
    course_result = db.execute_query(course_query, (course_id,))
    if not course_result:
        return jsonify({'error': 'Course not found'}), 404
    
    course = course_result[0]
    
    # Get user's attempts
    attempts_query = """
    SELECT attempt_id, score, passed, attempt_date
    FROM course_attempts 
    WHERE employee_id = %s AND course_id = %s
    ORDER BY attempt_date DESC
    """
    attempts = db.execute_query(attempts_query, (user_id, course_id)) or []
    
    # Format attempt dates
    for attempt in attempts:
        attempt['attempt_date'] = attempt['attempt_date'].strftime('%Y-%m-%d %H:%M')
    
    # Check if user has earned the badge
    has_badge = False
    if course['badge_name']:
        badge_query = """
        SELECT 1 FROM employee_badges eb
        JOIN badge_catalog bc ON eb.badge_id = bc.badge_id
        WHERE eb.employee_id = %s AND bc.badge_name = %s
        """
        badge_result = db.execute_query(badge_query, (user_id, course['badge_name']))
        has_badge = bool(badge_result)
    
    return jsonify({
        'course': course,
        'attempts': attempts,
        'has_badge': has_badge
    })

@app.route('/api/career/course/<int:course_id>/start-exam')
@login_required
def start_exam(course_id):
    # Get course details
    course_query = """
    SELECT course_name, passing_score FROM course_catalog 
    WHERE course_id = %s AND is_active = 1
    """
    course_result = db.execute_query(course_query, (course_id,))
    
    if not course_result:
        return jsonify({'error': 'Course not found'}), 404
    
    course = course_result[0]
    
    # Get random 20 questions for the exam
    questions_query = """
    SELECT question_id, question_text, option_a, option_b, option_c, option_d
    FROM course_questions 
    WHERE course_id = %s 
    ORDER BY RAND() 
    LIMIT 20
    """
    questions = db.execute_query(questions_query, (course_id,))
    
    if not questions or len(questions) < 20:
        return jsonify({'error': 'Not enough questions available for this course'}), 400
    
    return jsonify({
        'course_name': course['course_name'],
        'passing_score': course['passing_score'],
        'total_questions': len(questions),
        'questions': questions
    })

@app.route('/api/career/course/<int:course_id>/submit-exam', methods=['POST'])
@login_required
def submit_exam(course_id):
    user_id = session['user_id']
    answers = request.json.get('answers', {})
    
    if not answers:
        return jsonify({'error': 'No answers provided'}), 400
    
    # Get correct answers
    question_ids = list(answers.keys())
    if not question_ids:
        return jsonify({'error': 'No valid answers provided'}), 400
    
    placeholders = ','.join(['%s'] * len(question_ids))
    correct_answers_query = f"""
    SELECT question_id, correct_answer 
    FROM course_questions 
    WHERE question_id IN ({placeholders})
    """
    
    correct_answers_result = db.execute_query(correct_answers_query, question_ids)
    correct_answers = {str(row['question_id']): row['correct_answer'] for row in correct_answers_result}
    
    # Calculate score
    total_questions = len(correct_answers)
    correct_count = 0
    
    for question_id, user_answer in answers.items():
        if correct_answers.get(question_id) == user_answer:
            correct_count += 1
    
    score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    # Get course passing score
    course_query = "SELECT passing_score, badge_id FROM course_catalog WHERE course_id = %s"
    course_result = db.execute_query(course_query, (course_id,))
    
    if not course_result:
        return jsonify({'error': 'Course not found'}), 404
    
    course = course_result[0]
    passed = score >= course['passing_score']
    
    # Save attempt
    attempt_query = """
    INSERT INTO course_attempts (employee_id, course_id, score, total_questions, 
                                passed, answers_json, attempt_date)
    VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """
    
    db.execute_query(attempt_query, (
        user_id, course_id, score, total_questions, passed, json.dumps(answers)
    ))
    
    # Award badge if passed and badge exists
    badge_awarded = False
    if passed and course['badge_id']:
        # Check if user already has this badge
        existing_badge_query = """
        SELECT 1 FROM employee_badges 
        WHERE employee_id = %s AND badge_id = %s
        """
        existing_badge = db.execute_query(existing_badge_query, (user_id, course['badge_id']))
        
        if not existing_badge:
            badge_query = """
            INSERT INTO employee_badges (employee_id, badge_id, awarded_on)
            VALUES (%s, %s, CURDATE())
            """
            db.execute_query(badge_query, (user_id, course['badge_id']))
            badge_awarded = True
    
    return jsonify({
        'score': score,
        'correct_answers': correct_count,
        'total_questions': total_questions,
        'passing_score': course['passing_score'],
        'passed': passed,
        'badge_awarded': badge_awarded
    })

# ============================================================================
# INDUCTION ROUTES (keeping existing functionality)
# ============================================================================

@app.route('/induction')
@login_required
def induction_kit():
    return render_template('induction.html')

@app.route('/induction/company-overview')
@login_required
def company_overview():
    return render_template('company-overview.html')

@app.route('/induction/code-of-conduct')
@login_required
def code_of_conduct():
    return render_template('code-of-conduct.html')

@app.route('/induction/it-security')
@login_required
def it_security():
    return render_template('it-security.html')

@app.route('/induction/work-schedule-attendance')
@login_required
def work_schedule_attendance():
    return render_template('work-schedule-attendance.html')

# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/read-more')
def read_more():
    return render_template('readmore.html')

@app.route('/contact-submit', methods=['POST'])
def contact_submit():
    # Handle contact form submission
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    
    # Here you would typically save to database or send email
    # For now, just flash a success message
    flash('Thank you for your message! We will get back to you soon.', 'success')
    return redirect(url_for('home'))

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# End of routes for the induction kit file - Samvedha


@app.route('/readmore')
def read_more():
    return render_template('readmore.html')

@app.route('/services/ai-ml')
def ai_ml():
    return render_template('ai_ml.html')

@app.route('/services/application-services')
def application_services():
    return render_template('application_services.html')

@app.route('/services/cloud-services')
def cloud_services():
    return render_template('cloud_services.html')

@app.route('/services/data-analytics')
def data_analytics():
    return render_template('data_analytics.html')

@app.route('/services/devsecops')
def devsecops():
    return render_template('devsecops.html')

@app.route('/contact-submit', methods=['POST'])
def contact_submit():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    message = request.form['message']
    consent = 'consent' in request.form

    # Store or send the message here
    return redirect(url_for('home'))  # or show a success page


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT ua.account_id, ua.email, ua.employee_id, e.first_name, e.last_name, 
                   e.department, e.role_title
            FROM user_accounts ua
            JOIN employee e ON ua.employee_id = e.employee_id
            WHERE ua.email = %s AND ua.password = %s
        """, (email, password))

        user = cur.fetchone()

        if user:
            session['user'] = {
                'account_id': user['account_id'],
                'employee_id': user['employee_id'],
                'email': user['email'],
                'name': f"{user['first_name']} {user['last_name']}",
                'department': user['department'],
                'role_title': user['role_title']
            }

            flash("Logged in successfully!", "success")

            # Accurate Redirection based on DB fields
            if user['role_title'].lower() == 'admin' or user['department'].upper() == 'CEO':
                return redirect(url_for('admin_dashboard'))

            elif user['department'] in ['HR', 'Manager']:
                return redirect(url_for('hr_portal'))

            elif user['department'] == 'IT':
                return redirect(url_for('it_portal'))

            else:
                return redirect(url_for('employee_portal'))
        else:
            flash('Incorrect credentials or account not found.', 'error')

        cur.close()
        conn.close()
        return render_template('access.html')  # Render access.html for consistency
    return render_template('access.html')  # Render access.html for GET requests

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('signin'))
    return f"<h1>Hello, {session['user']['name']} 👋 Welcome to the NexIQon Portal</h1>"

@app.route('/access')
def access_page():
    if 'user' not in session:
        flash("Please sign in first", "error")
        return redirect(url_for('signin'))
    return render_template('access.html')

from functools import wraps  # Helps preserve function info

def login_required(f):  # This wraps your route function like leave_form()
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:  # 🔐 Check: Is user logged in?
            flash("You need to sign in to access this page.", "error")
            return redirect(url_for('signin'))  # 🚪 Redirect to login
        return f(*args, **kwargs)  # ✅ Else continue to the real route
    return decorated_function


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = get_user_by_email(email)

        if user:
            token = s.dumps(email, salt='password-reset-salt')
            reset_link = url_for('reset_password', token=token, _external=True)

            # Simulate sending email
            print(f"[Simulated Email] Reset link for {email}: {reset_link}")

            flash('A password reset link has been generated and logged to the console.', 'success')

        else:
            flash('Email not found in our records.', 'error')

        # 🔁 IMPORTANT: redirect back to the form (GET request)
        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')



@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Try to decode the token with a max age of 30 minutes
        email = s.loads(token, salt='password-reset-salt', max_age=1800)  # 30 mins

        if request.method == 'POST':
            new_password = request.form['password']

            # Update the user's password in PostgreSQL
            try:
                conn = psycopg2.connect(
                    dbname="NexIQon",
                    user="sanjay",
                    password="",  # 🔁 Update if necessary
                    host="localhost",
                    port="5432"
                )
                cur = conn.cursor()
                cur.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
                conn.commit()
                cur.close()
                conn.close()

                flash('Your password has been reset successfully. Please log in.', 'success')
                return redirect(url_for('signin'))

            except Exception as e:
                flash(f"Error updating password: {e}", 'error')

        return render_template('reset_password.html', token=token)

    except SignatureExpired:
        return "<h1>Reset link has expired.</h1>", 403
    except BadSignature:
        return "<h1>Invalid reset token.</h1>", 403


def get_user_by_email(email):
    try:
        conn = psycopg2.connect(
            dbname="NexIQon",
            user="sanjay",
            password="",  # 🔒 Add password if needed
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()  # tuple like (id, email, password, ...)
        cur.close()
        conn.close()
        return user
    except Exception as e:
        print(f"Database error: {e}")
        return None

@app.route('/employee-dashboard')
def employee_dashboard():
    if 'user' not in session or session['user'].get('role') != 'employee':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('employee_login'))

    return render_template('employee_dashboard.html')


@app.route('/employee_leave_form')
def employee_leave_form():
    return render_template('employee_leave_form.html')

@app.route('/hr_leave_requests')
def hr_leave_requests():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    manager_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Fetch all pending leave requests assigned to this manager
    cur.execute("""
        SELECT lr.leave_id, e.first_name, e.last_name,
               lr.leave_type, lr.sub_type, lr.start_date, lr.end_date, lr.total_days,
               lr.reason, lr.status, lr.rejection_reason, lr.created_at
        FROM leave_requests lr
        JOIN employee e ON lr.employee_id = e.employee_id
        WHERE lr.approved_by = %s AND lr.status = 'Pending'
        ORDER BY lr.created_at DESC
    """, (manager_id,))

    requests = cur.fetchall()
    conn.close()
    return render_template("hr_leave_requests.html", leave_requests=requests)



@app.route('/submit_leave', methods=['POST'])
def submit_leave():
    if 'user' not in session:
        flash("Please sign in first", "error")
        return redirect(url_for('signin'))

    data = request.form
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO leave_requests (employee_id, leave_type, sub_type, start_date, end_date, reason)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cur.execute(query, (
        session['user']['employee_id'],
        data['leave_type'],
        data.get('sub_type'),
        data['start_date'],
        data['end_date'],
        data['reason']
    ))

    conn.commit()
    cur.close()
    conn.close()

    flash("Leave submitted successfully", "success")
    return redirect(url_for('leave_status'))


@app.route('/leave_status')
def leave_status():
    if 'user' not in session:
        flash("Please sign in first", "error")
        return redirect(url_for('signin'))

    employee_id = session['user']['employee_id']
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT leave_type, sub_type, start_date, end_date, total_days, reason, status, rejection_reason, created_at
    FROM leave_requests
    WHERE employee_id = %s
    ORDER BY created_at DESC
    """

    cur.execute(query, (employee_id,))
    leaves = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('leave_status.html', leave_history=leaves)


@app.route('/update-leave-status', methods=['POST'])
def update_leave_status():
    leave_id = request.form['leave_id']
    status = request.form['status']
    rejection_reason = request.form.get('rejection_reason') if status == 'Rejected' else None

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE leave_requests
        SET status = %s, rejection_reason = %s
        WHERE leave_id = %s
    """, (status, rejection_reason, leave_id))

    conn.commit()
    conn.close()

    flash("Leave request updated successfully!", "success")
    return redirect('/hr_leave_requests')

@app.route('/hr/feedback', methods=['GET', 'POST'])
def hr_feedback():
    if 'user' not in session or session['user'].get('role') != 'hr':
        return redirect(url_for('signin'))

    conn = psycopg2.connect(
        dbname="NexIQon",
        user="sanjay",
        password="",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    if request.method == 'POST':
        feedback_id = request.form['feedback_id']
        response = request.form['response']
        cur.execute("""
    UPDATE feedback
    SET hr_response = %s
    WHERE id = %s
""", (response, feedback_id))

        conn.commit()

    # ✅ Use correct column names here
    cur.execute("SELECT id, message, hr_response, submitted_at, hr_responded_at FROM feedback")

    feedback_entries = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("hr_feedback.html", feedbacks=feedback_entries)


@app.route('/feedback-responses')
def feedback_responses():
    conn = psycopg2.connect(
        dbname="NexIQon",
        user="sanjay",
        password="",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT message, response, responded_at FROM feedback WHERE response IS NOT NULL ORDER BY responded_at DESC")
    feedback_rows = cur.fetchall()
    cur.close()
    conn.close()

    # Pass as list of dicts for easy access
    responses = [{
        "message": msg,
        "response": resp,
        "responded_at": ts
    } for msg, resp, ts in feedback_rows]

    return render_template("feedback_responses.html", responses=responses)

@app.route('/performance-feedback')
def performance_feedback():
    return render_template('performance_feedback.html')

@app.route('/onboarding-tracker')
def onboarding_tracker():
    return render_template('onboarding_tracker.html')

# HR-specific logout route
@app.route('/hr-logout')
def hr_logout():
    session.clear()
    flash('HR has been logged out successfully.', 'success')
    return redirect('/hr-login')


@app.route('/unified-login', methods=['GET', 'POST'])
def unified_login():
    if request.method == 'GET':
        return redirect(url_for('access_page'))
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Please provide both email and password', 'error')
        return redirect(url_for('access_page'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Get user account and employee details
        cur.execute("""
            SELECT ua.account_id, ua.employee_id, ua.email, ua.password, ua.is_temp_password,
                   e.first_name, e.last_name, e.department, e.role_title, e.manager_id, e.photo_blob
            FROM user_accounts ua
            JOIN employee e ON ua.employee_id = e.employee_id
            WHERE ua.email = %s AND e.status = 'active'
        """, (email,))
        
        user = cur.fetchone()
        conn.close()
        
        if not user:
            flash('Invalid email or password', 'error')
            return redirect(url_for('access_page'))
        
        # Simple password check (in production, use proper hashing)
        if user['password'] != password:
            flash('Invalid email or password', 'error')
            return redirect(url_for('access_page'))
        
        # Set session data
        session['user_id'] = user['employee_id']
        session['user_email'] = user['email']
        session['user_name'] = f"{user['first_name']} {user['last_name']}"
        session['user_department'] = user['department']
        session['user_role'] = user['role_title']
        session['manager_id'] = user['manager_id']
        session['is_temp_password'] = user['is_temp_password']
        
        # Role-based redirection
        department = user['department'].upper()
        
        if department == 'CEO':
            # Admin access - redirect to admin dashboard with all modules
            return redirect(url_for('admin_dashboard'))
        elif department in ['HR', 'MANAGER']:
            # HR/Manager access - redirect to HR portal with employee portal access
            return redirect(url_for('hr_portal'))
        elif department == 'IT':
            # IT access - redirect to IT portal with employee and career access
            return redirect(url_for('it_portal'))
        else:
            # Employee access - redirect to employee portal
            return redirect(url_for('employee_portal'))
            
    except Exception as e:
        flash(f'Login error: {str(e)}', 'error')
        return redirect(url_for('access_page'))


@app.route('/hr-portal')
@login_required
def hr_portal():
    """HR Portal - HR, Manager, and CEO access"""
    if session.get('user_department') not in ['HR', 'Manager', 'CEO']:
        flash('Access denied - HR privileges required', 'error')
        return redirect(url_for('signin'))
    
    return render_template('hr_portal.html', 
                         user_name=session.get('user_name'),
                         user_department=session.get('user_department'))

@app.route('/employee-portal')
@login_required
def employee_portal():
    """Employee Portal - All employees access"""
    if 'user_id' not in session:
        flash('Please log in to access employee portal.', 'error')
        return redirect(url_for('signin'))
    
    return render_template('employee_portal.html', 
                         user_name=session.get('user_name'),
                         user_department=session.get('user_department'),
                         employee_id=session.get('employee_id'))

@app.route('/it-portal')
@login_required
def it_portal():
    """IT Portal - IT and CEO access"""
    if session.get('user_department') not in ['IT', 'CEO']:
        flash('Access denied - IT privileges required', 'error')
        return redirect(url_for('signin'))
    
    return render_template('it_portal.html', 
                         user_name=session.get('user_name'),
                         user_department=session.get('user_department'))

@app.route('/career-portal')
@login_required
def career_portal():
    """Career Portal - All employees access"""
    if 'user_id' not in session:
        flash('Please log in to access career portal.', 'error')
        return redirect(url_for('signin'))
    
    return render_template('career_portal.html', 
                         user_name=session.get('user_name'),
                         user_department=session.get('user_department'),
                         employee_id=session.get('employee_id'))

# Admin Dashboard API Endpoints
@app.route('/api/admin/dashboard-stats')
@login_required
def admin_dashboard_stats():
    if session.get('user_department') != 'CEO':
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get total employees
        cur.execute("SELECT COUNT(*) FROM employee WHERE status = 'active'")
        total_employees = cur.fetchone()[0]
        
        # Get open tickets
        cur.execute("SELECT COUNT(*) FROM tickets WHERE status IN ('Open', 'In Progress')")
        open_tickets = cur.fetchone()[0]
        
        # Get pending leave requests
        cur.execute("SELECT COUNT(*) FROM leave_requests WHERE status = 'Pending'")
        pending_leaves = cur.fetchone()[0]
        
        # Get active job postings
        cur.execute("SELECT COUNT(*) FROM job_postings")
        active_jobs = cur.fetchone()[0]
        
        conn.close()
        
        return {
            'total_employees': total_employees,
            'open_tickets': open_tickets,
            'pending_leaves': pending_leaves,
            'active_jobs': active_jobs
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/admin/recent-activity')
@login_required
def admin_recent_activity():
    if session.get('user_department') != 'CEO':
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        activities = []
        
        # Recent employee additions
        cur.execute("""
            SELECT CONCAT('New employee: ', first_name, ' ', last_name, ' joined') as description,
                   joined_date as timestamp, 'user-plus' as icon
            FROM employee 
            WHERE joined_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY joined_date DESC LIMIT 5
        """)
        emp_activities = cur.fetchall()
        
        # Recent ticket submissions
        cur.execute("""
            SELECT CONCAT('New ticket submitted by employee') as description,
                   submitted_on as timestamp, 'ticket-alt' as icon
            FROM tickets 
            WHERE submitted_on >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ORDER BY submitted_on DESC LIMIT 5
        """)
        ticket_activities = cur.fetchall()
        
        # Combine activities
        all_activities = emp_activities + ticket_activities
        all_activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        
        # Format timestamps
        for activity in all_activities[:10]:
            if activity['timestamp']:
                activity['timestamp'] = activity['timestamp'].strftime('%Y-%m-%d %H:%M')
            else:
                activity['timestamp'] = 'Unknown'
        
        conn.close()
        
        return {'activities': all_activities[:10]}
        
    except Exception as e:
        return {'error': str(e)}, 500

# Employee Portal API Endpoints
@app.route('/api/employee/profile')
@login_required
def employee_get_profile():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT e.*, p.project_name, m.first_name as manager_first_name, m.last_name as manager_last_name
            FROM employee e
            LEFT JOIN project p ON e.project_id = p.project_id
            LEFT JOIN employee m ON e.manager_id = m.employee_id
            WHERE e.employee_id = %s
        """, (session.get('employee_id'),))
        
        profile = cur.fetchone()
        conn.close()
        
        if profile:
            # Format dates
            if profile['joined_date']:
                profile['joined_date'] = profile['joined_date'].strftime('%Y-%m-%d')
            # Convert photo_blob to base64 if exists
            if profile['photo_blob']:
                import base64
                profile['photo_base64'] = base64.b64encode(profile['photo_blob']).decode('utf-8')
        
        return {'profile': profile}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/employee/submit-timesheet', methods=['POST'])
@login_required
def employee_submit_timesheet():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get form data
        week_start = request.form['week_start']
        project_id = request.form.get('project_id')
        work_description = request.form.get('work_description', '')
        
        # Process daily hours
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        
        # Calculate week dates
        from datetime import datetime, timedelta
        start_date = datetime.strptime(week_start, '%Y-%m-%d')
        
        for i, day in enumerate(days):
            hours = request.form.get(f'hours_{day}')
            if hours and float(hours) > 0:
                work_date = start_date + timedelta(days=i)
                
                cur.execute("""
                    INSERT INTO timesheet (employee_id, project_id, work_date, hours_logged, work_description)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    hours_logged = VALUES(hours_logged),
                    work_description = VALUES(work_description)
                """, (
                    session.get('employee_id'),
                    project_id if project_id else None,
                    work_date.strftime('%Y-%m-%d'),
                    float(hours),
                    work_description
                ))
        
        conn.commit()
        conn.close()
        
        flash('Timesheet submitted successfully!', 'success')
        return redirect(url_for('employee_portal'))
        
    except Exception as e:
        flash(f'Error submitting timesheet: {str(e)}', 'error')
        return redirect(url_for('employee_portal'))

@app.route('/employee/submit-ticket', methods=['POST'])
@login_required
def employee_submit_ticket():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        women_safety = 1 if request.form.get('women_safety') == '1' else 0
        
        cur.execute("""
            INSERT INTO tickets (employee_id, department, subject, issue_description, severity, women_safety, status, created_date)
            VALUES (%s, %s, %s, %s, %s, %s, 'Open', NOW())
        """, (
            session.get('employee_id'),
            request.form['department'],
            request.form['subject'],
            request.form['description'],
            request.form['severity'],
            women_safety
        ))
        
        conn.commit()
        conn.close()
        
        flash('Support ticket submitted successfully!', 'success')
        return redirect(url_for('employee_portal'))
        
    except Exception as e:
        flash(f'Error submitting ticket: {str(e)}', 'error')
        return redirect(url_for('employee_portal'))

@app.route('/employee/submit-feedback', methods=['POST'])
@login_required
def employee_submit_feedback():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO feedback (employee_id, feedback_type, target_role, feedback_text, is_anonymous, created_date)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (
            session.get('employee_id'),
            request.form['feedback_type'],
            request.form.get('target_role'),
            request.form['feedback_text'],
            1  # Always anonymous
        ))
        
        conn.commit()
        conn.close()
        
        flash('Anonymous feedback submitted successfully!', 'success')
        return redirect(url_for('employee_portal'))
        
    except Exception as e:
        flash(f'Error submitting feedback: {str(e)}', 'error')
        return redirect(url_for('employee_portal'))

# Employee Portal API Endpoints
@app.route('/api/employee/my-tickets')
@login_required
def employee_get_my_tickets():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT ticket_id, department, subject, issue_description as description, 
                   severity, status, women_safety, created_date, updated_date
            FROM tickets 
            WHERE employee_id = %s 
            ORDER BY created_date DESC
        """, (session.get('employee_id'),))
        
        tickets = cur.fetchall()
        
        # Format dates
        for ticket in tickets:
            if ticket['created_date']:
                ticket['created_date'] = ticket['created_date'].strftime('%Y-%m-%d %H:%M')
            if ticket['updated_date']:
                ticket['updated_date'] = ticket['updated_date'].strftime('%Y-%m-%d %H:%M')
        
        conn.close()
        
        return {'tickets': tickets}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/employee/induction')
@login_required
def employee_get_induction():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Get induction content for the employee's department
        cur.execute("""
            SELECT ic.content_id, ic.title, ic.description, ic.file_path, ic.content_type,
                   ic.created_date, ic.is_mandatory
            FROM induction_content ic
            LEFT JOIN employee e ON e.department = ic.target_department OR ic.target_department IS NULL
            WHERE e.employee_id = %s AND ic.is_active = TRUE
            ORDER BY ic.is_mandatory DESC, ic.created_date DESC
        """, (session.get('employee_id'),))
        
        content = cur.fetchall()
        
        # Format dates
        for item in content:
            if item['created_date']:
                item['created_date'] = item['created_date'].strftime('%Y-%m-%d')
        
        conn.close()
        
        return {'content': content}
        
    except Exception as e:
        return {'error': str(e)}, 500



# Career Portal API Endpoints
@app.route('/api/career/badges')
@login_required
def career_get_badges():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Get employee badges
        cur.execute("""
            SELECT eb.*, bc.badge_name, bc.description, bc.icon
            FROM employee_badges eb
            JOIN badge_catalog bc ON eb.badge_id = bc.badge_id
            WHERE eb.employee_id = %s
            ORDER BY eb.earned_date DESC
        """, (session.get('employee_id'),))
        
        badges = cur.fetchall()
        
        # Get available badges not yet earned
        cur.execute("""
            SELECT bc.*
            FROM badge_catalog bc
            WHERE bc.badge_id NOT IN (
                SELECT badge_id FROM employee_badges WHERE employee_id = %s
            )
        """, (session.get('employee_id'),))
        
        available_badges = cur.fetchall()
        
        conn.close()
        
        return {
            'earned_badges': badges,
            'available_badges': available_badges
        }
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/career/courses')
@login_required
def career_get_courses():
    try:
        search_query = request.args.get('search', '')
        category = request.args.get('category', '')
        
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Build search query
        base_query = """
            SELECT cc.*, bc.badge_name, bc.description as badge_description,
                   COUNT(ca.attempt_id) as total_attempts,
                   MAX(ca.score) as best_score,
                   MAX(ca.passed) as has_passed
            FROM course_catalog cc
            LEFT JOIN badge_catalog bc ON cc.badge_id = bc.badge_id
            LEFT JOIN course_attempts ca ON cc.course_id = ca.course_id AND ca.employee_id = %s
            WHERE cc.is_active = TRUE
        """
        
        params = [session.get('employee_id')]
        
        if search_query:
            base_query += " AND (cc.course_name LIKE %s OR cc.description LIKE %s)"
            params.extend([f'%{search_query}%', f'%{search_query}%'])
        
        if category:
            base_query += " AND cc.skill_category = %s"
            params.append(category)
        
        base_query += " GROUP BY cc.course_id ORDER BY cc.course_name"
        
        cur.execute(base_query, params)
        courses = cur.fetchall()
        
        # Get available categories
        cur.execute("SELECT DISTINCT skill_category FROM course_catalog WHERE is_active = TRUE")
        categories = [row['skill_category'] for row in cur.fetchall()]
        
        conn.close()
        
        return {
            'courses': courses,
            'categories': categories
        }
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/career/course/<int:course_id>')
@login_required
def career_get_course_details(course_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Get course details
        cur.execute("""
            SELECT cc.*, bc.badge_name, bc.description as badge_description, bc.icon
            FROM course_catalog cc
            LEFT JOIN badge_catalog bc ON cc.badge_id = bc.badge_id
            WHERE cc.course_id = %s AND cc.is_active = TRUE
        """, (course_id,))
        
        course = cur.fetchone()
        
        if not course:
            return {'error': 'Course not found'}, 404
        
        # Get user's attempt history for this course
        cur.execute("""
            SELECT attempt_id, score, total_questions, passed, attempt_date
            FROM course_attempts
            WHERE employee_id = %s AND course_id = %s
            ORDER BY attempt_date DESC
        """, (session.get('employee_id'), course_id))
        
        attempts = cur.fetchall()
        
        # Format attempt dates
        for attempt in attempts:
            if attempt['attempt_date']:
                attempt['attempt_date'] = attempt['attempt_date'].strftime('%Y-%m-%d %H:%M')
        
        # Check if user already has the badge
        cur.execute("""
            SELECT COUNT(*) as has_badge
            FROM employee_badges
            WHERE employee_id = %s AND badge_id = %s
        """, (session.get('employee_id'), course['badge_id']))
        
        has_badge = cur.fetchone()['has_badge'] > 0
        
        conn.close()
        
        return {
            'course': course,
            'attempts': attempts,
            'has_badge': has_badge
        }
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/career/course/<int:course_id>/start-exam')
@login_required
def career_start_exam(course_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Verify course exists and is active
        cur.execute("""
            SELECT course_name, passing_score
            FROM course_catalog
            WHERE course_id = %s AND is_active = TRUE
        """, (course_id,))
        
        course = cur.fetchone()
        
        if not course:
            return {'error': 'Course not found or inactive'}, 404
        
        # Get 20 random questions for this course
        cur.execute("""
            SELECT question_id, question_text, option_a, option_b, option_c, option_d
            FROM course_questions
            WHERE course_id = %s
            ORDER BY RAND()
            LIMIT 20
        """, (course_id,))
        
        questions = cur.fetchall()
        
        if len(questions) < 20:
            return {'error': 'Not enough questions available for this course'}, 400
        
        conn.close()
        
        return {
            'course_name': course['course_name'],
            'passing_score': course['passing_score'],
            'questions': questions,
            'total_questions': len(questions)
        }
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/career/course/<int:course_id>/submit-exam', methods=['POST'])
@login_required
def career_submit_exam(course_id):
    try:
        answers = request.json.get('answers', {})  # {question_id: 'A', question_id: 'B', ...}
        
        if not answers:
            return {'error': 'No answers provided'}, 400
        
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Get course details
        cur.execute("""
            SELECT course_name, passing_score, badge_id
            FROM course_catalog
            WHERE course_id = %s AND is_active = TRUE
        """, (course_id,))
        
        course = cur.fetchone()
        
        if not course:
            return {'error': 'Course not found'}, 404
        
        # Get correct answers for submitted questions
        question_ids = list(answers.keys())
        placeholders = ','.join(['%s'] * len(question_ids))
        
        cur.execute(f"""
            SELECT question_id, correct_answer
            FROM course_questions
            WHERE question_id IN ({placeholders})
        """, question_ids)
        
        correct_answers = {str(row['question_id']): row['correct_answer'] for row in cur.fetchall()}
        
        # Calculate score
        total_questions = len(answers)
        correct_count = 0
        
        for question_id, user_answer in answers.items():
            if correct_answers.get(str(question_id)) == user_answer:
                correct_count += 1
        
        score = int((correct_count / total_questions) * 100)
        passed = score >= course['passing_score']
        
        # Record attempt
        cur.execute("""
            INSERT INTO course_attempts 
            (employee_id, course_id, score, total_questions, passed, answers_json)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session.get('employee_id'),
            course_id,
            score,
            total_questions,
            passed,
            json.dumps(answers)
        ))
        
        attempt_id = cur.lastrowid
        
        # Award badge if passed and not already earned
        badge_awarded = False
        if passed and course['badge_id']:
            # Check if user already has this badge
            cur.execute("""
                SELECT COUNT(*) as has_badge
                FROM employee_badges
                WHERE employee_id = %s AND badge_id = %s
            """, (session.get('employee_id'), course['badge_id']))
            
            if cur.fetchone()['has_badge'] == 0:
                # Award the badge
                cur.execute("""
                    INSERT INTO employee_badges (employee_id, badge_id, earned_date)
                    VALUES (%s, %s, NOW())
                """, (session.get('employee_id'), course['badge_id']))
                badge_awarded = True
        
        conn.commit()
        conn.close()
        
        return {
            'attempt_id': attempt_id,
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'passed': passed,
            'passing_score': course['passing_score'],
            'badge_awarded': badge_awarded,
            'course_name': course['course_name']
        }
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/career/my-attempts')
@login_required
def career_get_my_attempts():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT ca.*, cc.course_name, cc.skill_category, bc.badge_name
            FROM course_attempts ca
            JOIN course_catalog cc ON ca.course_id = cc.course_id
            LEFT JOIN badge_catalog bc ON cc.badge_id = bc.badge_id
            WHERE ca.employee_id = %s
            ORDER BY ca.attempt_date DESC
        """, (session.get('employee_id'),))
        
        attempts = cur.fetchall()
        
        # Format dates
        for attempt in attempts:
            if attempt['attempt_date']:
                attempt['attempt_date'] = attempt['attempt_date'].strftime('%Y-%m-%d %H:%M')
        
        conn.close()
        
        return {'attempts': attempts}
        
    except Exception as e:
        return {'error': str(e)}, 500

# IT Portal API Endpoints
@app.route('/api/it/dashboard-stats')
@login_required
def it_dashboard_stats():
    if session.get('user_department') not in ['IT', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get open IT tickets
        cur.execute("SELECT COUNT(*) FROM tickets WHERE department = 'IT' AND status IN ('Open', 'In Progress')")
        open_tickets = cur.fetchone()[0]
        
        # Get total devices
        cur.execute("SELECT COUNT(*) FROM asset_inventory")
        total_devices = cur.fetchone()[0]
        
        # Get available devices
        cur.execute("SELECT COUNT(*) FROM asset_inventory WHERE status = 'Available'")
        available_devices = cur.fetchone()[0]
        
        # Get devices needing repair
        cur.execute("SELECT COUNT(*) FROM asset_inventory WHERE status = 'Under Repair'")
        pending_repairs = cur.fetchone()[0]
        
        conn.close()
        
        return {
            'open_tickets': open_tickets,
            'total_devices': total_devices,
            'available_devices': available_devices,
            'pending_repairs': pending_repairs
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/it/tickets')
@login_required
def it_get_tickets():
    if session.get('user_department') not in ['IT', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT t.*, e.first_name, e.last_name
            FROM tickets t
            JOIN employee e ON t.employee_id = e.employee_id
            WHERE t.department = 'IT'
            ORDER BY t.submitted_on DESC
        """)
        
        tickets = cur.fetchall()
        conn.close()
        
        # Format dates
        for ticket in tickets:
            if ticket['submitted_on']:
                ticket['submitted_on'] = ticket['submitted_on'].strftime('%Y-%m-%d %H:%M')
        
        return {'tickets': tickets}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/it/update-ticket', methods=['POST'])
@login_required
def it_update_ticket():
    if session.get('user_department') not in ['IT', 'CEO']:
        flash('Access denied', 'error')
        return redirect(url_for('it_portal'))
    
    try:
        ticket_id = request.form['ticket_id']
        status = request.form['status']
        resolution_notes = request.form.get('resolution_notes', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE tickets 
            SET status = %s, resolution_notes = %s, resolved_by = %s, resolved_on = NOW()
            WHERE ticket_id = %s
        """, (status, resolution_notes, session.get('employee_id'), ticket_id))
        
        conn.commit()
        conn.close()
        
        flash('Ticket status updated successfully!', 'success')
        return redirect(url_for('it_portal'))
        
    except Exception as e:
        flash(f'Error updating ticket: {str(e)}', 'error')
        return redirect(url_for('it_portal'))

@app.route('/api/it/devices')
@login_required
def it_get_devices():
    if session.get('user_department') not in ['IT', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT ai.*, 
                   CONCAT(e.first_name, ' ', e.last_name) as assigned_to
            FROM asset_inventory ai
            LEFT JOIN employee e ON ai.assigned_to = e.employee_id
            ORDER BY ai.asset_id DESC
        """)
        
        devices = cur.fetchall()
        conn.close()
        
        # Format dates
        for device in devices:
            if device.get('purchase_date'):
                device['purchase_date'] = device['purchase_date'].strftime('%Y-%m-%d')
            if device.get('warranty_expiry'):
                device['warranty_expiry'] = device['warranty_expiry'].strftime('%Y-%m-%d')
        
        return {'devices': devices}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/it/add-device', methods=['POST'])
@login_required
def it_add_device():
    if session.get('user_department') not in ['IT', 'CEO']:
        flash('Access denied', 'error')
        return redirect(url_for('it_portal'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO asset_inventory 
            (device_type, brand, model, serial_number, purchase_date, warranty_expiry, 
             specifications, status, added_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Available', %s)
        """, (
            request.form['device_type'], request.form['brand'],
            request.form['model'], request.form['serial_number'],
            request.form.get('purchase_date'), request.form.get('warranty_expiry'),
            request.form.get('specifications', ''), session.get('employee_id')
        ))
        
        conn.commit()
        conn.close()
        
        flash('Device added successfully!', 'success')
        return redirect(url_for('it_portal'))
        
    except Exception as e:
        flash(f'Error adding device: {str(e)}', 'error')
        return redirect(url_for('it_portal'))

@app.route('/it/assign-device', methods=['POST'])
@login_required
def it_assign_device():
    if session.get('user_department') not in ['IT', 'CEO']:
        flash('Access denied', 'error')
        return redirect(url_for('it_portal'))
    
    try:
        asset_id = request.form['asset_id']
        employee_id = request.form['employee_id']
        assigned_date = request.form.get('assigned_date')
        notes = request.form.get('notes', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Update asset inventory
        cur.execute("""
            UPDATE asset_inventory 
            SET assigned_to = %s, assigned_date = %s, status = 'Assigned', notes = %s
            WHERE asset_id = %s
        """, (employee_id, assigned_date, notes, asset_id))
        
        conn.commit()
        conn.close()
        
        flash('Device assigned successfully!', 'success')
        return redirect(url_for('it_portal'))
        
    except Exception as e:
        flash(f'Error assigning device: {str(e)}', 'error')
        return redirect(url_for('it_portal'))

@app.route('/api/it/troubleshooting-docs')
@login_required
def it_get_troubleshooting_docs():
    if session.get('user_department') not in ['IT', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Create troubleshooting_docs table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS troubleshooting_docs (
                doc_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                problem_description TEXT NOT NULL,
                solution_steps TEXT NOT NULL,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES employee(employee_id)
            )
        """)
        
        cur.execute("""
            SELECT td.*, e.first_name, e.last_name
            FROM troubleshooting_docs td
            LEFT JOIN employee e ON td.created_by = e.employee_id
            ORDER BY td.created_at DESC
        """)
        
        docs = cur.fetchall()
        conn.close()
        
        return {'docs': docs}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/it/add-troubleshooting', methods=['POST'])
@login_required
def it_add_troubleshooting():
    if session.get('user_department') not in ['IT', 'CEO']:
        flash('Access denied', 'error')
        return redirect(url_for('it_portal'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS troubleshooting_docs (
                doc_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                problem_description TEXT NOT NULL,
                solution_steps TEXT NOT NULL,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES employee(employee_id)
            )
        """)
        
        cur.execute("""
            INSERT INTO troubleshooting_docs 
            (title, category, problem_description, solution_steps, created_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form['title'], request.form['category'],
            request.form['problem_description'], request.form['solution_steps'],
            session.get('employee_id')
        ))
        
        conn.commit()
        conn.close()
        
        flash('Troubleshooting guide added successfully!', 'success')
        return redirect(url_for('it_portal'))
        
    except Exception as e:
        flash(f'Error adding guide: {str(e)}', 'error')
        return redirect(url_for('it_portal'))

#onboarding feature for hr portal


# HR Onboarding Panel View
@app.route('/hr_onboarding')
def hr_onboarding():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM employee WHERE status = 'active'")
    employees = cur.fetchall()
    conn.close()
    return render_template("hr_onboarding.html", employees=employees)

# Add New Employee
@app.route('/add_employee', methods=['POST'])
def add_employee():
    form = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO employee 
        (first_name, last_name, email, contact_number, gender, department, role_title,
         visa_type, experience_years, salary, location, designation,
         leaves_sick, leaves_personal, comp_off, status, joined_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                5, 10, 0, 'active', NOW())
    """, (
        form['first_name'], form['last_name'], form['email'], form['contact_number'],
        form['gender'], form['department'], form['role_title'],
        form['visa_type'], form['experience_years'], form['salary'],
        form['location'], form['designation']
    ))
    conn.commit()
    conn.close()
    flash("✅ Employee added successfully!", "success")
    return redirect(url_for('hr_onboarding'))

# Edit Employee Inline
@app.route('/edit_employee/<int:emp_id>', methods=['POST'])
def edit_employee(emp_id):
    form = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE employee
        SET first_name=%s, email=%s, contact_number=%s, department=%s, designation=%s
        WHERE employee_id=%s
    """, (
        form['first_name'], form['email'], form['contact_number'],
        form['department'], form['designation'], emp_id
    ))
    conn.commit()
    conn.close()
    flash("✏️ Employee updated.", "success")
    return redirect(url_for('hr_onboarding'))

# Deactivate Employee (soft delete)
@app.route('/deactivate_employee/<int:emp_id>')
def deactivate_employee(emp_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employee SET status = 'inactive' WHERE employee_id = %s", (emp_id,))
    conn.commit()
    conn.close()
    flash("🗑️ Employee deactivated.", "info")
    return redirect(url_for('hr_onboarding'))

# 🤖 Chatbot Integration
OLLAMA_API_URL = "http://localhost:11434/api/chat"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_prompt = data.get("prompt")

    def generate():
        payload = {
            "model": "llama3",
            "messages": [{"role": "user", "content": user_prompt}],
            "stream": True
        }
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))["message"]["content"]
                    yield chunk

    return Response(stream_with_context(generate()), content_type='text/plain')

# HR Portal API Endpoints (Additional)
@app.route('/api/hr/timesheet-requests')
@login_required
def hr_get_timesheet_requests():
    if session.get('user_department') not in ['HR', 'Manager', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT t.*, e.first_name, e.last_name, e.department, p.project_name
            FROM timesheet t
            JOIN employee e ON t.employee_id = e.employee_id
            LEFT JOIN project p ON t.project_id = p.project_id
            WHERE t.status = 'Pending' OR t.status IS NULL
            ORDER BY t.work_date DESC
        """)
        
        requests = cur.fetchall()
        
        # Format dates
        for req in requests:
            if req['work_date']:
                req['work_date'] = req['work_date'].strftime('%Y-%m-%d')
        
        conn.close()
        
        return {'timesheet_requests': requests}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/hr/approve-timesheet', methods=['POST'])
@login_required
def hr_approve_timesheet():
    if session.get('user_department') not in ['HR', 'Manager', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        timesheet_id = request.form['timesheet_id']
        action = request.form['action']  # 'approve' or 'reject'
        comments = request.form.get('comments', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        status = 'Approved' if action == 'approve' else 'Rejected'
        
        cur.execute("""
            UPDATE timesheet 
            SET status = %s, approved_by = %s, approval_date = NOW(), approval_comments = %s
            WHERE timesheet_id = %s
        """, (status, session.get('employee_id'), comments, timesheet_id))
        
        conn.commit()
        conn.close()
        
        flash(f'Timesheet {status.lower()} successfully!', 'success')
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        flash(f'Error processing timesheet: {str(e)}', 'error')
        return redirect(url_for('hr_portal'))

@app.route('/api/hr/hr-tickets')
@login_required
def hr_get_hr_tickets():
    if session.get('user_department') not in ['HR', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT t.*, e.first_name, e.last_name, e.department as emp_department
            FROM tickets t
            JOIN employee e ON t.employee_id = e.employee_id
            WHERE t.department = 'HR' OR t.women_safety = 1
            ORDER BY t.created_date DESC
        """)
        
        tickets = cur.fetchall()
        
        # Format dates
        for ticket in tickets:
            if ticket['created_date']:
                ticket['created_date'] = ticket['created_date'].strftime('%Y-%m-%d %H:%M')
            if ticket['updated_date']:
                ticket['updated_date'] = ticket['updated_date'].strftime('%Y-%m-%d %H:%M')
        
        conn.close()
        
        return {'tickets': tickets}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/hr/update-ticket-status', methods=['POST'])
@login_required
def hr_update_ticket_status():
    if session.get('user_department') not in ['HR', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        ticket_id = request.form['ticket_id']
        status = request.form['status']
        resolution = request.form.get('resolution', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE tickets 
            SET status = %s, resolution = %s, resolved_by = %s, updated_date = NOW()
            WHERE ticket_id = %s
        """, (status, resolution, session.get('employee_id'), ticket_id))
        
        conn.commit()
        conn.close()
        
        flash('Ticket updated successfully!', 'success')
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        flash(f'Error updating ticket: {str(e)}', 'error')
        return redirect(url_for('hr_portal'))

@app.route('/api/hr/job-postings')
@login_required
def hr_get_job_postings():
    if session.get('user_department') not in ['HR', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT jp.*, COUNT(ja.application_id) as application_count
            FROM job_postings jp
            LEFT JOIN job_applications ja ON jp.job_id = ja.job_id
            GROUP BY jp.job_id
            ORDER BY jp.created_date DESC
        """)
        
        postings = cur.fetchall()
        
        # Format dates
        for posting in postings:
            if posting['created_date']:
                posting['created_date'] = posting['created_date'].strftime('%Y-%m-%d')
            if posting['application_deadline']:
                posting['application_deadline'] = posting['application_deadline'].strftime('%Y-%m-%d')
        
        conn.close()
        
        return {'job_postings': postings}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/hr/job-applications')
@login_required
def hr_get_job_applications():
    if session.get('user_department') not in ['HR', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT ja.*, jp.job_title, jp.department, e.first_name, e.last_name, e.email
            FROM job_applications ja
            JOIN job_postings jp ON ja.job_id = jp.job_id
            LEFT JOIN employee e ON ja.employee_id = e.employee_id
            ORDER BY ja.application_date DESC
        """)
        
        applications = cur.fetchall()
        
        # Format dates
        for app in applications:
            if app['application_date']:
                app['application_date'] = app['application_date'].strftime('%Y-%m-%d %H:%M')
        
        conn.close()
        
        return {'applications': applications}
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/hr/update-application-status', methods=['POST'])
@login_required
def hr_update_application_status():
    if session.get('user_department') not in ['HR', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        application_id = request.form['application_id']
        status = request.form['status']
        notes = request.form.get('notes', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE job_applications 
            SET status = %s, hr_notes = %s, reviewed_by = %s, review_date = NOW()
            WHERE application_id = %s
        """, (status, notes, session.get('employee_id'), application_id))
        
        conn.commit()
        conn.close()
        
        flash('Application status updated successfully!', 'success')
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        flash(f'Error updating application: {str(e)}', 'error')
        return redirect(url_for('hr_portal'))

@app.route('/hr/create-job', methods=['POST'])
@login_required
def hr_create_job():
    if session.get('user_department') not in ['HR', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO job_postings 
            (job_title, department, job_description, requirements, salary_range, 
             employment_type, location, application_deadline, posted_by, created_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'Active')
        """, (
            request.form['job_title'],
            request.form['department'],
            request.form['job_description'],
            request.form['requirements'],
            request.form.get('salary_range'),
            request.form['employment_type'],
            request.form.get('location'),
            request.form.get('application_deadline'),
            session.get('employee_id')
        ))
        
        conn.commit()
        conn.close()
        
        flash('Job posting created successfully!', 'success')
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        flash(f'Error creating job posting: {str(e)}', 'error')
        return redirect(url_for('hr_portal'))

@app.route('/hr/upload-induction', methods=['POST'])
@login_required
def hr_upload_induction():
    if session.get('user_department') not in ['HR', 'CEO']:
        return {'error': 'Access denied'}, 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Handle file upload if present
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # In production, save to proper file storage
                file_path = f"/uploads/induction/{file.filename}"
                # file.save(file_path)  # Uncomment in production
        
        cur.execute("""
            INSERT INTO induction_content 
            (title, description, content_type, target_department, file_path, 
             is_mandatory, created_by, created_date, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), TRUE)
        """, (
            request.form['title'],
            request.form['description'],
            request.form['content_type'],
            request.form.get('target_department'),
            file_path,
            1 if request.form.get('is_mandatory') == 'on' else 0,
            session.get('employee_id')
        ))
        
        conn.commit()
        conn.close()
        
        flash('Induction content uploaded successfully!', 'success')
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        flash(f'Error uploading induction content: {str(e)}', 'error')
        return redirect(url_for('hr_portal'))

# ===== PORTAL ROUTES - Missing routes that signin redirects to =====

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    """Admin Dashboard - CEO access only"""
    if session.get('user_department') != 'CEO':
        flash('Access denied - Admin privileges required', 'error')
        return redirect(url_for('signin'))
    
    # Pass user data to template
    return render_template('admin_dashboard.html', 
                         user_name=session.get('user_name'),
                         user_department=session.get('user_department'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
