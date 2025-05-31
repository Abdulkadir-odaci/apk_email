import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("📤 Start sending test email")

# Environment variables for credentials
EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")

# Debug: print basic setup
print(f"📧 EMAIL_USER: {EMAIL_ADDRESS}")
print("🔒 EMAIL_PASS: FOUND" if EMAIL_PASSWORD else "❌ EMAIL_PASS: NOT FOUND")

# Check credentials
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    print("❌ ERROR: EMAIL_USER or EMAIL_PASS environment variable not set.")
    exit(1)

# Test recipients
recipients = ["abdlkdrdci@gmail.com", "abdulkadirodaci@gmail.com"]
print("📬 Sending test email to (BCC):", ", ".join(recipients))

# Email content
subject = "APK Herinnering – Maak een afspraak"
html_body = """
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2>📅 Tijd voor een APK-keuring</h2>
    <p>Beste klant,</p>
    <p>We herinneren u eraan dat het tijd is voor uw APK-keuring.</p>
    <p>
      Klik op de onderstaande knop om een afspraak te maken bij Koree Autoservice:
    </p>
    <p>
      <a href="https://koree-autoservice.nl/afspraak" 
         style="padding: 12px 24px; background-color: #1f4e79; color: white; text-decoration: none; border-radius: 5px;">
        Maak een afspraak
      </a>
    </p>
    <p style="margin-top: 30px;">
      📱 Heeft u vragen? Neem contact op via WhatsApp:
    </p>
    <p>
      <a href="https://wa.me/31687385143" target="_blank" style="text-decoration: none;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="24" style="vertical-align: middle;" alt="WhatsApp">
        <span style="margin-left: 8px; color: #25D366; font-weight: bold;">Stuur ons een bericht</span>
      </a>
    </p>
    <p>
      📞 Of <a href="tel:31687385143">bel ons direct</a>
    </p>
    <p>Met vriendelijke groet,<br>Koree Autoservice</p>
  </body>
</html>
"""


# Create email
message = MIMEMultipart("alternative")
message["Subject"] = subject
message["From"] = EMAIL_ADDRESS
message["To"] = "Klant"  # Generic name shown in email client
message["Bcc"] = ", ".join(recipients)  # Hidden list of real recipients

# Attach HTML content
message.attach(MIMEText(html_body, "html"))

# Send email
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        print("🔌 Connecting to SMTP server...")
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipients, message.as_string())
        print("✅ Test e-mail(s) succesvol verzonden.")
except Exception as e:
    print(f"❌ Fout bij verzenden van e-mail: {e}")



