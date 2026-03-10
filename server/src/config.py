import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sentinel:sentinel@localhost:5432/log_sentinel",
)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "16100"))
API_SHARED_TOKEN = os.getenv("API_SHARED_TOKEN", "").strip()
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "monitor@aihubautomate.com").strip()
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "marcelo@aiknow.ai").strip()
