# config/email_config.py

from fastapi_mail import ConnectionConfig
import os 
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
# Validate required fields
if not SMTP_USER or not SMTP_PASSWORD:
    raise ValueError("MAIL_USERNAME and MAIL_PASSWORD must be set in .env file")