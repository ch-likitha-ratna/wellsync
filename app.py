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

# Following route is for the induction kit file - Samvedha
@app.route('/induction')
def induction_kit():
    return render_template('induction.html')

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
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = psycopg2.connect(
                dbname="NexIQon",
                user="sanjay",        # 🔁 Replace with your actual PostgreSQL username
                password="",# 🔁 Replace with your actual PostgreSQL password
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE email = %s", (email,))
            result = cur.fetchone()
            cur.close()
            conn.close()
        except Exception as e:
            flash(f'Database connection error: {e}', 'error')
            return render_template('signin.html')

        if result:
            db_password = result[0]
            if db_password == password:  # You can add hashing later
                session['user'] = {'email': email}
                flash('Login successful!', 'success')
                return redirect(url_for('access_page'))  # Or another welcome page
            else:
                flash('Invalid password', 'error')
        else:
            flash('Email not found or not a member', 'error')

    return render_template('signin.html')


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



@app.route('/hr-login', methods=['GET', 'POST'])
def hr_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = psycopg2.connect(
                dbname="NexIQon",
                user="sanjay",        
                password="",  # replace with your actual password
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute("SELECT password, role FROM users WHERE email = %s", (email,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                db_password, role = result
                if password == db_password and role == 'hr':
                    session['user'] = {'email': email, 'role': role}
                    flash('Login successful! Welcome HR.', 'success')
                    return redirect('/hr-portal')  # HR dashboard route
                else:
                    flash('Access denied: Not authorized as HR.', 'error')
            else:
                flash('Invalid credentials.', 'error')

        except Exception as e:
            flash(f'Database connection error: {e}', 'error')

    return render_template('hr_login.html')


@app.route('/hr-portal')
def hr_portal():
    if session.get('user') and session['user']['role'] == 'hr':
        return render_template('hr_portal.html')
    else:
        flash("Unauthorized access", "error")
        return redirect('/hr-login')


@app.route('/employee-login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            conn = psycopg2.connect(
                dbname="NexIQon",
                user="sanjay",
                password="",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute("SELECT password, role FROM users WHERE email = %s", (email,))
            result = cur.fetchone()
            cur.close()
            conn.close()
        except Exception as e:
            flash(f'Database error: {e}', 'error')
            return render_template('employee_login.html')

        if result:
            db_password, role = result
            if password == db_password:
                if role == 'employee':
                    session['user'] = {'email': email, 'role': role}
                    flash('Login successful!', 'success')
                    return redirect('/employee-portal')
                else:
                    flash('Access denied: Not an employee', 'error')
            else:
                flash('Invalid password', 'error')
        else:
            flash('Email not found', 'error')

    # Only render login page if GET or after invalid POST
    return render_template('employee_login.html')

@app.route('/employee-dashboard')
def employee_dashboard():
    if 'user' not in session or session['user'].get('role') != 'employee':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('employee_login'))

    return render_template('employee_dashboard.html')


@app.route('/employee-portal')
def employee_portal():
    if 'user' in session and session['user'].get('role') == 'employee':
        return render_template('employee_portal.html')
    else:
        flash('Unauthorized access', 'error')
        return redirect('/employee-login')

@app.route('/manage-employees')
def manage_employees():
    try:
        conn = psycopg2.connect(
            dbname="NexIQon",
            user="sanjay",
            password="",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT id, email, role FROM users WHERE role = 'employee'")
        rows = cur.fetchall()
        employees = [{'id': r[0], 'email': r[1], 'role': r[2]} for r in rows]
        cur.close()
        conn.close()
    except Exception as e:
        flash(f'Error fetching employee data: {e}', 'error')
        employees = []

    return render_template('manage_employees.html', employees=employees)


@app.route('/request-leave', methods=['GET', 'POST'])
def request_leave():
    if request.method == 'POST':
        email = session.get('user_email')  # store email in session during login
        leave_date = request.form['leave_date']
        leave_days = int(request.form['leave_days'])
        leave_type = request.form['leave_type']
        reason = request.form['reason']

        conn = psycopg2.connect(...)  # your config
        cur = conn.cursor()

        # Check how many leaves taken this month
        cur.execute("""
            SELECT SUM(leave_days) FROM leave_requests 
            WHERE employee_email = %s 
              AND EXTRACT(MONTH FROM leave_date) = EXTRACT(MONTH FROM CURRENT_DATE)
              AND status = 'Approved'
        """, (email,))
        total_taken = cur.fetchone()[0] or 0

        if total_taken + leave_days > 5:
            flash("You’ve exceeded the monthly leave quota (5 days).", "danger")
        else:
            cur.execute("""
                INSERT INTO leave_requests 
                (employee_email, leave_date, leave_days, leave_type, reason) 
                VALUES (%s, %s, %s, %s, %s)
            """, (email, leave_date, leave_days, leave_type, reason))
            conn.commit()
            flash("Leave request submitted!", "success")

        cur.close()
        conn.close()

    return render_template("employee_leave_form.html")



@app.route('/hr/leave-requests', methods=['GET', 'POST'])
def hr_leave_requests():
    if 'user' not in session:
        return redirect(url_for('signin'))

    email = session['user'].get('email')

    conn = psycopg2.connect(
        dbname="NexIQon",
        user="sanjay",
        password="",  # Use proper credentials
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE email = %s", (email,))
    result = cur.fetchone()

    if not result or result[0] != 'hr':
        flash('Access denied: HR only', 'error')
        return redirect(url_for('signin'))

    # ✅ Process Approve/Reject Actions via POST
    if request.method == 'POST':
        req_id = request.form['req_id']
        action = request.form['action']
        cur.execute("UPDATE leave_requests SET status = %s WHERE id = %s", (action, req_id))
        conn.commit()

        cur.close()
        conn.close()

        # ✅ Redirect after POST to avoid re-submission / stale view
        return redirect(url_for('hr_leave_requests'))

    # ✅ Fetch Updated Requests
    cur.execute("SELECT * FROM leave_requests ORDER BY submitted_at DESC")
    requests = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("hr_leave_requests.html", requests=requests)

@app.route('/submit-leave', methods=['GET', 'POST'])
def submit_leave_request():
    if 'user' not in session:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        try:
            email = session['user']['email']
            leave_type = request.form['leave_type']
            reason = request.form['reason']
            num_days = int(request.form['leave_days'])

            conn = psycopg2.connect(
                dbname="NexIQon",
                user="sanjay",
                password="",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            # ✅ Check how many approved leaves the employee already has this month
            cur.execute("""
                SELECT COUNT(*) FROM leave_requests 
                WHERE employee_email = %s
                  AND EXTRACT(MONTH FROM leave_date) = EXTRACT(MONTH FROM CURRENT_DATE)
                  AND EXTRACT(YEAR FROM leave_date) = EXTRACT(YEAR FROM CURRENT_DATE)
                  AND status = 'Approved'
            """, (email,))
            approved_count = cur.fetchone()[0]

            if approved_count >= 5:
                flash("⚠️ You've already submitted 5 approved leaves this month. Further approvals may be rejected.", "warning")

            # ✅ Insert each leave date as a pending request
            for i in range(num_days):
                leave_date = request.form[f'leave_date_{i}']
                cur.execute("""
                    INSERT INTO leave_requests (employee_email, leave_date, leave_days, leave_type, reason, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (email, leave_date, 1, leave_type, reason, 'Pending'))

            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('leave_status'))

        except Exception as e:
            return f"Error: {e}"

    return render_template('submit_leave.html')

@app.route('/leave-status')
def leave_status():
    if 'user' not in session:
        return redirect(url_for('signin'))

    email = session['user']['email']

    conn = psycopg2.connect(
        dbname="NexIQon",
        user="sanjay",
        password="",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT leave_date, leave_days, leave_type, reason, status 
        FROM leave_requests 
        WHERE employee_email = %s
        ORDER BY submitted_at DESC
    """, (email,))
    leaves = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("leave_status.html", leaves=leaves)


@app.route('/submit-feedback', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        message = request.form['message']

        conn = psycopg2.connect(
            dbname="NexIQon",
            user="sanjay",
            password="",  # secure properly in prod
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO feedback (message) VALUES (%s)", (message,))
        conn.commit()
        cur.close()
        conn.close()

        # No flash here to avoid leaking to other users
        return render_template("thank_you.html")  # new page

    return render_template("submit_feedback.html")


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

@app.route('/view-feedback-responses')
def view_feedback_responses():
    conn = psycopg2.connect(
        dbname="NexIQon",
        user="sanjay",
        password="",  # Provide password if needed
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT id, message, hr_response, submitted_at FROM feedback ORDER BY submitted_at DESC")
    feedbacks = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('view_feedback.html', feedbacks=feedbacks)


@app.route('/hr-announcements', methods=['GET', 'POST'])
def hr_announcements():
    conn = psycopg2.connect(
        dbname="NexIQon",
        user="sanjay",
        password="",  # Fill in your DB password
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cur.execute("INSERT INTO announcements (title, content) VALUES (%s, %s)", 
                    (title, content))
        conn.commit()
        flash("Announcement posted successfully!", "success")

    cur.execute("""
    SELECT title, content, posted_on 
    FROM announcements 
    WHERE posted_on >= NOW() - INTERVAL '30 days' 
    ORDER BY posted_on DESC
""")

    announcements = cur.fetchall()
    cur.close()
    conn.close()

    announcements_data = [
    {'title': a[0], 'content': a[1], 'date': a[2].strftime('%Y-%m-%d %H:%M')}
    for a in announcements
]


    return render_template('announcements.html', announcements=announcements_data)

@app.route('/employee-announcements')
def employee_announcements():
    conn = psycopg2.connect(
        dbname="NexIQon",
        user="sanjay",
        password="",  # your DB password
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # ✅ Only show announcements from last 30 days
    cur.execute("""
        SELECT title, content, posted_on 
        FROM announcements 
        WHERE posted_on >= NOW() - INTERVAL '30 days' 
        ORDER BY posted_on DESC
    """)
    data = cur.fetchall()
    conn.close()

    announcements = [
        {'title': d[0], 'content': d[1], 'date': d[2].strftime('%Y-%m-%d %H:%M')}
        for d in data
    ]
    return render_template("employee_announcements.html", announcements=announcements)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
