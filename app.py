from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import db
from auth import login_required, role_required, authenticate_user, create_user_session, clear_user_session, get_current_user
from azure_storage import azure_storage
from utils import allowed_file, generate_unique_filename, calculate_work_days, log_user_activity
from config import Config
import os
import logging
from datetime import datetime, timedelta
import json
import random

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# ==================== AUTHENTICATION ROUTES ====================

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
        
        user = authenticate_user(email, password)
        if user:
            create_user_session(user)
            log_user_activity(user['employee_id'], 'Login', f'User logged in from {request.remote_addr}', db)
            
            # Redirect based on role
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
            flash('Invalid email or password', 'error')
    
    return render_template('signin.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_user_activity(session['user_id'], 'Logout', 'User logged out', db)
    clear_user_session()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('home'))

# ==================== ADMIN DASHBOARD ====================

@app.route('/admin-dashboard')
@login_required
@role_required(['ceo', 'cto'])
def admin_dashboard():
    return render_template('admin_dashboard.html', user_name=session.get('user_name'))

@app.route('/api/admin/dashboard-stats')
@login_required
@role_required(['ceo', 'cto'])
def admin_dashboard_stats():
    try:
        # Get total employees
        total_employees = db.execute_query("SELECT COUNT(*) as count FROM employee WHERE status = 'active'")
        
        # Get open tickets
        open_tickets = db.execute_query("SELECT COUNT(*) as count FROM tickets WHERE status IN ('Open', 'In Progress')")
        
        # Get pending leaves
        pending_leaves = db.execute_query("SELECT COUNT(*) as count FROM leave_requests WHERE status = 'Pending'")
        
        # Get job postings
        job_postings = db.execute_query("SELECT COUNT(*) as count FROM job_postings")
        
        return jsonify({
            'total_employees': total_employees[0]['count'] if total_employees else 0,
            'open_tickets': open_tickets[0]['count'] if open_tickets else 0,
            'pending_leaves': pending_leaves[0]['count'] if pending_leaves else 0,
            'job_postings': job_postings[0]['count'] if job_postings else 0
        })
    except Exception as e:
        logging.error(f"Error loading admin dashboard stats: {e}")
        return jsonify({'error': 'Failed to load dashboard stats'}), 500

