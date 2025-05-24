import schedule
import time
import threading
from database import DatabaseManager
from email_service import EmailService
from datetime import datetime
import streamlit as st

class BackgroundService:
    def __init__(self, email_service, database_manager):
        self.email_service = email_service
        self.db_manager = database_manager
        self.is_running = False
        self.thread = None
        self.last_check = None
        self.notification_log = []
    
    def check_and_send_notifications(self):
        """Check for vehicles due for notification and send emails"""
        try:
            self.last_check = datetime.now()
            
            # Get vehicles that need notification (7 days before control date)
            vehicles_due = self.db_manager.get_vehicles_due_for_notification(days_before=7)
            
            notifications_sent = 0
            errors = []
            
            for vehicle in vehicles_due:
                try:
                    # Send email notification
                    success, message = self.email_service.send_control_reminder(
                        vehicle['number_plate'],
                        vehicle['control_date'],
                        vehicle['owner_email']
                    )
                    
                    if success:
                        # Update notification timestamp
                        self.db_manager.update_notification_sent(vehicle['number_plate'])
                        
                        # Log successful email
                        self.db_manager.log_email(
                            vehicle['number_plate'],
                            vehicle['owner_email'],
                            'SUCCESS',
                            'Notification sent successfully'
                        )
                        
                        notifications_sent += 1
                        
                        # Add to notification log for display
                        self.notification_log.append({
                            'timestamp': datetime.now(),
                            'number_plate': vehicle['number_plate'],
                            'email': vehicle['owner_email'],
                            'status': 'SUCCESS',
                            'control_date': vehicle['control_date']
                        })
                        
                    else:
                        # Log failed email
                        self.db_manager.log_email(
                            vehicle['number_plate'],
                            vehicle['owner_email'],
                            'FAILED',
                            message
                        )
                        
                        errors.append(f"{vehicle['number_plate']}: {message}")
                        
                        self.notification_log.append({
                            'timestamp': datetime.now(),
                            'number_plate': vehicle['number_plate'],
                            'email': vehicle['owner_email'],
                            'status': 'FAILED',
                            'control_date': vehicle['control_date'],
                            'error': message
                        })
                        
                except Exception as e:
                    error_msg = f"Error processing {vehicle['number_plate']}: {str(e)}"
                    errors.append(error_msg)
                    
                    self.db_manager.log_email(
                        vehicle['number_plate'],
                        vehicle['owner_email'],
                        'ERROR',
                        error_msg
                    )
            
            # Keep only last 50 notifications in log
            if len(self.notification_log) > 50:
                self.notification_log = self.notification_log[-50:]
            
            return notifications_sent, errors
            
        except Exception as e:
            error_msg = f"Error in background service: {str(e)}"
            return 0, [error_msg]
    
    def run_scheduler(self):
        """Run the scheduled tasks"""
        # Schedule the notification check to run every hour
        schedule.every().hour.do(self.check_and_send_notifications)
        
        # Also run once immediately when started
        self.check_and_send_notifications()
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start_background_service(self):
        """Start the background service in a separate thread"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
            return True, "Background service started successfully"
        else:
            return False, "Background service is already running"
    
    def stop_background_service(self):
        """Stop the background service"""
        if self.is_running:
            self.is_running = False
            schedule.clear()
            return True, "Background service stopped successfully"
        else:
            return False, "Background service is not running"
    
    def get_service_status(self):
        """Get current service status"""
        return {
            'is_running': self.is_running,
            'last_check': self.last_check,
            'pending_jobs': len(schedule.jobs),
            'recent_notifications': self.notification_log[-10:] if self.notification_log else []
        }
    
    def manual_check(self):
        """Manually trigger a notification check"""
        return self.check_and_send_notifications()
    
    def get_vehicles_needing_notification(self):
        """Get list of vehicles that need notification"""
        return self.db_manager.get_vehicles_due_for_notification(days_before=7)