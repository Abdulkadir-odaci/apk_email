import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Environment variables for credentials
EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")

# Test recipients
recipients = ["abdlkdrdci@gmail.com", "muslumertekin@hotmail.com"]

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
    <p>Met vriendelijke groet,<br>Koree Autoservice</p>
  </body>
</html>
"""

# Create email
message = MIMEMultipart("alternative")
message["Subject"] = subject
message["From"] = EMAIL_ADDRESS
message["To"] = ", ".join(recipients)

# Attach HTML content
message.attach(MIMEText(html_body, "html"))

# Send email
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipients, message.as_string())
        print("✅ Test e-mail(s) succesvol verzonden.")
except Exception as e:
    print(f"❌ Fout bij verzenden van e-mail: {e}")

