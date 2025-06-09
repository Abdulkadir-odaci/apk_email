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

def get_apk_reminders_from_supabase(days_ahead=30):
    """
    Fetch customers who need APK reminders from Supabase
    """
    try:
        supabase = init_supabase()
        
        # Calculate the cutoff date (30 days from now)
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
        
        # Query clients with APK expiry within the next 30 days
        result = supabase.table('client').select(
            'name, email, licence_plate, apk_expiry_date, car_brand, car_model'
        ).not_.is_('apk_expiry_date', 'null').lte(
            'apk_expiry_date', cutoff_date_str
        ).gte(
            'apk_expiry_date', datetime.now().strftime('%Y-%m-%d')
        ).execute()
        
        customers = result.data
        print(f"📊 Found {len(customers)} customers needing APK reminders")
        
        # Filter and add days until expiry
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

def create_personalized_email(customer):
    """Create personalized HTML email content with WhatsApp integration"""
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
    
    # Urgency message based on days
    if days_until <= 0:
        urgency_message = "🚨 <strong style='color: red;'>URGENT: Uw APK is vandaag verlopen!</strong>"
    elif days_until <= 7:
        urgency_message = f"🚨 <strong style='color: red;'>URGENT: Uw APK verloopt over {days_until} dagen!</strong>"
    elif days_until <= 14:
        urgency_message = f"⚠️ <strong style='color: orange;'>Uw APK verloopt binnenkort over {days_until} dagen</strong>"
    else:
        urgency_message = f"📅 Uw APK verloopt over {days_until} dagen"
    
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
            .button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
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
                transition: all 0.3s ease;
            }}
            .whatsapp-button:hover {{
                background-color: #128c7e;
                transform: translateY(-2px);
            }}
            .phone-section {{ 
                text-align: center; 
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                border-top: 1px solid #eee;
                margin-top: 30px;
                color: #666;
            }}
            .whatsapp-icon {{
                width: 20px;
                height: 20px;
                vertical-align: middle;
                margin-right: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚗 APK Herinnering</h1>
                <p>Koree Autoservice</p>
            </div>
            
            <div class="content">
                <p>Beste {name},</p>
                
                <div class="urgency">
                    {urgency_message}
                </div>
                
                <p>We herinneren u eraan dat de APK-keuring{car_info} op <strong>{apk_date}</strong> verloopt.</p>
                
                <div class="car-info">
                    <h3>🚙 Voertuig gegevens:</h3>
                    <p><strong>Kenteken:</strong> {licence_plate}</p>
                    {f'<p><strong>Merk/Model:</strong> {car_brand} {car_model}</p>' if car_brand or car_model else ''}
                    <p><strong>APK vervalt:</strong> {apk_date}</p>
                </div>
                
                <p style="text-align: center;">
                    <a href="https://your-booking-website.com" class="button">
                        📅 Maak Online een Afspraak
                    </a>
                </p>
                
                <div class="whatsapp-section">
                    <h3>💬 Snel contact via WhatsApp</h3>
                    <p>Heeft u vragen of wilt u direct een afspraak maken?</p>
                    <a href="{whatsapp_url}" class="whatsapp-button" target="_blank">
                        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2ZmZiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyLjAxNyAyLjAxNEE5Ljk2MyA5Ljk2MyAwIDAgMCAyLjA1IDEyYzAgMS44ODUuNTEgMy42NCAxLjM4NiA1LjE0N0wyIDIybDUuMDM0LTEuMzJBOS45MyA5LjkzIDAgMCAwIDEyLjAxNyAyMmE5Ljk2MyA5Ljk2MyAwIDAgMCAwLTE5Ljk4NlpNMTIuMDE3IDIwLjE1YTguMTUgOC4xNSAwIDAgMS00LjE1Ny0xLjEzN2wtLjI5OC0uMTc3LTMuMDk2LjgxMi44MjUtMy4wMTYtLjE5NC0uMzEzQTguMTEzIDguMTEzIDAgMCAxIDMuOSAxMmE4LjEzIDguMTMgMCAwIDEgOC4xMTctOC4xNUE4LjEzIDguMTMgMCAwIDEgMjAuMTUgMTJhOC4xMyA4LjEzIDAgMCAxLTguMTMzIDguMTVabTQuNDYyLTYuMDg3Yy0uMjQ0LS4xMjItMS40NDctLjcxNC0xLjY3MS0uNzk2LS4yMjQtLjA4Mi0uMzg3LS4xMjItLjU1LjEyMi0uMTYzLjI0NC0uNjMzLjc5Ni0uNzc2Ljk1OS0uMTQzLjE2My0uMjg2LjE4My0uNTMuMDYxcy0xLjAzNS0uMzgyLTEuOTctMS4yMTVjLS43MjgtLjY1LTEuMjE5LTEuNDUzLTEuMzYyLTEuNjk3LS4xNDMtLjI0NC0uMDE1LS4zNzYuMTA3LS40OTguMTA5LS4xMDkuMjQ0LS4yODYuMzY2LS40MjkuMTIyLS4xNDMuMTYzLS4yNDQuMjQ0LS40MDcuMDgyLS4xNjMuMDQxLS4zMDUtLjAyLS40MjktLjA2MS0uMTIyLS41NS0xLjMyNi0uNzU0LTEuODE2LS4xOTgtLjQ3Ni0uNDA0LS40MTItLjU1LS40MjItLjE0My0uMDA5LS4zMDUtLjAxMS0uNDY4LS4wMTEtLjE2MyAwLS40MjkuMDYxLS42NTMuMzA1LS4yMjQuMjQ0LS44NTUuODM1LS44NTUgMi4wMzkgMCAxLjIwNC44NzYgMi4zNjguOTk4IDIuNTMxLjEyMi4xNjMgMS43MjMgMi42MzEgNC4xNzYgMy42OTEuNTg0LjI0NSAxLjA0LjM5MSAxLjM5Ni41MDIuNTg2LjE4NiAxLjEyLjE2IDEuNTQyLjA5Ny40NzEtLjA3IDEuNDQ3LS41OTEgMS42NTEtMS4xNjEuMjA0LS41Ny4yMDQtMS4wNi4xNDMtMS4xNjEtLjA2MS0uMTAyLS4yMjQtLjE2My0uNDY4LS4yODVaIi8+Cjwvc3ZnPgo=" class="whatsapp-icon" alt="WhatsApp">
                        Stuur WhatsApp Bericht
                    </a>
                    <p style="font-size: 12px; color: #666;">
                        <em>Er wordt automatisch een bericht voorbereid met uw kenteken en afspraak details</em>
                    </p>
                </div>
                
                <div class="phone-section">
                    <h3>📞 Of bel ons direct</h3>
                    <p><strong>Telefoon:</strong> <a href="tel:+31612345678" style="color: #007bff;">+31 6 1234 5678</a></p>
                    <p><strong>Openingstijden:</strong> Ma-Vr 8:00-17:00, Za 9:00-15:00</p>
                </div>
                
                <p>Het is belangrijk om tijdig een nieuwe APK-keuring te laten uitvoeren om problemen met de verzekering en boetes te voorkomen.</p>
            </div>
            
            <div class="footer">
                <p><strong>Koree Autoservice</strong><br>
                Uw adres hier<br>
                Tel: +31 6 1234 5678<br>
                Email: info@koreeautoservice.nl</p>
                
                <p style="font-size: 12px; color: #999;">
                    U ontvangt deze e-mail omdat u klant bent bij Koree Autoservice.<br>
                    Wilt u geen herinneringen meer ontvangen? <a href="mailto:info@koreeautoservice.nl?subject=Uitschrijven APK herinneringen">Klik hier</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_body

def send_personalized_emails():
    """Send personalized emails to all customers needing APK reminders"""
    customers = get_apk_reminders_from_supabase()
    
    if not customers:
        print("ℹ️ No customers found needing APK reminders")
        return
    
    success_count = 0
    error_count = 0
    
    print(f"📧 Starting to send {len(customers)} personalized emails...")
    
    for customer in customers:
        try:
            name = customer.get('name', 'Klant')
            email = customer.get('email')
            licence_plate = customer.get('licence_plate', '')
            days_until = customer.get('days_until_expiry', 0)
            
            if not email:
                print(f"⚠️ Skipping {name} - no email address")
                continue
            
            print(f"📤 Sending email to {name} ({email}) - APK expires in {days_until} days")
            
            # Create personalized email content
            html_content = create_personalized_email(customer)
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🚗 APK Herinnering - {licence_plate} verloopt {'VANDAAG' if days_until <= 0 else f'over {days_until} dagen'}"
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
            
        except Exception as e:
            print(f"❌ Failed to send email to {customer.get('name', 'Unknown')} ({customer.get('email', 'No email')}): {e}")
            error_count += 1
    
    print(f"\n📊 Email Summary:")
    print(f"✅ Successfully sent: {success_count}")
    print(f"❌ Failed: {error_count}")
    print(f"📧 Total processed: {len(customers)}")

if __name__ == "__main__":
    send_personalized_emails()



