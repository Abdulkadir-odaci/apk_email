"""
Configuration file for Auto Control Management System
"""

import os
from datetime import datetime

# Database Configuration
DATABASE_CONFIG = {
    'db_path': 'auto_control.db',
    'backup_enabled': True,
    'backup_interval_hours': 24
}

# Email Configuration (Default values - can be overridden in app)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'sender_email': '',  # Will be set through the app
    'sender_password': '',  # Will be set through the app
    'email_template_style': 'modern'  # 'modern' or 'classic'
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    'check_interval_hours': 1,  # How often to check for notifications
    'notification_days_before': 7,  # Days before control date to send notification
    'max_notifications_per_vehicle': 3,  # Maximum notifications per vehicle
    'notification_interval_days': 3,  # Days between repeated notifications
    'business_hours_only': False,  # Send notifications only during business hours
    'business_start_hour': 9,
    'business_end_hour': 17
}

# Application Configuration
APP_CONFIG = {
    'app_title': 'Auto Control Management System',
    'app_icon': '🚗',
    'page_layout': 'wide',
    'theme_color': '#2E86AB',
    'max_file_upload_size': 10,  # MB
    'session_timeout_minutes': 60
}

# Logging Configuration
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'app.log',
    'max_log_size_mb': 10,
    'backup_count': 5,
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Security Configuration
SECURITY_CONFIG = {
    'encrypt_passwords': True,
    'session_encryption': True,
    'rate_limit_enabled': True,
    'max_requests_per_minute': 60
}

# Export Configuration
EXPORT_CONFIG = {
    'allowed_formats': ['csv', 'xlsx', 'json'],
    'default_export_format': 'csv',
    'include_metadata': True
}

# Development Configuration
DEV_CONFIG = {
    'debug_mode': False,
    'auto_reload': True,
    'show_sql_queries': False,
    'mock_email_service': False  # For testing without real email
}

def load_environment_variables():
    """Load configuration from environment variables"""
    config = {}
    
    # Email configuration from environment
    config['SMTP_SERVER'] = os.getenv('SMTP_SERVER', EMAIL_CONFIG['smtp_server'])
    config['SMTP_PORT'] = int(os.getenv('SMTP_PORT', EMAIL_CONFIG['smtp_port']))
    config['SENDER_EMAIL'] = os.getenv('SENDER_EMAIL', '')
    config['SENDER_PASSWORD'] = os.getenv('SENDER_PASSWORD', '')
    
    # Database configuration
    config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', DATABASE_CONFIG['db_path'])
    
    # Notification configuration
    config['NOTIFICATION_DAYS'] = int(os.getenv('NOTIFICATION_DAYS', NOTIFICATION_CONFIG['notification_days_before']))
    config['CHECK_INTERVAL'] = int(os.getenv('CHECK_INTERVAL', NOTIFICATION_CONFIG['check_interval_hours']))
    
    # Development configuration
    config['DEBUG_MODE'] = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    config['MOCK_EMAIL'] = os.getenv('MOCK_EMAIL', 'False').lower() == 'true'
    
    return config

def get_version():
    """Get application version"""
    return "1.0.0"

def get_build_info():
    """Get build information"""
    return {
        'version': get_version(),
        'build_date': datetime.now().strftime('%Y-%m-%d'),
        'python_version': '3.8+',
        'streamlit_version': '1.28.1'
    }