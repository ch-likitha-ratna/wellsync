from flask import Flask, render_template
import os

app = Flask(__name__, template_folder=os.path.join(os.pardir, 'templates'))

# Route for the Induction Kit page
@app.route('/induction')
def induction_kit():
    return render_template('induction.html')

@app.route('/induction/company-overview')
def company_overview():
    return render_template('company-overview.html')

@app.route('/induction/code-of-conduct')
def code_of_conduct():
    return render_template('code-of-conduct.html')

@app.route('/induction/it-security')
def it_security():
    return render_template('it-security.html')

@app.route('/induction/work-schedule-attendance')
def work_schedule_attendance():
    return render_template('work-schedule-attendance.html')

if __name__ == '__main__':
    app.run(debug=True)

