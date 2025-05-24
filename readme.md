🚗 Auto Control Management System
A comprehensive Streamlit application for managing vehicle control deadlines with automated email notifications.
🌟 Features

Vehicle Management: Add, search, update, and delete vehicle records
Automated Notifications: Background service sends email reminders before control deadlines
Dashboard: Real-time overview of vehicle statuses and notification activity
Email Integration: Configurable SMTP settings with HTML email templates
Reports & Analytics: Detailed reports and statistics
Data Export: Export data in CSV format
Background Service: Automatic monitoring and notification sending

🚀 Quick Start
Prerequisites

Python 3.8 or higher
Streamlit
SQLite3 (included with Python)

Installation

Clone the repository
bashgit clone <your-repository-url>
cd auto-control-management

Install dependencies
bashpip install -r requirements.txt

Run the application
bashstreamlit run app.py

Access the application
Open your browser and go to http://localhost:8501

📧 Email Configuration
Gmail Setup (Recommended)

Enable 2-Factor Authentication on your Google account
Generate an App Password:

Go to Google Account Settings
Security → 2-Step Verification → App passwords
Select "Mail" and generate a password
Use this App Password in the application (not your regular Gmail password)


Configure in the app:

Go to "Email Configuration" page
Enter your Gmail address
Enter the App Password (16-character code)
SMTP Server: smtp.gmail.com
SMTP Port: 587



Other Email Providers

Outlook/Hotmail: smtp.live.com:587
Yahoo: smtp.mail.yahoo.com:587
Custom SMTP: Contact your email provider for settings

📱 Usage Guide
1. Initial Setup

Configure Email: Go to "Email Configuration" and set up your SMTP settings
Test Connection: Use the "Test Connection" button to verify email setup
Start Background Service: Go to "Background Service" and start the monitoring service

2. Adding Vehicles

Go to "Add Vehicle" page
Enter:

Number Plate (e.g., ABC-123)
Owner Email
Control Date


Click "Add Vehicle"

3. Monitoring

Dashboard: View overall statistics and recent activity
Background Service: Monitor automatic notification system
Reports: View detailed analytics and export data

4. Manual Operations

Search Vehicle: Find specific vehicle information
Send Test Email: Manually send notification to a vehicle owner
Bulk Notifications: Send notifications to all due vehicles at once

🏗️ Project Structure
auto-control-management/
├── app.py                 # Main Streamlit application
├── database.py           # Database management class
├── email_service.py      # Email service implementation
├── background_service.py # Background monitoring service
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── auto_control.db     # SQLite database (created automatically)
🔧 Configuration
Environment Variables
You can configure the application using environment variables:
bash# Email Configuration
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"

# Notification Settings
export NOTIFICATION_DAYS="7"
export CHECK_INTERVAL="1"

# Development
export DEBUG_MODE="false"
export MOCK_EMAIL="false"
Configuration File
Edit config.py to customize:

Notification timing: How many days before control date to send notifications
Check intervals: How often the background service checks for due vehicles
Email templates: Customize the notification email appearance
Database settings: Database path and backup options

📊 Database Schema
Vehicles Table

id: Primary key
number_plate: Vehicle number plate (unique)
owner_email: Owner's email address
control_date: Date when control is due
last_notification_sent: Timestamp of last notification
created_at: Record creation timestamp
updated_at: Record update timestamp

Email Logs Table

id: Primary key
number_plate: Vehicle number plate
email_sent_to: Recipient email
sent_at: Email sent timestamp
status: Email status (SUCCESS/FAILED/ERROR)
message: Additional message or error details

🔄 Background Service
The background service automatically:

Checks every hour for vehicles with approaching control dates
Sends email notifications 7 days before the control date
Logs all email activity for tracking and debugging
Prevents duplicate notifications by tracking when notifications were sent
Handles errors gracefully and logs failures for review

Service Management

Start Service: Begins automatic monitoring
Stop Service: Stops automatic monitoring
Manual Check: Immediately check for due notifications
View Status: Monitor service health and activity

📈 Reports & Analytics
The reports page provides:

Vehicle statistics: Total, overdue, due soon, future controls
Date distribution: Visual representation of control dates
Status breakdown: Categorized vehicle statuses
Export functionality: Download filtered data as CSV
Date range filtering: Focus on specific time periods

🔒 Security Features

No password storage: Email passwords are stored only in session memory
Input validation: All user inputs are validated and sanitized
SQL injection protection: Uses parameterized queries
Error handling: Comprehensive error handling prevents application crashes

🚀 Deployment
Local Development
bashstreamlit run app.py
Production Deployment

Streamlit Cloud:

Push to GitHub
Connect to Streamlit Cloud
Deploy directly from repository


Docker (create Dockerfile):
dockerfileFROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]

VPS/Cloud Server:

Install Python and dependencies
Use process manager like PM2 or systemd
Configure reverse proxy with Nginx



🐛 Troubleshooting
Common Issues

Email not sending:

Check SMTP credentials
Verify App Password for Gmail
Test email connection in settings


Background service not working:

Ensure email is configured first
Check service status in Background Service page
Look for error messages in the interface


Database errors:

Ensure write permissions in application directory
Check disk space
Restart application if database is locked


Performance issues:

Large number of vehicles may slow down operations
Consider adding database indexes for optimization
Monitor system resources



Logs and Debugging

Check the Streamlit terminal for error messages
Use the "Reports" page to verify data integrity
Test email functionality with the built-in test feature
Monitor background service status regularly

🤝 Contributing

Fork the repository
Create a feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
🆘 Support
If you encounter any issues or have questions:

Check the troubleshooting section above
Create an issue on GitHub
Check the application's built-in help and documentation

🔄 Updates and Maintenance
Regular Maintenance

Database Backup: Regularly backup the SQLite database file
Email Service: Monitor email sending success rates
Dependencies: Keep Python packages updated
Security: Review and update email credentials periodically

Version History

v1.0.0: Initial release with core functionality

Vehicle management
Email notifications
Background service
Reports and analytics



🎯 Future Enhancements

 SMS notifications
 Multiple notification