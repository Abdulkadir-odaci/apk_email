import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from supabase import create_client, Client

print("📤 Starting personalized APK email reminders")

# Environment variables for credentials
EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Debug: print basic setup
print(f"📧 EMAIL_USER: {EMAIL_ADDRESS}")
print("🔒 EMAIL_PASS: FOUND" if EMAIL_PASSWORD else "❌ EMAIL_PASS: NOT FOUND")
print("🔒 SUPABASE: FOUND" if SUPABASE_URL and SUPABASE_KEY else "❌ SUPABASE: NOT CONFIGURED")

# Check credentials
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    print("❌ ERROR: EMAIL_USER or EMAIL_PASS environment variable not set.")
    exit(1)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL or SUPABASE_KEY environment variable not set.")
    exit(1)

# Initialize Supabase client
def init_supabase():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def format_date(date_str):
    """Format date from YYYY-MM-DD to DD-MM-YYYY"""
    if not date_str:
        return "Niet bekend"
    try:
        date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
        return date_obj.strftime('%d-%m-%Y')
    except:
        return date_str

def get_all_customers_with_apk():
    """
    Fetch ALL customers with APK data from Supabase - regardless of expiry date
    """
    try:
        supabase = init_supabase()
        
        # Query ALL clients with APK expiry dates (no date filtering)
        result = supabase.table('client').select(
            'name, email, licence_plate, apk_expiry_date, car_brand, car_model'
        ).not_.is_('apk_expiry_date', 'null').not_.is_('email', 'null').execute()
        
        customers = result.data
        print(f"📊 Found {len(customers)} customers with APK data")
        
        # Add days until expiry for all customers
        customers_with_days = []
        today = datetime.now().date()
        
        for customer in customers:
            if customer.get('email') and customer.get('apk_expiry_date'):
                try:
                    apk_date = datetime.strptime(customer['apk_expiry_date'][:10], '%Y-%m-%d').date()
                    days_until_expiry = (apk_date - today).days
                    
                    customer['days_until_expiry'] = days_until_expiry
                    customers_with_days.append(customer)
                except:
                    continue
        
        return customers_with_days
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

