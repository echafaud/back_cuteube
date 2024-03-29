import os

from dotenv import load_dotenv

load_dotenv('.env-prod')

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
SECRET = os.environ.get("SECRET")
BOTO_SERVICE_NAME = os.environ.get("BOTO_SERVICE_NAME")
BOTO_ENDPOINT_URL = os.environ.get("BOTO_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
FINGERPRINT_API_KEY = os.environ.get("FINGERPRINT_API_KEY")
FINGERPRINT_API_REGION = os.environ.get("FINGERPRINT_API_REGION")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_LOGIN = os.environ.get("SMTP_LOGIN")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
ORIGINS = os.environ.get("ORIGINS").split(',')
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
COOKIE_DOMAIN = os.environ.get("COOKIE_DOMAIN")
