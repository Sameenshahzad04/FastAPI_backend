

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.email_config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM
import logging

logger = logging.getLogger(__name__)
# Get templates directory (FIXED PATH)
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "template"  # Make sure this matches your folder name

# Debug: Print the path (check console when server starts)
logger.info(f" BASE_DIR: {BASE_DIR}")
logger.info(f" TEMPLATE_DIR: {TEMPLATE_DIR}")
logger.info(f" TEMPLATE_DIR exists: {TEMPLATE_DIR.exists()}")

# Check if email.html exists
EMAIL_TEMPLATE = TEMPLATE_DIR / "email.html"
logger.info(f" email.html exists: {EMAIL_TEMPLATE.exists()}")

if not EMAIL_TEMPLATE.exists():
    logger.error(f" Template file not found at: {EMAIL_TEMPLATE}")
    logger.error(f"   Please create: {EMAIL_TEMPLATE}")

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

def send_credentials_email(to: str, username: str, password: str, org_name: str):
    
    try:
        # Load template
        template = env.get_template("email.html")
        
        # Render template with variables
        body = template.render(
            username=username,
            user_email=to,
            password=password,
            org_name=org_name
        )
        
        # Create email message
        message = MIMEMultipart()
        message["From"] = EMAIL_FROM
        message["To"] = to
        message["Subject"] = f"Welcome to {org_name} - Your Account Credentials"
        
        # Attach HTML body
        message.attach(MIMEText(body, "html"))
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to, message.as_string())
        
        logger.info(f"Email sent successfully to {to}")
        return True
        
    except Exception as e:
        logger.error(f" Error sending email to {to}: {str(e)}")
        return False