def create_personalized_email_all_users(customer):
    """Create personalized HTML email content for ALL users"""
    name = customer.get('name', 'Klant')
    apk_date = format_date(customer.get('apk_expiry_date'))
    licence_plate = customer.get('licence_plate', '')
    car_brand = customer.get('car_brand', '')
    car_model = customer.get('car_model', '')
    days_until = customer.get('days_until_expiry', 0)
    
    # Create car description
    car_info = ""
    if car_brand or car_model:
        car_parts = [part for part in [car_brand, car_model] if part]
        car_info = f" voor uw {' '.join(car_parts)}"
    
    # Different messages based on APK status
    if days_until < 0:
        # APK already expired
        urgency_message = f"🚨 <strong style='color: red;'>URGENT: Uw APK is {abs(days_until)} dagen geleden verlopen!</strong>"
        email_subject = f"🚨 URGENT - APK VERLOPEN - {licence_plate}"
        main_message = f"Uw APK is op {apk_date} verlopen. U moet direct actie ondernemen!"
    elif days_until == 0:
        # APK expires today
        urgency_message = "🚨 <strong style='color: red;'>URGENT: Uw APK verloopt VANDAAG!</strong>"
        email_subject = f"🚨 APK VERLOOPT VANDAAG - {licence_plate}"
        main_message = f"Uw APK verloopt vandaag ({apk_date}). Maak vandaag nog een afspraak!"
    elif days_until <= 7:
        # APK expires within a week
        urgency_message = f"🚨 <strong style='color: red;'>URGENT: Uw APK verloopt over {days_until} dagen!</strong>"
        email_subject = f"🚨 APK verloopt binnenkort - {licence_plate}"
        main_message = f"Uw APK verloopt over {days_until} dagen op {apk_date}. Plan nu uw afspraak!"
    elif days_until <= 30:
        # APK expires within a month
        urgency_message = f"⚠️ <strong style='color: orange;'>Uw APK verloopt over {days_until} dagen</strong>"
        email_subject = f"📅 APK Herinnering - {licence_plate}"
        main_message = f"Uw APK verloopt over {days_until} dagen op {apk_date}. Het is tijd om een afspraak te plannen."
    else:
        # APK is still valid for more than 30 days
        urgency_message = f"✅ <strong style='color: green;'>Uw APK is nog {days_until} dagen geldig</strong>"
        email_subject = f"📋 APK Status Update - {licence_plate}"
        main_message = f"Uw APK is nog geldig tot {apk_date} ({days_until} dagen). We houden u op de hoogte!"
    
    # Store subject in customer data for use in send function
    customer['email_subject'] = email_subject
    
    # WhatsApp message pre-filled text
    whatsapp_message = f"Hallo, ik wil graag een APK afspraak maken voor kenteken {licence_plate}{car_info}. APK vervalt op {apk_date}."
    whatsapp_url = f"https://wa.me/31612345678?text={whatsapp_message.replace(' ', '%20')}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                line-height: 1.6; 
                color: #333; 
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                padding: 20px; 
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white;
                padding: 30px 20px; 
                text-align: center; 
                border-radius: 10px 10px 0 0;
                margin: -20px -20px 20px -20px;
            }}
            .content {{ padding: 20px 0; }}
            .urgency {{ 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0; 
                text-align: center;
                font-size: 18px;
                background: #fff3cd;
                border: 1px solid #ffeaa7;
            }}
            .car-info {{
                background: #e3f2fd;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                border-left: 4px solid #2196f3;
            }}
            .button {{ 
                display: inline-block; 
                padding: 15px 30px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important; 
                text-decoration: none; 
                border-radius: 25px; 
                margin: 15px 5px;
                font-weight: bold;
                text-align: center;
                transition: all 0.3s ease;
            }}
            .whatsapp-section {{ 
                background: #e8f5e8; 
                padding: 20px; 
                border-radius: 8px; 
                margin: 20px 0; 
                text-align: center;
                border: 2px solid #4caf50;
            }}
            .whatsapp-button {{ 
                display: inline-block; 
                padding: 12px 25px; 
                background-color: #25D366; 
                color: white !important; 
                text-decoration: none; 
                border-radius: 25px; 
                margin: 10px 0;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                border-top: 1px solid #eee;
                margin-top: 30px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚗 APK Status Update</h1>
                <p>Koree Autoservice</p>
            </div>
            
            <div class="content">
                <p>Beste {name},</p>
                
                <div class="urgency">
                    {urgency_message}
                </div>
                
                <p>{main_message}</p>
                
                <div class="car-info">
                    <h3>🚙 Voertuig gegevens:</h3>
                    <p><strong>Kenteken:</strong> {licence_plate}</p>
                    {f'<p><strong>Merk/Model:</strong> {car_brand} {car_model}</p>' if car_brand or car_model else ''}
                    <p><strong>APK vervalt:</strong> {apk_date}</p>
                </div>
                
                {f'''
                <p style="text-align: center;">
                    <a href="https://your-booking-website.com" class="button">
                        📅 Maak Online een Afspraak
                    </a>
                </p>
                
                <div class="whatsapp-section">
                    <h3>💬 Snel contact via WhatsApp</h3>
                    <p>Heeft u vragen of wilt u direct een afspraak maken?</p>
                    <a href="{whatsapp_url}" class="whatsapp-button" target="_blank">
                        📱 Stuur WhatsApp Bericht
                    </a>
                </div>
                ''' if days_until <= 30 else ''}
                
                <p>Met vriendelijke groet,<br>
                Het team van Koree Autoservice</p>
            </div>
            
            <div class="footer">
                <p><strong>Koree Autoservice</strong><br>
                Uw adres hier<br>
                Tel: +31 6 1234 5678<br>
                Email: info@koreeautoservice.nl</p>
                
                <p style="font-size: 12px; color: #999;">
                    U ontvangt deze dagelijkse APK status update omdat u klant bent bij Koree Autoservice.<br>
                    <a href="mailto:info@koreeautoservice.nl?subject=Uitschrijven APK updates">Uitschrijven</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_body

def send_daily_apk_status_emails():
    """Send daily APK status emails to ALL customers"""
    customers = get_all_customers_with_apk()  # Changed function name
    
    if not customers:
        print("ℹ️ No customers found with APK data")
        return
    
    success_count = 0
    error_count = 0
    
    print(f"📧 Starting to send daily APK status emails to {len(customers)} customers...")
    
    for customer in customers:
        try:
            name = customer.get('name', 'Klant')
            email = customer.get('email')
            days_until = customer.get('days_until_expiry', 0)
            
            if not email:
                print(f"⚠️ Skipping {name} - no email address")
                continue
            
            print(f"📤 Sending email to {name} ({email}) - APK: {days_until} days")
            
            # Create personalized email content
            html_content = create_personalized_email_all_users(customer)
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = customer.get('email_subject', 'APK Status Update')
            message["From"] = EMAIL_ADDRESS
            message["To"] = email
            
            # Attach HTML content
            message.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, [email], message.as_string())
            
            print(f"✅ Email sent successfully to {name} ({email})")
            success_count += 1
            
            # Add small delay to avoid rate limiting
            import time
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Failed to send email to {customer.get('name', 'Unknown')}: {e}")
            error_count += 1
    
    print(f"\n📊 Daily Email Summary:")
    print(f"✅ Successfully sent: {success_count}")
    print(f"❌ Failed: {error_count}")
    print(f"📧 Total customers: {len(customers)}")

# Update the main function call
if __name__ == "__main__":
    send_daily_apk_status_emails()




