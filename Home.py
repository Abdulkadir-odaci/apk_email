# import streamlit as st
# import pandas as pd
# from datetime import datetime, date, timedelta
# import time
# from database import DatabaseManager
# # from email_service import EmailService
# # from background_service import BackgroundService

# # Page configuration
# st.set_page_config(
#     page_title="Auto Control Management System",
#     page_icon="🚗",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Initialize session state
# if 'db_manager' not in st.session_state:
#     st.session_state.db_manager = DatabaseManager()

# # if 'email_service' not in st.session_state:
# #     st.session_state.email_service = EmailService()

# # if 'background_service' not in st.session_state:
# #     st.session_state.background_service = BackgroundService(
# #         st.session_state.email_service,
# #         st.session_state.db_manager
# #     )

# if 'email_configured' not in st.session_state:
#     st.session_state.email_configured = False

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         background: linear-gradient(90deg, #2E86AB, #A23B72);
#         padding: 1rem;
#         border-radius: 10px;
#         color: white;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
    
#     .metric-card {
#         background-color: #f8f9fa;
#         padding: 1rem;
#         border-radius: 8px;
#         border-left: 4px solid #2E86AB;
#         margin: 0.5rem 0;
#     }
    
#     .alert-danger {
#         background-color: #f8d7da;
#         border: 1px solid #f5c6cb;
#         color: #721c24;
#         padding: 0.75rem;
#         border-radius: 0.375rem;
#         margin: 1rem 0;
#     }
    
#     .alert-success {
#         background-color: #d1e7dd;
#         border: 1px solid #badbcc;
#         color: #0f5132;
#         padding: 0.75rem;
#         border-radius: 0.375rem;
#         margin: 1rem 0;
#     }
    
#     .alert-warning {
#         background-color: #fff3cd;
#         border: 1px solid #ffecb5;
#         color: #664d03;
#         padding: 0.75rem;
#         border-radius: 0.375rem;
#         margin: 1rem 0;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Header
# st.markdown("""
# <div class="main-header">
#     <h1>🚗 Auto Control Management System</h1>
#     <p>Automated notification system for vehicle control deadlines</p>
# </div>
# """, unsafe_allow_html=True)

# # Sidebar for navigation
# st.sidebar.title("📋 Navigation")
# page = st.sidebar.selectbox(
#     "Choose a page:",
#     ["🏠 Dashboard", "➕ Add Vehicle", "🔍 Search Vehicle", "📊 All Vehicles", "⚙️ Email Configuration", "🔄 Background Service", "📈 Reports"]
# )

# # Email Configuration Check
# if not st.session_state.email_configured and page != "⚙️ Email Configuration":
#     st.markdown("""
#     <div class="alert-warning">
#         <strong>⚠️ Email Not Configured</strong><br>
#         Please configure your email settings first to enable notifications.
#         Go to "Email Configuration" in the sidebar.
#     </div>
#     """, unsafe_allow_html=True)

# # Dashboard Page
# if page == "🏠 Dashboard":
#     st.header("📊 Dashboard")
    
#     # Get statistics
#     all_vehicles = st.session_state.db_manager.get_all_vehicles()
#     vehicles_due = st.session_state.db_manager.get_vehicles_due_for_notification(days_before=7)
    
#     # Metrics
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.metric("Total Vehicles", len(all_vehicles) if not all_vehicles.empty else 0)
    
#     with col2:
#         st.metric("Due for Control", len(vehicles_due))
    
#     with col3:
#         service_status = st.session_state.background_service.get_service_status()
#         status_text = "Running" if service_status['is_running'] else "Stopped"
#         st.metric("Background Service", status_text)
    
#     with col4:
#         last_check = service_status.get('last_check')
#         if last_check:
#             st.metric("Last Check", last_check.strftime("%H:%M"))
#         else:
#             st.metric("Last Check", "Never")
    
#     # Recent notifications
#     st.subheader("📧 Recent Notifications")
#     recent_notifications = service_status.get('recent_notifications', [])
    
#     if recent_notifications:
#         for notification in recent_notifications:
#             status_color = "🟢" if notification['status'] == 'SUCCESS' else "🔴"
#             st.write(f"{status_color} {notification['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
#                     f"{notification['number_plate']} → {notification['email']}")
#     else:
#         st.info("No recent notifications")
    
#     # Vehicles due for control
#     if vehicles_due:
#         st.subheader("⚠️ Vehicles Due for Control")
#         for vehicle in vehicles_due:
#             control_date = datetime.strptime(vehicle['control_date'], '%Y-%m-%d').date()
#             days_until = (control_date - date.today()).days
            
#             if days_until < 0:
#                 st.error(f"🚨 **{vehicle['number_plate']}** - Control was due {abs(days_until)} days ago!")
#             elif days_until <= 3:
#                 st.warning(f"⚠️ **{vehicle['number_plate']}** - Control due in {days_until} days")
#             else:
#                 st.info(f"ℹ️ **{vehicle['number_plate']}** - Control due in {days_until} days")

# # Add Vehicle Page
# elif page == "➕ Add Vehicle":
#     st.header("➕ Add New Vehicle")
    
#     with st.form("add_vehicle_form"):
#         col1, col2 = st.columns(2)
        
#         with col1:
#             number_plate = st.text_input("Number Plate", placeholder="e.g., ABC-123").upper()
#             owner_email = st.text_input("Owner Email", placeholder="owner@example.com")
        
#         with col2:
#             control_date = st.date_input("Control Date", min_value=date.today())
            
#         submitted = st.form_submit_button("Add Vehicle", type="primary")
        
#         if submitted:
#             if number_plate and owner_email and control_date:
#                 success, message = st.session_state.db_manager.add_vehicle(
#                     number_plate, owner_email, control_date.strftime('%Y-%m-%d')
#                 )
                
#                 if success:
#                     st.success(f"✅ {message}")
#                     st.rerun()
#                 else:
#                     st.error(f"❌ {message}")
#             else:
#                 st.error("❌ Please fill all fields")

# # Search Vehicle Page
# elif page == "🔍 Search Vehicle":
#     st.header("🔍 Search Vehicle")
    
#     search_plate = st.text_input("Enter Number Plate", placeholder="e.g., ABC-123").upper()
    
#     if search_plate:
#         vehicle = st.session_state.db_manager.get_vehicle(search_plate)
        
#         if vehicle:
#             st.success(f"✅ Vehicle found: {vehicle['number_plate']}")
            
#             # Display vehicle information
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 st.info(f"**Owner Email:** {vehicle['owner_email']}")
#                 st.info(f"**Control Date:** {vehicle['control_date']}")
            
#             with col2:
#                 control_date = datetime.strptime(vehicle['control_date'], '%Y-%m-%d').date()
#                 days_until = (control_date - date.today()).days
                
#                 if days_until < 0:
#                     st.error(f"🚨 Control was due {abs(days_until)} days ago!")
#                 elif days_until <= 7:
#                     st.warning(f"⚠️ Control due in {days_until} days")
#                 else:
#                     st.success(f"✅ Control due in {days_until} days")
            
#             # Actions
#             st.subheader("Actions")
#             col1, col2, col3 = st.columns(3)
            
#             with col1:
#                 if st.button("📧 Send Test Email"):
#                     if st.session_state.email_configured:
#                         success, message = st.session_state.email_service.send_control_reminder(
#                             vehicle['number_plate'],
#                             vehicle['control_date'],
#                             vehicle['owner_email']
#                         )
#                         if success:
#                             st.success("✅ Test email sent successfully!")
#                         else:
#                             st.error(f"❌ Failed to send email: {message}")
#                     else:
#                         st.error("❌ Email not configured")
            
#             with col2:
#                 new_control_date = st.date_input("Update Control Date", 
#                                                value=control_date, 
#                                                min_value=date.today())
#                 if st.button("📅 Update Date"):
#                     success, message = st.session_state.db_manager.add_vehicle(
#                         vehicle['number_plate'],
#                         vehicle['owner_email'],
#                         new_control_date.strftime('%Y-%m-%d')
#                     )
#                     if success:
#                         st.success("✅ Control date updated!")
#                         st.rerun()
#                     else:
#                         st.error(f"❌ {message}")
            
#             with col3:
#                 if st.button("🗑️ Delete Vehicle", type="secondary"):
#                     success, message = st.session_state.db_manager.delete_vehicle(search_plate)
#                     if success:
#                         st.success("✅ Vehicle deleted!")
#                         st.rerun()
#                     else:
#                         st.error(f"❌ {message}")
#         else:
#             st.warning(f"⚠️ No vehicle found with number plate: {search_plate}")

# # All Vehicles Page
# elif page == "📊 All Vehicles":
#     st.header("📊 All Vehicles")
    
#     vehicles_df = st.session_state.db_manager.get_all_vehicles()
    
#     if not vehicles_df.empty:
#         # Add days until control column
#         vehicles_df['control_date'] = pd.to_datetime(vehicles_df['control_date'])
#         vehicles_df['days_until_control'] = (vehicles_df['control_date'] - pd.Timestamp.now()).dt.days
        
#         # Format display
#         display_df = vehicles_df.copy()
#         display_df['control_date'] = display_df['control_date'].dt.strftime('%Y-%m-%d')
#         display_df['status'] = display_df['days_until_control'].apply(
#             lambda x: "🚨 Overdue" if x < 0 else 
#                      "⚠️ Due Soon" if x <= 7 else 
#                      "✅ On Track"
#         )
        
#         # Display table
#         st.dataframe(
#             display_df[['number_plate', 'owner_email', 'control_date', 'days_until_control', 'status']],
#             column_config={
#                 "number_plate": "Number Plate",
#                 "owner_email": "Owner Email",
#                 "control_date": "Control Date",
#                 "days_until_control": "Days Until Control",
#                 "status": "Status"
#             },
#             use_container_width=True
#         )
        
#         # Bulk actions
#         st.subheader("🔧 Bulk Actions")
#         col1, col2 = st.columns(2)
        
#         with col1:
#             if st.button("📧 Send All Due Notifications"):
#                 if st.session_state.email_configured:
#                     vehicles_due = st.session_state.db_manager.get_vehicles_due_for_notification(days_before=7)
#                     if vehicles_due:
#                         sent_count = 0
#                         failed_count = 0
                        
#                         progress_bar = st.progress(0)
#                         status_text = st.empty()
                        
#                         for i, vehicle in enumerate(vehicles_due):
#                             status_text.text(f"Sending email to {vehicle['number_plate']}...")
#                             success, message = st.session_state.email_service.send_control_reminder(
#                                 vehicle['number_plate'],
#                                 vehicle['control_date'],
#                                 vehicle['owner_email']
#                             )
                            
#                             if success:
#                                 sent_count += 1
#                                 st.session_state.db_manager.update_notification_sent(vehicle['number_plate'])
#                             else:
#                                 failed_count += 1
                            
#                             progress_bar.progress((i + 1) / len(vehicles_due))
                        
#                         status_text.text("")
#                         st.success(f"✅ Sent {sent_count} notifications, {failed_count} failed")
#                     else:
#                         st.info("ℹ️ No vehicles due for notification")
#                 else:
#                     st.error("❌ Email not configured")
        
#         with col2:
#             # Export data
#             csv = display_df.to_csv(index=False)
#             st.download_button(
#                 label="📥 Download CSV",
#                 data=csv,
#                 file_name=f"vehicles_{datetime.now().strftime('%Y%m%d')}.csv",
#                 mime="text/csv"
#             )
#     else:
#         st.info("ℹ️ No vehicles found. Add some vehicles to get started!")

# # Email Configuration Page
# elif page == "⚙️ Email Configuration":
#     st.header("⚙️ Email Configuration")
    
#     st.info("📧 Configure your email settings to enable automatic notifications.")
    
#     with st.form("email_config_form"):
#         col1, col2 = st.columns(2)
        
#         with col1:
#             sender_email = st.text_input("Sender Email", placeholder="your-email@gmail.com")
#             smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
        
#         with col2:
#             sender_password = st.text_input("App Password", type="password", 
#                                           help="Use App Password for Gmail")
#             smtp_port = st.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             test_email = st.text_input("Test Email Address", placeholder="test@example.com")
        
#         submitted = st.form_submit_button("💾 Save Configuration", type="primary")
#         test_connection = st.form_submit_button("🔍 Test Connection")
        
#         if submitted:
#             if sender_email and sender_password:
#                 st.session_state.email_service.configure_smtp(sender_email, sender_password)
#                 st.session_state.email_configured = True
#                 st.success("✅ Email configuration saved successfully!")
#             else:
#                 st.error("❌ Please provide email and password")
        
#         if test_connection:
#             if sender_email and sender_password:
#                 st.session_state.email_service.configure_smtp(sender_email, sender_password)
#                 success, message = st.session_state.email_service.test_email_connection()
                
#                 if success:
#                     st.success(f"✅ {message}")
                    
#                     # Send test email if test email is provided
#                     if test_email:
#                         test_success, test_message = st.session_state.email_service.send_control_reminder(
#                             "TEST-123", 
#                             (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
#                             test_email
#                         )
                        
#                         if test_success:
#                             st.success("✅ Test email sent successfully!")
#                         else:
#                             st.error(f"❌ Failed to send test email: {test_message}")
#                 else:
#                     st.error(f"❌ {message}")
#             else:
#                 st.error("❌ Please provide email and password")
    
#     # Gmail Instructions
#     with st.expander("📖 Gmail Setup Instructions"):
#         st.markdown("""
#         **For Gmail users:**
        
#         1. **Enable 2-Factor Authentication** on your Google account
#         2. **Generate an App Password**:
#            - Go to Google Account settings
#            - Security → 2-Step Verification → App passwords
#            - Select "Mail" and generate a password
#            - Use this App Password (not your regular password)
#         3. **SMTP Settings**:
#            - Server: `smtp.gmail.com`
#            - Port: `587`
        
#         **For other email providers:**
#         - **Outlook/Hotmail**: `smtp.live.com:587`
#         - **Yahoo**: `smtp.mail.yahoo.com:587`
#         - **Custom SMTP**: Contact your email provider for settings
#         """)

# # Background Service Page
# elif page == "🔄 Background Service":
#     st.header("🔄 Background Service Management")
    
#     service_status = st.session_state.background_service.get_service_status()
    
#     # Service Status
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         status = "🟢 Running" if service_status['is_running'] else "🔴 Stopped"
#         st.metric("Service Status", status)
    
#     with col2:
#         last_check = service_status.get('last_check')
#         if last_check:
#             st.metric("Last Check", last_check.strftime("%Y-%m-%d %H:%M"))
#         else:
#             st.metric("Last Check", "Never")
    
#     with col3:
#         st.metric("Scheduled Jobs", service_status.get('pending_jobs', 0))
    
#     # Service Controls
#     st.subheader("🎛️ Service Controls")
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         if st.button("▶️ Start Service", disabled=service_status['is_running']):
#             if st.session_state.email_configured:
#                 success, message = st.session_state.background_service.start_background_service()
#                 if success:
#                     st.success(f"✅ {message}")
#                     st.rerun()
#                 else:
#                     st.error(f"❌ {message}")
#             else:
#                 st.error("❌ Configure email settings first")
    
#     with col2:
#         if st.button("⏹️ Stop Service", disabled=not service_status['is_running']):
#             success, message = st.session_state.background_service.stop_background_service()
#             if success:
#                 st.success(f"✅ {message}")
#                 st.rerun()
#             else:
#                 st.error(f"❌ {message}")
    
#     with col3:
#         if st.button("🔄 Manual Check"):
#             if st.session_state.email_configured:
#                 with st.spinner("Checking for notifications..."):
#                     sent_count, errors = st.session_state.background_service.manual_check()
                
#                 if sent_count > 0:
#                     st.success(f"✅ Sent {sent_count} notifications")
                
#                 if errors:
#                     for error in errors:
#                         st.error(f"❌ {error}")
                
#                 if sent_count == 0 and not errors:
#                     st.info("ℹ️ No notifications needed at this time")
#             else:
#                 st.error("❌ Configure email settings first")
    
#     # Vehicles needing notification
#     st.subheader("⚠️ Vehicles Needing Notification")
#     vehicles_due = st.session_state.background_service.get_vehicles_needing_notification()
    
#     if vehicles_due:
#         for vehicle in vehicles_due:
#             control_date = datetime.strptime(vehicle['control_date'], '%Y-%m-%d').date()
#             days_until = (control_date - date.today()).days
            
#             col1, col2, col3 = st.columns([2, 2, 1])
            
#             with col1:
#                 st.write(f"**{vehicle['number_plate']}**")
#                 st.write(f"📧 {vehicle['owner_email']}")
            
#             with col2:
#                 st.write(f"📅 Control: {vehicle['control_date']}")
#                 if days_until < 0:
#                     st.write(f"🚨 {abs(days_until)} days overdue")
#                 else:
#                     st.write(f"⏰ {days_until} days remaining")
            
#             with col3:
#                 if st.button(f"📧 Send", key=f"send_{vehicle['number_plate']}"):
#                     success, message = st.session_state.email_service.send_control_reminder(
#                         vehicle['number_plate'],
#                         vehicle['control_date'],
#                         vehicle['owner_email']
#                     )
                    
#                     if success:
#                         st.session_state.db_manager.update_notification_sent(vehicle['number_plate'])
#                         st.success("✅ Email sent!")
#                         st.rerun()
#                     else:
#                         st.error(f"❌ {message}")
            
#             st.divider()
#     else:
#         st.info("ℹ️ No vehicles currently need notification")
    
#     # Recent Activity
#     st.subheader("📊 Recent Notification Activity")
#     recent_notifications = service_status.get('recent_notifications', [])
    
#     if recent_notifications:
#         for notification in recent_notifications[-10:]:  # Show last 10
#             status_icon = "✅" if notification['status'] == 'SUCCESS' else "❌"
            
#             col1, col2, col3 = st.columns([1, 2, 2])
            
#             with col1:
#                 st.write(f"{status_icon} {notification['status']}")
            
#             with col2:
#                 st.write(f"**{notification['number_plate']}**")
#                 st.write(f"📧 {notification['email']}")
            
#             with col3:
#                 st.write(f"📅 {notification['timestamp'].strftime('%Y-%m-%d %H:%M')}")
#                 if notification['status'] == 'FAILED' and 'error' in notification:
#                     st.write(f"❌ {notification['error'][:50]}...")
#     else:
#         st.info("ℹ️ No recent activity")

# # Reports Page
# elif page == "📈 Reports":
#     st.header("📈 Reports & Analytics")
    
#     # Get data
#     all_vehicles = st.session_state.db_manager.get_all_vehicles()
    
#     if not all_vehicles.empty:
#         # Date range selector
#         col1, col2 = st.columns(2)
        
#         with col1:
#             start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        
#         with col2:
#             end_date = st.date_input("End Date", value=date.today() + timedelta(days=30))
        
#         # Filter data
#         all_vehicles['control_date'] = pd.to_datetime(all_vehicles['control_date'])
#         filtered_vehicles = all_vehicles[
#             (all_vehicles['control_date'].dt.date >= start_date) & 
#             (all_vehicles['control_date'].dt.date <= end_date)
#         ]
        
#         # Statistics
#         st.subheader("📊 Statistics")
        
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             total_vehicles = len(filtered_vehicles)
#             st.metric("Total Vehicles", total_vehicles)
        
#         with col2:
#             overdue = len(filtered_vehicles[filtered_vehicles['control_date'].dt.date < date.today()])
#             st.metric("Overdue", overdue)
        
#         with col3:
#             due_soon = len(filtered_vehicles[
#                 (filtered_vehicles['control_date'].dt.date >= date.today()) &
#                 (filtered_vehicles['control_date'].dt.date <= date.today() + timedelta(days=7))
#             ])
#             st.metric("Due This Week", due_soon)
        
#         with col4:
#             future = len(filtered_vehicles[filtered_vehicles['control_date'].dt.date > date.today() + timedelta(days=7)])
#             st.metric("Future Controls", future)
        
#         # Control Date Distribution
#         st.subheader("📅 Control Date Distribution")
        
#         # Group by month
#         filtered_vehicles['month_year'] = filtered_vehicles['control_date'].dt.to_period('M')
#         monthly_counts = filtered_vehicles.groupby('month_year').size().reset_index(name='count')
#         monthly_counts['month_year'] = monthly_counts['month_year'].astype(str)
        
#         if not monthly_counts.empty:
#             st.bar_chart(monthly_counts.set_index('month_year'))
        
#         # Status breakdown
#         st.subheader("🚦 Status Breakdown")
        
#         # Calculate status for each vehicle
#         today = pd.Timestamp.now().date()
#         filtered_vehicles['days_until'] = (filtered_vehicles['control_date'].dt.date - today).apply(lambda x: x.days)
        
#         def get_status(days):
#             if days < 0:
#                 return "Overdue"
#             elif days <= 7:
#                 return "Due Soon"
#             elif days <= 30:
#                 return "Due This Month"
#             else:
#                 return "Future"
        
#         filtered_vehicles['status'] = filtered_vehicles['days_until'].apply(get_status)
#         status_counts = filtered_vehicles['status'].value_counts()
        
#         # Display as pie chart data
#         if not status_counts.empty:
#             st.write("Status Distribution:")
#             for status, count in status_counts.items():
#                 percentage = (count / len(filtered_vehicles)) * 100
#                 st.write(f"- {status}: {count} vehicles ({percentage:.1f}%)")
        
#         # Detailed vehicle list
#         st.subheader("📋 Detailed Vehicle List")
        
#         display_df = filtered_vehicles.copy()
#         display_df['control_date'] = display_df['control_date'].dt.strftime('%Y-%m-%d')
#         display_df['status_icon'] = display_df['status'].map({
#             'Overdue': '🚨',
#             'Due Soon': '⚠️',
#             'Due This Month': '📅',
#             'Future': '✅'
#         })
        
#         st.dataframe(
#             display_df[['number_plate', 'owner_email', 'control_date', 'days_until', 'status_icon', 'status']],
#             column_config={
#                 "number_plate": "Number Plate",
#                 "owner_email": "Owner Email", 
#                 "control_date": "Control Date",
#                 "days_until": "Days Until",
#                 "status_icon": "📊",
#                 "status": "Status"
#             },
#             use_container_width=True
#         )
        
#         # Export filtered data
#         csv = display_df.to_csv(index=False)
#         st.download_button(
#             label="📥 Download Filtered Data",
#             data=csv,
#             file_name=f"vehicles_report_{start_date}_{end_date}.csv",
#             mime="text/csv"
#         )
    
#     else:
#         st.info("ℹ️ No data available for reports. Add some vehicles first!")

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style="text-align: center; color: #6c757d; padding: 1rem;">
#     <p>🚗 Auto Control Management System | Built with Streamlit</p>
#     <p>For support and updates, check the GitHub repository</p>
# </div>
# """, unsafe_allow_html=True)
import streamlit as st

st.set_page_config(
    page_title="Koree Autoservice",
    page_icon="🚗",
    layout="centered"
)

st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #1f4e79;'>🚗 Koree Autoservice</h1>
        <p style='font-size: 18px;'>Welkom bij de APK Herinneringsservice</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

st.markdown("## 📋 Kies een actie:")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/1_Klant_Toevoegen.py", label="👤 Klant Toevoegen", icon="🧾")

with col2:
    st.page_link("pages/2_Check_Auto_Info.py", label="🔍 Kenteken Opzoeken", icon="🚘")
