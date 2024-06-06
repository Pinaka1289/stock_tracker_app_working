import aiosmtplib
from email.message import EmailMessage
import smtplib


# Email configuration
SMTP_HOST = "localhost"
SMTP_PORT = 1025
SMTP_USER = "noreply@mykubera.com"
SMTP_PASSWORD = None

# Function to send email


# Function to send email
async def send_registration_email(to_email: str, username: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = to_email
    message["Subject"] = "Registration Successful"
    message.set_content(
        f"Hello {username},\n\nThank you for registering on MyKubera platform.")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.send_message(message)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
