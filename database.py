import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

class DatabaseManager:
    def __init__(self, db_path="auto_control.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create vehicles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number_plate TEXT UNIQUE NOT NULL,
                owner_email TEXT NOT NULL,
                control_date DATE NOT NULL,
                last_notification_sent DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create email_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number_plate TEXT NOT NULL,
                email_sent_to TEXT NOT NULL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_vehicle(self, number_plate, owner_email, control_date):
        """Add a new vehicle to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO vehicles 
                (number_plate, owner_email, control_date, updated_at) 
                VALUES (?, ?, ?, ?)
            ''', (number_plate.upper(), owner_email, control_date, datetime.now()))
            
            conn.commit()
            conn.close()
            return True, "Vehicle added successfully"
        except Exception as e:
            return False, f"Error adding vehicle: {str(e)}"
    
    def get_vehicle(self, number_plate):
        """Get vehicle information by number plate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM vehicles WHERE number_plate = ?
        ''', (number_plate.upper(),))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = ['id', 'number_plate', 'owner_email', 'control_date', 
                      'last_notification_sent', 'created_at', 'updated_at']
            return dict(zip(columns, result))
        return None
    
    def get_all_vehicles(self):
        """Get all vehicles from the database"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM vehicles", conn)
        conn.close()
        return df
    
    def get_vehicles_due_for_notification(self, days_before=7):
        """Get vehicles that need notification (control date is approaching)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate the date threshold
        threshold_date = (datetime.now() + timedelta(days=days_before)).date()
        
        cursor.execute('''
            SELECT * FROM vehicles 
            WHERE control_date <= ? 
            AND (last_notification_sent IS NULL 
                 OR date(last_notification_sent) < date('now'))
        ''', (threshold_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'number_plate', 'owner_email', 'control_date', 
                  'last_notification_sent', 'created_at', 'updated_at']
        
        return [dict(zip(columns, row)) for row in results]
    
    def update_notification_sent(self, number_plate):
        """Update the last notification sent timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE vehicles 
            SET last_notification_sent = ? 
            WHERE number_plate = ?
        ''', (datetime.now(), number_plate.upper()))
        
        conn.commit()
        conn.close()
    
    def log_email(self, number_plate, email_sent_to, status, message=""):
        """Log email sending activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO email_logs 
            (number_plate, email_sent_to, status, message) 
            VALUES (?, ?, ?, ?)
        ''', (number_plate, email_sent_to, status, message))
        
        conn.commit()
        conn.close()
    
    def delete_vehicle(self, number_plate):
        """Delete a vehicle from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM vehicles WHERE number_plate = ?', 
                          (number_plate.upper(),))
            
            conn.commit()
            conn.close()
            return True, "Vehicle deleted successfully"
        except Exception as e:
            return False, f"Error deleting vehicle: {str(e)}"