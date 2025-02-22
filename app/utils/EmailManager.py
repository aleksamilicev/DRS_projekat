import smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
from config import Config

executor = ThreadPoolExecutor(max_workers=5)

def send_email_async(email: str, text: str):
    """Function to send an email asynchronously."""
    sender_email = Config.EMAIL
    sender_password = Config.PASSWORD
    smtp_server = Config.SMTP_SERVER
    smtp_port = Config.SMTP_PORT

    try:
        msg = MIMEText(text)
        msg["Subject"] = "Welcome to Our Platform"
        msg["From"] = sender_email
        msg["To"] = email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        print(f"Email sent to {email} successfully!")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")

def send_email(email: str, text: str):
    """Function to handle email sending in a separate thread."""
    executor.submit(send_email_async, email, text)