@app.route('/api/admin/recent-activity')
@login_required
@role_required(['ceo', 'cto'])
def admin_recent_activity():
    try:
        query = """
        SELECT ual.action, ual.details, ual.timestamp,
               CONCAT(e.first_name, ' ', e.last_name) as employee_name
        FROM user_activity_log ual
        JOIN employee e ON ual.employee_id = e.employee_id
        ORDER BY ual.timestamp DESC
        LIMIT 10
        """
        activities = db.execute_query(query)
        
        formatted_activities = []
        for activity in activities or []:
            formatted_activities.append({
                'description': f"{activity['employee_name']} {activity['action']}",
                'timestamp': activity['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'icon': 'fas fa-user',
                'color': 'blue'
            })
        
        return jsonify({'activities': formatted_activities})
    except Exception as e:
        logging.error(f"Error loading recent activity: {e}")
        return jsonify({'activities': []})

# ==================== EMPLOYEE PORTAL ====================

@app.route('/employee-portal')
@login_required
def employee_portal():
    return render_template('employee_portal.html', 
                         user_name=session.get('user_name'),
                         user_role=session.get('user_role'),
                         user_email=session.get('user_email'),
                         user_department=session.get('user_department'))

@app.route('/api/employee/profile')
@login_required
def employee_profile():
    try:
        query = """
        SELECT e.employee_id, e.first_name, e.last_name, e.email, e.contact_number,
               e.department, e.role_title, e.location, e.leaves_sick, e.leaves_personal,
               e.comp_off, e.joined_date
        FROM employee e
        WHERE e.employee_id = %s AND e.status = 'active'
        """
        result = db.execute_query(query, (session['user_id'],))
        
        if result:
            profile = result[0]
            profile['joined_date'] = profile['joined_date'].strftime('%Y-%m-%d') if profile['joined_date'] else ''
            return jsonify({'profile': profile})
        
        return jsonify({'error': 'Profile not found'}), 404
    except Exception as e:
        logging.error(f"Error loading employee profile: {e}")
        return jsonify({'error': 'Failed to load profile'}), 500

@app.route('/submit-leave', methods=['POST'])
@login_required
def submit_leave():
    try:
        leave_type = request.form.get('leave_type')
        sub_type = request.form.get('sub_type')
        try:
            # Get form data
            leave_type = request.form.get('leave_type')
            sub_type = request.form.get('sub_type') if leave_type == 'Paid' else None
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            reason = request.form.get('reason', '')
            
            # Validate required fields
            if not all([leave_type, start_date, end_date]):
                flash('Please fill in all required fields.', 'error')
                return redirect(url_for('submit_leave'))
            
            # Validate dates
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                if start_dt > end_dt:
                    flash('Start date cannot be after end date.', 'error')
                    return redirect(url_for('submit_leave'))
                    
                if start_dt < datetime.now().date():
                    flash('Cannot request leave for past dates.', 'error')
                    return redirect(url_for('submit_leave'))
                    
            except ValueError:
                flash('Invalid date format.', 'error')
                return redirect(url_for('submit_leave'))
            
            # Insert into database
            query = """
            INSERT INTO leave_requests (employee_id, leave_type, sub_type, start_date, end_date, reason, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending', NOW())
            """
            
            result = db.execute_query(query, (
                session['user_id'], 
                leave_type, 
                sub_type, 
                start_date, 
                end_date, 
                reason
            ))
            
            if result is not None:
                # Get the inserted leave request for confirmation
                leave_query = """
                SELECT lr.*, e.first_name, e.last_name 
                FROM leave_requests lr
                JOIN employee e ON lr.employee_id = e.employee_id
                WHERE lr.employee_id = %s 
                ORDER BY lr.created_at DESC 
                LIMIT 1
                """
                leave_data = db.execute_query(leave_query, (session['user_id'],))
                
                if leave_data:
                    # Log activity
                    log_user_activity(session['user_id'], 'Leave Request Submitted', 
                                    f'Leave type: {leave_type}, Dates: {start_date} to {end_date}', db)
                    
                    flash('Leave request submitted successfully!', 'success')
                    return render_template('leave_confirmation.html', leave_request=leave_data[0])
                else:
                    flash('Leave request submitted but confirmation failed.', 'warning')
                    return redirect(url_for('leave_status'))
            else:
                flash('Failed to submit leave request. Please try again.', 'error')
                return redirect(url_for('submit_leave'))
                
        except Exception as e:
            logging.error(f"Leave request submission error: {str(e)}")
            flash(f'Error submitting leave request: {str(e)}', 'error')
            return redirect(url_for('submit_leave'))

@app.route('/leave-status')
@login_required
def leave_status():
    try:
        query = """
        SELECT lr.*, e.first_name, e.last_name,
               CASE 
                   WHEN lr.approved_by IS NOT NULL THEN 
                       CONCAT(mgr.first_name, ' ', mgr.last_name)
                   ELSE NULL
               END as approved_by_name
        FROM leave_requests lr
        JOIN employee e ON lr.employee_id = e.employee_id
        LEFT JOIN employee mgr ON lr.approved_by = mgr.employee_id
        WHERE lr.employee_id = %s 
        ORDER BY lr.created_at DESC
        """
        leave_requests = db.execute_query(query, (session['user_id'],))
        return render_template('leave_status.html', leave_requests=leave_requests or [])
    except Exception as e:
        logging.error(f"Error loading leave status: {str(e)}")
        flash('Error loading leave requests.', 'error')
        return render_template('leave_status.html', leave_requests=[])

def submit_timesheet():
    try:
        week_start = request.form.get('week_start')
        project_id = request.form.get('project_id')
        work_description = request.form.get('work_description')
        
        # Get hours for each day
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        
        for i, day in enumerate(days):
            hours = request.form.get(f'hours_{day}')
            if hours and float(hours) > 0:
                # Calculate the actual date
                week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
                work_date = week_start_date + timedelta(days=i)
                
                # Insert timesheet entry
                query = """
                INSERT INTO timesheet (employee_id, project_id, work_date, hours_logged, description)
                VALUES (%s, %s, %s, %s, %s)
                """
                db.execute_query(query, (session['user_id'], project_id, work_date, float(hours), work_description))
        
        # Log activity
        log_user_activity(session['user_id'], 'Timesheet Submitted', f'Timesheet for week starting {week_start}', db)
        
        flash('Timesheet submitted successfully', 'success')
        return redirect(url_for('employee_portal'))
        
    except Exception as e:
        logging.error(f"Error submitting timesheet: {e}")
        flash('Error submitting timesheet', 'error')
        return redirect(url_for('employee_portal'))

@app.route('/employee/submit-feedback', methods=['POST'])
@login_required
def submit_feedback():
    try:
        feedback_type = request.form.get('feedback_type')
        target_role = request.form.get('target_role')
        feedback_text = request.form.get('feedback_text')
        
        # Insert anonymous feedback
        query = """
        INSERT INTO anonymous_feedback (employee_id, feedback_type, target_role, feedback_text)
        VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query, (session['user_id'], feedback_type, target_role, feedback_text))
        
        # Log activity
        log_user_activity(session['user_id'], 'Feedback Submitted', f'Anonymous feedback submitted', db)
        
        flash('Feedback submitted successfully', 'success')
        return redirect(url_for('employee_portal'))
        
    except Exception as e:
        logging.error(f"Error submitting feedback: {e}")
        flash('Error submitting feedback', 'error')
        return redirect(url_for('employee_portal'))

@app.route('/employee/submit-ticket', methods=['POST'])
@login_required
def submit_ticket():
    try:
        department = request.form.get('department')
        severity = request.form.get('severity')
        subject = request.form.get('subject')
        description = request.form.get('description')
        women_safety = 1 if request.form.get('women_safety') else 0
        
        # Get employee info
        emp_query = "SELECT email, gender FROM employee WHERE employee_id = %s"
        emp_result = db.execute_query(emp_query, (session['user_id'],))
        
        if emp_result:
            email = emp_result[0]['email']
            gender = emp_result[0]['gender']
            
            # Insert ticket
            query = """
            INSERT INTO tickets (employee_id, email, department, gender, women_safety, 
                               description, severity_level, status, subject)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Open', %s)
            """
            db.execute_query(query, (session['user_id'], email, department, gender, 
                                   women_safety, description, severity, subject))
            
            # Log activity
            log_user_activity(session['user_id'], 'Ticket Submitted', f'Support ticket: {subject}', db)
            
            flash('Support ticket submitted successfully', 'success')
        else:
            flash('Error: Employee information not found', 'error')
            
        return redirect(url_for('employee_portal'))
        
    except Exception as e:
        logging.error(f"Error submitting ticket: {e}")
        flash('Error submitting ticket', 'error')
        return redirect(url_for('employee_portal'))

@app.route('/api/employee/my-tickets')
@login_required
def my_tickets():
    try:
        query = """
        SELECT ticket_id, subject, description, department, severity_level as severity,
               status, submitted_on as created_date
        FROM tickets
        WHERE employee_id = %s
        ORDER BY submitted_on DESC
        """
        tickets = db.execute_query(query, (session['user_id'],))
        
        formatted_tickets = []
        for ticket in tickets or []:
            formatted_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'subject': ticket['subject'],
                'description': ticket['description'],
                'department': ticket['department'],
                'severity': ticket['severity'],
                'status': ticket['status'],
                'created_date': ticket['created_date'].strftime('%Y-%m-%d') if ticket['created_date'] else ''
            })
        
        return jsonify({'tickets': formatted_tickets})
    except Exception as e:
        logging.error(f"Error loading employee tickets: {e}")
        return jsonify({'tickets': []})

@app.route('/api/employee/induction')
@login_required
def employee_induction():
    try:
        query = """
        SELECT title, description, added_on
        FROM induction_content
        ORDER BY added_on DESC
        """
        content = db.execute_query(query)
        
        formatted_content = []
        for item in content or []:
            formatted_content.append({
                'title': item['title'],
                'description': item['description'],
                'file_path': None  # Add file path logic if needed
            })
        
        return jsonify({'content': formatted_content})
    except Exception as e:
        logging.error(f"Error loading induction content: {e}")
        return jsonify({'content': []})

# ==================== HR PORTAL ====================

@app.route('/hr-portal')
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def hr_portal():
    return render_template('hr_portal.html', user_name=session.get('user_name'))

@app.route('/api/hr/dashboard-stats')
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def hr_dashboard_stats():
    try:
        # Get total employees
        total_employees = db.execute_query("SELECT COUNT(*) as count FROM employee WHERE status = 'active'")
        
        # Get pending leaves
        pending_leaves = db.execute_query("SELECT COUNT(*) as count FROM leave_requests WHERE status = 'Pending'")
        
        # Get pending timesheets
        pending_timesheets = db.execute_query("""
            SELECT COUNT(*) as count FROM timesheet t
            LEFT JOIN timesheet_approvals ta ON t.timesheet_id = ta.timesheet_id
            WHERE ta.status IS NULL OR ta.status = 'Pending'
        """)
        
        # Get active jobs
        active_jobs = db.execute_query("SELECT COUNT(*) as count FROM job_postings")
        
        return jsonify({
            'total_employees': total_employees[0]['count'] if total_employees else 0,
            'pending_leaves': pending_leaves[0]['count'] if pending_leaves else 0,
            'pending_timesheets': pending_timesheets[0]['count'] if pending_timesheets else 0,
            'active_jobs': active_jobs[0]['count'] if active_jobs else 0
        })
    except Exception as e:
        logging.error(f"Error loading HR dashboard stats: {e}")
        return jsonify({'error': 'Failed to load dashboard stats'}), 500

@app.route('/api/hr/employees')
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def hr_employees():
    try:
        query = """
        SELECT employee_id, first_name, last_name, email, department, role_title
        FROM employee
        WHERE status = 'active'
        ORDER BY first_name, last_name
        """
        employees = db.execute_query(query)
        
        return jsonify({'employees': employees or []})
    except Exception as e:
        logging.error(f"Error loading employees: {e}")
        return jsonify({'employees': []})

@app.route('/hr/add-employee', methods=['POST'])
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def add_employee():
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        contact_number = request.form.get('contact_number')
        department = request.form.get('department')
        role_title = request.form.get('role_title')
        salary = request.form.get('salary')
        location = request.form.get('location')
        
        # Insert employee
        emp_query = """
        INSERT INTO employee (first_name, last_name, email, contact_number, department, 
                            role_title, salary, location, joined_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'active')
        """
        db.execute_query(emp_query, (first_name, last_name, email, contact_number, 
                                    department, role_title, salary, location))
        
        # Get the new employee ID
        emp_id_query = "SELECT employee_id FROM employee WHERE email = %s"
        emp_result = db.execute_query(emp_id_query, (email,))
        
        if emp_result:
            employee_id = emp_result[0]['employee_id']
            
            # Create user account with default password
            default_password = f"{first_name}@123"
            user_query = """
            INSERT INTO user_accounts (employee_id, email, password, is_temp_password)
            VALUES (%s, %s, %s, 1)
            """
            db.execute_query(user_query, (employee_id, email, default_password))
            
            # Log activity
            log_user_activity(session['user_id'], 'Employee Added', f'Added employee: {first_name} {last_name}', db)
            
            flash(f'Employee added successfully. Default password: {default_password}', 'success')
        else:
            flash('Error creating employee account', 'error')
            
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        logging.error(f"Error adding employee: {e}")
        flash('Error adding employee', 'error')
        return redirect(url_for('hr_portal'))

@app.route('/api/hr/timesheet-requests')
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def hr_timesheet_requests():
    try:
        query = """
        SELECT t.timesheet_id, t.work_date, t.hours_logged, t.description,
               e.first_name, e.last_name, p.project_name,
               COALESCE(ta.status, 'Pending') as status
        FROM timesheet t
        JOIN employee e ON t.employee_id = e.employee_id
        LEFT JOIN project p ON t.project_id = p.project_id
        LEFT JOIN timesheet_approvals ta ON t.timesheet_id = ta.timesheet_id
        WHERE COALESCE(ta.status, 'Pending') = 'Pending'
        ORDER BY t.work_date DESC
        """
        requests = db.execute_query(query)
        
        formatted_requests = []
        for req in requests or []:
            formatted_requests.append({
                'timesheet_id': req['timesheet_id'],
                'first_name': req['first_name'],
                'last_name': req['last_name'],
                'work_date': req['work_date'].strftime('%Y-%m-%d') if req['work_date'] else '',
                'hours_logged': float(req['hours_logged']) if req['hours_logged'] else 0,
                'project_name': req['project_name'],
                'status': req['status']
            })
        
        return jsonify({'timesheet_requests': formatted_requests})
    except Exception as e:
        logging.error(f"Error loading timesheet requests: {e}")
        return jsonify({'timesheet_requests': []})

@app.route('/hr/approve-timesheet', methods=['POST'])
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def approve_timesheet():
    try:
        timesheet_id = request.form.get('timesheet_id')
        action = request.form.get('action')
        
        status = 'Approved' if action == 'approve' else 'Rejected'
        
        # Insert or update approval record
        query = """
        INSERT INTO timesheet_approvals (timesheet_id, employee_id, approved_by, status, approved_at)
        SELECT t.employee_id, t.employee_id, %s, %s, NOW()
        FROM timesheet t WHERE t.timesheet_id = %s
        ON DUPLICATE KEY UPDATE
        approved_by = %s, status = %s, approved_at = NOW()
        """
        db.execute_query(query, (session['user_id'], status, timesheet_id, session['user_id'], status))
        
        # Log activity
        log_user_activity(session['user_id'], f'Timesheet {status}', f'Timesheet ID: {timesheet_id}', db)
        
        flash(f'Timesheet {status.lower()} successfully', 'success')
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        logging.error(f"Error approving timesheet: {e}")
        flash('Error processing timesheet approval', 'error')
        return redirect(url_for('hr_portal'))

@app.route('/api/hr/hr-tickets')
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def hr_tickets():
    try:
        query = """
        SELECT t.ticket_id, t.subject, t.description as issue_description, t.severity_level as severity,
               t.status, t.submitted_on as created_date, t.women_safety,
               e.first_name, e.last_name
        FROM tickets t
        JOIN employee e ON t.employee_id = e.employee_id
        WHERE t.department = 'HR'
        ORDER BY t.submitted_on DESC
        """
        tickets = db.execute_query(query)
        
        formatted_tickets = []
        for ticket in tickets or []:
            formatted_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'subject': ticket['subject'],
                'issue_description': ticket['issue_description'],
                'severity': ticket['severity'],
                'status': ticket['status'],
                'created_date': ticket['created_date'].strftime('%Y-%m-%d') if ticket['created_date'] else '',
                'women_safety': bool(ticket['women_safety']),
                'first_name': ticket['first_name'],
                'last_name': ticket['last_name']
            })
        
        return jsonify({'tickets': formatted_tickets})
    except Exception as e:
        logging.error(f"Error loading HR tickets: {e}")
        return jsonify({'tickets': []})

@app.route('/hr/update-ticket-status', methods=['POST'])
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def update_ticket_status():
    try:
        ticket_id = request.form.get('ticket_id')
        status = request.form.get('status')
        resolution = request.form.get('resolution')
        
        # Update ticket status
        query = "UPDATE tickets SET status = %s WHERE ticket_id = %s"
        db.execute_query(query, (status, ticket_id))
        
        # Log activity
        log_user_activity(session['user_id'], f'Ticket {status}', f'Ticket ID: {ticket_id}', db)
        
        flash(f'Ticket status updated to {status}', 'success')
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        logging.error(f"Error updating ticket status: {e}")
        flash('Error updating ticket status', 'error')
        return redirect(url_for('hr_portal'))

@app.route('/api/hr/job-postings')
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def hr_job_postings():
    try:
        query = """
        SELECT jp.job_id, jp.position_name as job_title, jp.level, jp.job_location,
               jp.skills_required, jp.salary, jp.job_description,
               'IT' as department, 'Full-time' as employment_type,
               DATE(NOW()) as created_date, NULL as application_deadline,
               'Active' as status,
               (SELECT COUNT(*) FROM job_applications ja WHERE ja.job_id = jp.job_id) as application_count
        FROM job_postings jp
        ORDER BY jp.job_id DESC
        """
        postings = db.execute_query(query)
        
        formatted_postings = []
        for posting in postings or []:
            formatted_postings.append({
                'job_id': posting['job_id'],
                'job_title': posting['job_title'],
                'department': posting['department'],
                'employment_type': posting['employment_type'],
                'job_description': posting['job_description'],
                'created_date': posting['created_date'].strftime('%Y-%m-%d') if posting['created_date'] else '',
                'application_deadline': posting['application_deadline'],
                'status': posting['status'],
                'application_count': posting['application_count']
            })
        
        return jsonify({'job_postings': formatted_postings})
    except Exception as e:
        logging.error(f"Error loading job postings: {e}")
        return jsonify({'job_postings': []})

@app.route('/hr/create-job', methods=['POST'])
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def create_job():
    try:
        position_name = request.form.get('position_name')
        level = request.form.get('level')
        job_location = request.form.get('job_location')
        salary = request.form.get('salary')
        skills_required = request.form.get('skills_required')
        job_description = request.form.get('job_description')
        
        # Insert job posting
        query = """
        INSERT INTO job_postings (position_name, level, job_location, skills_required, 
                                salary, job_description, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        db.execute_query(query, (position_name, level, job_location, skills_required, 
                               salary, job_description, session['user_id']))
        
        # Log activity
        log_user_activity(session['user_id'], 'Job Posted', f'Job posting: {position_name}', db)
        
        flash('Job posting created successfully', 'success')
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        logging.error(f"Error creating job posting: {e}")
        flash('Error creating job posting', 'error')
        return redirect(url_for('hr_portal'))

@app.route('/api/hr/job-applications')
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def hr_job_applications():
    try:
        query = """
        SELECT ja.application_id, jp.position_name as job_title,
               e.first_name, e.last_name, ja.status,
               DATE(NOW()) as application_date
        FROM job_applications ja
        JOIN job_postings jp ON ja.job_id = jp.job_id
        JOIN employee e ON ja.employee_id = e.employee_id
        ORDER BY ja.application_id DESC
        """
        applications = db.execute_query(query)
        
        formatted_applications = []
        for app in applications or []:
            formatted_applications.append({
                'application_id': app['application_id'],
                'job_title': app['job_title'],
                'first_name': app['first_name'],
                'last_name': app['last_name'],
                'status': app['status'],
                'application_date': app['application_date'].strftime('%Y-%m-%d') if app['application_date'] else ''
            })
        
        return jsonify({'applications': formatted_applications})
    except Exception as e:
        logging.error(f"Error loading job applications: {e}")
        return jsonify({'applications': []})

@app.route('/hr/update-application-status', methods=['POST'])
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def update_application_status():
    try:
        application_id = request.form.get('application_id')
        status = request.form.get('status')
        
        # Update application status
        query = "UPDATE job_applications SET status = %s WHERE application_id = %s"
        db.execute_query(query, (status, application_id))
        
        # Log activity
        log_user_activity(session['user_id'], f'Application {status}', f'Application ID: {application_id}', db)
        
        flash(f'Application status updated to {status}', 'success')
        return redirect(url_for('hr_portal'))
        
    except Exception as e:
        logging.error(f"Error updating application status: {e}")
        flash('Error updating application status', 'error')
        return redirect(url_for('hr_portal'))

# ==================== CAREER PORTAL ====================

@app.route('/career-portal')
@login_required
def career_portal():
    return render_template('career_portal.html', user_name=session.get('user_name'))

@app.route('/api/career/courses')
@login_required
def career_courses():
    try:
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        # Base query
        query = """
        SELECT cc.course_id, cc.course_name, cc.description, cc.skill_category,
               cc.difficulty_level, cc.duration_hours, cc.passing_score,
               bc.badge_name,
               COUNT(ca.attempt_id) as total_attempts,
               MAX(ca.score) as best_score,
               MAX(CASE WHEN ca.passed = 1 THEN 1 ELSE 0 END) as has_passed
        FROM course_catalog cc
        LEFT JOIN badge_catalog bc ON cc.badge_id = bc.badge_id
        LEFT JOIN course_attempts ca ON cc.course_id = ca.course_id AND ca.employee_id = %s
        WHERE cc.is_active = 1
        """
        params = [session['user_id']]
        
        if search:
            query += " AND (cc.course_name LIKE %s OR cc.description LIKE %s)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        if category:
            query += " AND cc.skill_category = %s"
            params.append(category)
        
        query += " GROUP BY cc.course_id ORDER BY cc.course_name"
        
        courses = db.execute_query(query, params)
        
        # Get categories
        cat_query = "SELECT DISTINCT skill_category FROM course_catalog WHERE is_active = 1"
        categories = db.execute_query(cat_query)
        category_list = [cat['skill_category'] for cat in categories or []]
        
        return jsonify({
            'courses': courses or [],
            'categories': category_list
        })
    except Exception as e:
        logging.error(f"Error loading courses: {e}")
        return jsonify({'courses': [], 'categories': []})

@app.route('/api/career/course/<int:course_id>')
@login_required
def career_course_detail(course_id):
    try:
        # Get course details
        course_query = """
        SELECT cc.course_id, cc.course_name, cc.description, cc.skill_category,
               cc.difficulty_level, cc.duration_hours, cc.passing_score,
               bc.badge_name
        FROM course_catalog cc
        LEFT JOIN badge_catalog bc ON cc.badge_id = bc.badge_id
        WHERE cc.course_id = %s AND cc.is_active = 1
        """
        course_result = db.execute_query(course_query, (course_id,))
        
        if not course_result:
            return jsonify({'error': 'Course not found'}), 404
        
        course = course_result[0]
        
        # Get user's attempts
        attempts_query = """
        SELECT score, passed, attempt_date
        FROM course_attempts
        WHERE course_id = %s AND employee_id = %s
        ORDER BY attempt_date DESC
        """
        attempts = db.execute_query(attempts_query, (course_id, session['user_id']))
        
        # Check if user has the badge
        badge_query = """
        SELECT 1 FROM employee_badges eb
        JOIN badge_catalog bc ON eb.badge_id = bc.badge_id
        JOIN course_catalog cc ON bc.badge_id = cc.badge_id
        WHERE cc.course_id = %s AND eb.employee_id = %s
        """
        has_badge = bool(db.execute_query(badge_query, (course_id, session['user_id'])))
        
        formatted_attempts = []
        for attempt in attempts or []:
            formatted_attempts.append({
                'score': attempt['score'],
                'passed': bool(attempt['passed']),
                'attempt_date': attempt['attempt_date'].strftime('%Y-%m-%d') if attempt['attempt_date'] else ''
            })
        
        return jsonify({
            'course': course,
            'attempts': formatted_attempts,
            'has_badge': has_badge
        })
    except Exception as e:
        logging.error(f"Error loading course details: {e}")
        return jsonify({'error': 'Failed to load course details'}), 500

@app.route('/api/career/course/<int:course_id>/start-exam')
@login_required
def start_exam(course_id):
    try:
        # Get course info
        course_query = """
        SELECT course_name, passing_score FROM course_catalog 
        WHERE course_id = %s AND is_active = 1
        """
        course_result = db.execute_query(course_query, (course_id,))
        
        if not course_result:
            return jsonify({'error': 'Course not found'}), 404
        
        course = course_result[0]
        
        # Get random 20 questions
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
    except Exception as e:
        logging.error(f"Error starting exam: {e}")
        return jsonify({'error': 'Failed to start exam'}), 500

@app.route('/api/career/course/<int:course_id>/submit-exam', methods=['POST'])
@login_required
def submit_exam(course_id):
    try:
        data = request.get_json()
        answers = data.get('answers', {})
        
        # Get course info and correct answers
        course_query = """
        SELECT cc.course_name, cc.passing_score, cc.badge_id
        FROM course_catalog cc
        WHERE cc.course_id = %s AND cc.is_active = 1
        """
        course_result = db.execute_query(course_query, (course_id,))
        
        if not course_result:
            return jsonify({'error': 'Course not found'}), 404
        
        course = course_result[0]
        
        # Get correct answers for submitted questions
        question_ids = list(answers.keys())
        if not question_ids:
            return jsonify({'error': 'No answers provided'}), 400
        
        placeholders = ','.join(['%s'] * len(question_ids))
        correct_query = f"""
        SELECT question_id, correct_answer
        FROM course_questions
        WHERE question_id IN ({placeholders})
        """
        correct_answers = db.execute_query(correct_query, question_ids)
        
        # Calculate score
        correct_count = 0
        total_questions = len(correct_answers)
        
        correct_dict = {str(q['question_id']): q['correct_answer'] for q in correct_answers}
        
        for question_id, user_answer in answers.items():
            if correct_dict.get(question_id) == user_answer:
                correct_count += 1
        
        score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
        passed = score >= course['passing_score']
        
        # Save attempt
        attempt_query = """
        INSERT INTO course_attempts (employee_id, course_id, score, total_questions, passed, answers_json)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        db.execute_query(attempt_query, (session['user_id'], course_id, score, total_questions, 
                                       passed, json.dumps(answers)))
        
        # Award badge if passed and not already awarded
        badge_awarded = False
        if passed and course['badge_id']:
            # Check if badge already exists
            existing_badge = db.execute_query("""
                SELECT 1 FROM employee_badges 
                WHERE employee_id = %s AND badge_id = %s
            """, (session['user_id'], course['badge_id']))
            
            if not existing_badge:
                # Award badge
                db.execute_query("""
                    INSERT INTO employee_badges (employee_id, badge_id)
                    VALUES (%s, %s)
                """, (session['user_id'], course['badge_id']))
                badge_awarded = True
        
        # Log activity
        log_user_activity(session['user_id'], f'Exam {"Passed" if passed else "Failed"}', 
                         f'Course: {course["course_name"]}, Score: {score}%', db)
        
        return jsonify({
            'score': score,
            'correct_answers': correct_count,
            'total_questions': total_questions,
            'passing_score': course['passing_score'],
            'passed': passed,
            'badge_awarded': badge_awarded
        })
    except Exception as e:
        logging.error(f"Error submitting exam: {e}")
        return jsonify({'error': 'Failed to submit exam'}), 500

@app.route('/api/career/badges')
@login_required
def career_badges():
    try:
        # Get earned badges
        earned_query = """
        SELECT bc.badge_name, bc.description, eb.awarded_on as earned_date
        FROM employee_badges eb
        JOIN badge_catalog bc ON eb.badge_id = bc.badge_id
        WHERE eb.employee_id = %s
        ORDER BY eb.awarded_on DESC
        """
        earned_badges = db.execute_query(earned_query, (session['user_id'],))
        
        # Get available badges (not earned)
        available_query = """
        SELECT bc.badge_name, bc.description
        FROM badge_catalog bc
        WHERE bc.badge_id NOT IN (
            SELECT badge_id FROM employee_badges WHERE employee_id = %s
        )
        ORDER BY bc.badge_name
        """
        available_badges = db.execute_query(available_query, (session['user_id'],))
        
        formatted_earned = []
        for badge in earned_badges or []:
            formatted_earned.append({
                'badge_name': badge['badge_name'],
                'description': badge['description'],
                'earned_date': badge['earned_date'].strftime('%Y-%m-%d') if badge['earned_date'] else ''
            })
        
        return jsonify({
            'earned_badges': formatted_earned,
            'available_badges': available_badges or []
        })
    except Exception as e:
        logging.error(f"Error loading badges: {e}")
        return jsonify({'earned_badges': [], 'available_badges': []})

@app.route('/api/career/my-attempts')
@login_required
def career_my_attempts():
    try:
        query = """
        SELECT ca.score, ca.passed, ca.attempt_date,
               cc.course_name, cc.skill_category,
               bc.badge_name
        FROM course_attempts ca
        JOIN course_catalog cc ON ca.course_id = cc.course_id
        LEFT JOIN badge_catalog bc ON cc.badge_id = bc.badge_id
        WHERE ca.employee_id = %s
        ORDER BY ca.attempt_date DESC
        """
        attempts = db.execute_query(query, (session['user_id'],))
        
        formatted_attempts = []
        for attempt in attempts or []:
            formatted_attempts.append({
                'course_name': attempt['course_name'],
                'skill_category': attempt['skill_category'],
                'score': attempt['score'],
                'passed': bool(attempt['passed']),
                'attempt_date': attempt['attempt_date'].strftime('%Y-%m-%d') if attempt['attempt_date'] else '',
                'badge_name': attempt['badge_name']
            })
        
        return jsonify({'attempts': formatted_attempts})
    except Exception as e:
        logging.error(f"Error loading attempts: {e}")
        return jsonify({'attempts': []})

@app.route('/api/career/search-skills')
@login_required
@role_required(['hr', 'manager', 'ceo', 'cto'])
def search_skills():
    try:
        skill = request.args.get('skill', '')
        
        if not skill:
            return jsonify({'employees': []})
        
        # Search for employees with badges related to the skill
        query = """
        SELECT DISTINCT e.employee_id, e.first_name, e.last_name, e.department, e.role_title,
               GROUP_CONCAT(bc.badge_name) as badges
        FROM employee e
        LEFT JOIN employee_badges eb ON e.employee_id = eb.employee_id
        LEFT JOIN badge_catalog bc ON eb.badge_id = bc.badge_id
        WHERE e.status = 'active' AND (
            bc.badge_name LIKE %s OR
            bc.description LIKE %s OR
            e.role_title LIKE %s
        )
        GROUP BY e.employee_id
        ORDER BY e.first_name, e.last_name
        """
        employees = db.execute_query(query, (f'%{skill}%', f'%{skill}%', f'%{skill}%'))
        
        return jsonify({'employees': employees or []})
    except Exception as e:
        logging.error(f"Error searching skills: {e}")
        return jsonify({'employees': []})

# ==================== IT PORTAL ====================

@app.route('/it-portal')
@login_required
@role_required(['it', 'ceo', 'cto'])
def it_portal():
    return render_template('it_portal.html')

@app.route('/api/it/dashboard-stats')
@login_required
@role_required(['it', 'ceo', 'cto'])
def it_dashboard_stats():
    try:
        # Get open tickets
        open_tickets = db.execute_query("SELECT COUNT(*) as count FROM tickets WHERE status IN ('Open', 'In Progress') AND department = 'IT'")
        
        # Get total devices
        total_devices = db.execute_query("SELECT COUNT(*) as count FROM device_inventory")
        
        # Get available devices
        available_devices = db.execute_query("SELECT COUNT(*) as count FROM device_inventory WHERE status = 'Available'")
        
        # Get devices under repair
        pending_repairs = db.execute_query("SELECT COUNT(*) as count FROM device_inventory WHERE status = 'Under Repair'")
        
        return jsonify({
            'open_tickets': open_tickets[0]['count'] if open_tickets else 0,
            'total_devices': total_devices[0]['count'] if total_devices else 0,
            'available_devices': available_devices[0]['count'] if available_devices else 0,
            'pending_repairs': pending_repairs[0]['count'] if pending_repairs else 0
        })
    except Exception as e:
        logging.error(f"Error loading IT dashboard stats: {e}")
        return jsonify({'error': 'Failed to load dashboard stats'}), 500

@app.route('/api/it/tickets')
@login_required
@role_required(['it', 'ceo', 'cto'])
def it_tickets():
    try:
        query = """
        SELECT t.ticket_id, t.subject, t.description as issue_description, t.severity_level as severity,
               t.status, t.submitted_on,
               e.first_name, e.last_name
        FROM tickets t
        JOIN employee e ON t.employee_id = e.employee_id
        WHERE t.department = 'IT'
        ORDER BY t.submitted_on DESC
        """
        tickets = db.execute_query(query)
        
        formatted_tickets = []
        for ticket in tickets or []:
            formatted_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'subject': ticket['subject'],
                'issue_description': ticket['issue_description'],
                'severity': ticket['severity'],
                'status': ticket['status'],
                'submitted_on': ticket['submitted_on'].strftime('%Y-%m-%d') if ticket['submitted_on'] else '',
                'first_name': ticket['first_name'],
                'last_name': ticket['last_name']
            })
        
        return jsonify({'tickets': formatted_tickets})
    except Exception as e:
        logging.error(f"Error loading IT tickets: {e}")
        return jsonify({'tickets': []})

@app.route('/it/update-ticket', methods=['POST'])
@login_required
@role_required(['it', 'ceo', 'cto'])
def it_update_ticket():
    try:
        ticket_id = request.form.get('ticket_id')
        status = request.form.get('status')
        
        # Update ticket status
        query = "UPDATE tickets SET status = %s WHERE ticket_id = %s"
        db.execute_query(query, (status, ticket_id))
        
        # Log activity
        log_user_activity(session['user_id'], f'IT Ticket {status}', f'Ticket ID: {ticket_id}', db)
        
        flash(f'Ticket status updated to {status}', 'success')
        return redirect(url_for('it_portal'))
        
    except Exception as e:
        logging.error(f"Error updating IT ticket: {e}")
        flash('Error updating ticket status', 'error')
        return redirect(url_for('it_portal'))

@app.route('/api/it/devices')
@login_required
@role_required(['it', 'ceo', 'cto'])
def it_devices():
    try:
        query = """
        SELECT di.device_id as asset_id, di.device_type, di.brand, di.model, 
               di.serial_number, di.status,
               CASE 
                   WHEN di.assigned_to IS NOT NULL THEN CONCAT(e.first_name, ' ', e.last_name)
                   ELSE NULL
               END as assigned_to
        FROM device_inventory di
        LEFT JOIN employee e ON di.assigned_to = e.employee_id
        ORDER BY di.device_type, di.brand, di.model
        """
        devices = db.execute_query(query)
        
        return jsonify({'devices': devices or []})
    except Exception as e:
        logging.error(f"Error loading devices: {e}")
        return jsonify({'devices': []})

@app.route('/it/add-device', methods=['POST'])
@login_required
@role_required(['it', 'ceo', 'cto'])
def add_device():
    try:
        device_type = request.form.get('device_type')
        brand = request.form.get('brand')
        model = request.form.get('model')
        serial_number = request.form.get('serial_number')
        
        # Insert device
        query = """
        INSERT INTO device_inventory (device_type, brand, model, serial_number, status)
        VALUES (%s, %s, %s, %s, 'Available')
        """
        db.execute_query(query, (device_type, brand, model, serial_number))
        
        # Log activity
        log_user_activity(session['user_id'], 'Device Added', f'{device_type}: {brand} {model}', db)
        
        flash('Device added successfully', 'success')
        return redirect(url_for('it_portal'))
        
    except Exception as e:
        logging.error(f"Error adding device: {e}")
        flash('Error adding device', 'error')
        return redirect(url_for('it_portal'))

@app.route('/it/assign-device', methods=['POST'])
@login_required
@role_required(['it', 'ceo', 'cto'])
def assign_device():
    try:
        asset_id = request.form.get('asset_id')
        employee_id = request.form.get('employee_id')
        
        # Update device assignment
        query = """
        UPDATE device_inventory 
        SET assigned_to = %s, status = 'Assigned'
        WHERE device_id = %s
        """
        db.execute_query(query, (employee_id, asset_id))
        
        # Log activity
        log_user_activity(session['user_id'], 'Device Assigned', f'Device ID: {asset_id} to Employee ID: {employee_id}', db)
        
        flash('Device assigned successfully', 'success')
        return redirect(url_for('it_portal'))
        
    except Exception as e:
        logging.error(f"Error assigning device: {e}")
        flash('Error assigning device', 'error')
        return redirect(url_for('it_portal'))

@app.route('/api/it/troubleshooting-docs')
@login_required
@role_required(['it', 'ceo', 'cto'])
def it_troubleshooting_docs():
    try:
        query = """
        SELECT doc_id, title, category, problem_description, solution_steps, created_at
        FROM troubleshooting_docs
        ORDER BY created_at DESC
        """
        docs = db.execute_query(query)
        
        formatted_docs = []
        for doc in docs or []:
            formatted_docs.append({
                'doc_id': doc['doc_id'],
                'title': doc['title'],
                'category': doc['category'],
                'problem_description': doc['problem_description'],
                'solution_steps': doc['solution_steps'],
                'created_at': doc['created_at'].strftime('%Y-%m-%d') if doc['created_at'] else ''
            })
        
        return jsonify({'docs': formatted_docs})
    except Exception as e:
        logging.error(f"Error loading troubleshooting docs: {e}")
        return jsonify({'docs': []})

@app.route('/it/add-troubleshooting', methods=['POST'])
@login_required
@role_required(['it', 'ceo', 'cto'])
def add_troubleshooting():
    try:
        title = request.form.get('title')
        category = request.form.get('category')
        problem_description = request.form.get('problem_description')
        solution_steps = request.form.get('solution_steps')
        
        # Insert troubleshooting doc
        query = """
        INSERT INTO troubleshooting_docs (title, category, problem_description, solution_steps, created_by)
        VALUES (%s, %s, %s, %s, %s)
        """
        db.execute_query(query, (title, category, problem_description, solution_steps, session['user_id']))
        
        # Log activity
        log_user_activity(session['user_id'], 'Troubleshooting Doc Added', f'Title: {title}', db)
        
        flash('Troubleshooting guide added successfully', 'success')
        return redirect(url_for('it_portal'))
        
    except Exception as e:
        logging.error(f"Error adding troubleshooting doc: {e}")
        flash('Error adding troubleshooting guide', 'error')
        return redirect(url_for('it_portal'))

# ==================== LEGACY ROUTES (Keep existing functionality) ====================

@app.route('/read-more')
def read_more():
    return render_template('readmore.html')

@app.route('/ai-ml')
def ai_ml():
    return render_template('ai_ml.html')

@app.route('/application-services')
def application_services():
    return render_template('application_services.html')

@app.route('/cloud-services')
def cloud_services():
    return render_template('cloud_services.html')

@app.route('/data-analytics')
def data_analytics():
    return render_template('data_analytics.html')

@app.route('/devsecops')
def devsecops():
    return render_template('devsecops.html')

@app.route('/induction')
def induction_kit():
    return render_template('induction.html')

@app.route('/company-overview')
def company_overview():
    return render_template('company-overview.html')

@app.route('/code-of-conduct')
def code_of_conduct():
    return render_template('code-of-conduct.html')

@app.route('/it-security')
def it_security():
    return render_template('it-security.html')

@app.route('/work-schedule-attendance')
def work_schedule_attendance():
    return render_template('work-schedule-attendance.html')

# ==================== API CHAT ROUTE ====================

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        # Simple chatbot responses
        responses = {
            'hello': 'Hello! How can I help you with NexIQoN services today?',
            'services': 'We offer AI & ML, Application Services, Cloud Services, Data Analytics, and DevSecOps.',
            'contact': 'You can contact us through the contact form on our website.',
            'careers': 'Visit our Career Portal to explore job opportunities and courses.',
            'help': 'I can help you with information about our services, careers, and general inquiries.'
        }
        
        # Simple keyword matching
        response = "I'm here to help! You can ask me about our services, careers, or general information about NexIQoN."
        for keyword, reply in responses.items():
            if keyword.lower() in prompt.lower():
                response = reply
                break
        
        return response
    except Exception as e:
        logging.error(f"Error in chat API: {e}")
        return "Sorry, I'm having trouble responding right now. Please try again later."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)