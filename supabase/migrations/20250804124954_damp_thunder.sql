-- Additional tables needed for the enhanced functionality

-- Anonymous feedback table
CREATE TABLE IF NOT EXISTS anonymous_feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    feedback_type ENUM('General', 'Manager', 'HR', 'Process', 'Workplace') NOT NULL,
    target_role ENUM('CEO', 'CTO', 'Manager', 'HR', 'Employee', 'IT') DEFAULT NULL,
    feedback_text TEXT NOT NULL,
    submitted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE,
    hr_response TEXT DEFAULT NULL,
    responded_at TIMESTAMP NULL,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'success', 'warning', 'error') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);

-- User activity log table
CREATE TABLE IF NOT EXISTS user_activity_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);

-- Device inventory table (enhanced from asset_inventory)
CREATE TABLE IF NOT EXISTS device_inventory (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    device_type ENUM('Laptop', 'Desktop', 'Monitor', 'Printer', 'Phone', 'Tablet', 'Other') NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    purchase_date DATE,
    warranty_expiry DATE,
    assigned_to INT DEFAULT NULL,
    status ENUM('Available', 'Assigned', 'Under Repair', 'Retired') DEFAULT 'Available',
    location VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES employee(employee_id)
);

-- HR documents table
CREATE TABLE IF NOT EXISTS hr_documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    document_type ENUM('Resume', 'Offer Letter', 'NDA', 'W4', 'I9', 'Visa', 'Other') NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    azure_blob_url VARCHAR(500),
    uploaded_by INT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_confidential BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
    FOREIGN KEY (uploaded_by) REFERENCES employee(employee_id)
);

-- Timesheet approval table
CREATE TABLE IF NOT EXISTS timesheet_approvals (
    approval_id INT AUTO_INCREMENT PRIMARY KEY,
    timesheet_id INT NOT NULL,
    employee_id INT NOT NULL,
    approved_by INT DEFAULT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    comments TEXT,
    approved_at TIMESTAMP NULL,
    FOREIGN KEY (timesheet_id) REFERENCES timesheet(timesheet_id),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
    FOREIGN KEY (approved_by) REFERENCES employee(employee_id)
);

-- Enhanced job applications table (if not exists)
CREATE TABLE IF NOT EXISTS job_applications_enhanced (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    applicant_name VARCHAR(200) NOT NULL,
    applicant_email VARCHAR(200) NOT NULL,
    applicant_phone VARCHAR(20),
    resume_path VARCHAR(500),
    cover_letter TEXT,
    status ENUM('Applied', 'Under Review', 'Interview', 'Accepted', 'Rejected') DEFAULT 'Applied',
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by INT DEFAULT NULL,
    reviewed_at TIMESTAMP NULL,
    interview_date DATETIME NULL,
    notes TEXT,
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id),
    FOREIGN KEY (reviewed_by) REFERENCES employee(employee_id)
);

-- Insert sample data for anonymous feedback
INSERT INTO anonymous_feedback (employee_id, feedback_type, target_role, feedback_text) VALUES
(24, 'Manager', 'Manager', 'Great leadership and support from the management team.'),
(25, 'HR', 'HR', 'HR processes could be more streamlined.'),
(26, 'General', NULL, 'Overall work environment is positive and collaborative.'),
(27, 'Process', NULL, 'Some processes need improvement for better efficiency.'),
(28, 'Workplace', NULL, 'Office facilities are excellent and well-maintained.');

-- Insert sample notifications
INSERT INTO notifications (employee_id, title, message, type) VALUES
(24, 'Leave Request Approved', 'Your leave request for July 1-3 has been approved.', 'success'),
(25, 'Timesheet Reminder', 'Please submit your timesheet for this week.', 'warning'),
(26, 'New Course Available', 'A new Python programming course is now available.', 'info'),
(27, 'Badge Earned', 'Congratulations! You have earned the Python Expert badge.', 'success'),
(28, 'System Maintenance', 'System maintenance scheduled for this weekend.', 'warning');

-- Insert sample device inventory
INSERT INTO device_inventory (device_type, brand, model, serial_number, assigned_to, status) VALUES
('Laptop', 'Dell', 'Latitude 7420', 'DL7420001', 24, 'Assigned'),
('Laptop', 'HP', 'EliteBook 840', 'HP840002', 25, 'Assigned'),
('Monitor', 'Samsung', '27" 4K', 'SM27K003', 26, 'Assigned'),
('Printer', 'Canon', 'ImageClass MF445dw', 'CN445004', NULL, 'Available'),
('Phone', 'iPhone', '13 Pro', 'IP13P005', 27, 'Assigned');