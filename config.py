import os
from dotenv import load_dotenv

load_dotenv(os.path.join(".env"))

PORT = int(os.environ.get("PORT"))
BOT_PORT = int(os.environ.get("BOT_PORT"))
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(",")

# Postgres db informations
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Telegram bot
BOT_API_TOKEN: str = os.environ.get("BOT_API_TOKEN") or ""
WEBHOOK_URL: str = os.environ.get("WEBHOOK_URL") or ""
NEWSLETTER_URL: str = os.environ.get("NEWSLETTER_URL") or ""
WEBAPP_URL: str = os.environ.get("WEBAPP_URL") or ""
ADMIN_GROUP_ID: str = os.environ.get("ADMIN_GROUP_ID") or ""

# Scat
SCAT_API_KEY = os.environ.get("SCAT_API_KEY") or ""
SCAT_API_URL = os.environ.get("SCAT_API_URL") or ""