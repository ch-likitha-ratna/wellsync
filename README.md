# NexIQoN Enterprise Portal

A comprehensive full-stack enterprise portal built with Flask and modern web technologies.

## Features

### Multi-Role Access System
- **Admin Dashboard**: CEO/CTO access to all modules
- **Employee Portal**: Personal dashboard, leave management, timesheets, feedback
- **HR Management**: Employee onboarding, leave approvals, job postings, ATS
- **IT Help Desk**: Ticket management, device tracking, troubleshooting docs
- **Career Portal**: Courses, certifications, badges, job applications

### Key Functionality
- Role-based authentication and authorization
- Leave management with approval workflow
- Timesheet submission and tracking
- Anonymous feedback system
- Ticket management system
- Course catalog with exam system
- Badge and certification tracking
- Job posting and application system
- Device inventory management
- Azure Blob Storage integration for file uploads

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS (TailwindCSS), JavaScript
- **Database**: MySQL
- **Cloud Storage**: Azure Blob Storage
- **Authentication**: Session-based with role management

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Azure Storage Account (optional, for file uploads)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nexiqon-portal
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   - Create MySQL database named `nexiqon`
   - Import the existing SQL schema files
   - Run the additional tables script:
   ```bash
   mysql -u root -p nexiqon < additional_tables.sql
   ```

5. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Update the configuration values:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` with your database credentials and other settings

6. **Azure Storage Setup (Optional)**
   - Create an Azure Storage Account
   - Create a container named `nexiqon-files`
   - Add the connection string to `.env`

### Running the Application

1. **Start the Flask application**
   ```bash
   python app.py
   ```

2. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Use the existing employee credentials from your database

### Default Login Credentials

Based on your existing data, you can use:
- Email: `liam.martinez@company.com` / Password: `Liam@123`
- Email: `nina.wells@company.com` / Password: `Nina@123`
- Email: `priya.sharma@company.com` / Password: `Priya@123`

## Azure Services Required

### 1. Azure Storage Account
Create a storage account for file uploads:

1. **Create Storage Account**
   - Go to Azure Portal
   - Create new Storage Account
   - Choose Standard performance tier
   - Select your preferred region

2. **Create Container**
   - In the storage account, go to Containers
   - Create a new container named `nexiqon-files`
   - Set access level to "Private"

3. **Get Connection String**
   - Go to Access Keys in your storage account
   - Copy the connection string
   - Add it to your `.env` file

### 2. Azure SQL Database (Optional)
If you want to use Azure SQL instead of local MySQL:

1. **Create Azure SQL Database**
   - Create new SQL Database in Azure
   - Import your schema
   - Update connection string in `.env`

## Project Structure

```
nexiqon-portal/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── database.py           # Database connection and utilities
├── auth.py               # Authentication and authorization
├── utils.py              # Utility functions
├── azure_storage.py      # Azure Blob Storage integration
├── requirements.txt      # Python dependencies
├── additional_tables.sql # Additional database tables
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── uploads/             # Local file uploads (if not using Azure)
└── README.md            # This file
```

## API Endpoints

### Authentication
- `POST /signin` - User login
- `GET /logout` - User logout

### Employee Portal
- `GET /employee-portal` - Employee dashboard
- `GET /api/employee/profile` - Get employee profile
- `POST /submit-leave` - Submit leave request
- `POST /employee/submit-timesheet` - Submit timesheet
- `POST /employee/submit-ticket` - Submit support ticket

### HR Management
- `GET /hr-portal` - HR dashboard
- `GET /api/hr/employees` - Get all employees
- `POST /hr/add-employee` - Add new employee
- `GET /api/hr/dashboard-stats` - Get HR statistics

### Career Portal
- `GET /career-portal` - Career dashboard
- `GET /api/career/courses` - Get available courses
- `POST /api/career/course/<id>/submit-exam` - Submit exam

### IT Help Desk
- `GET /it-portal` - IT dashboard
- `GET /api/it/tickets` - Get IT tickets
- `GET /api/it/devices` - Get device inventory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary software for NexIQoN.

## Support

For support and questions, please contact the development team.