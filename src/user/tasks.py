import smtplib
from email.message import EmailMessage

from src.celery_main import celery
from src.config import SMTP_HOST, SMTP_PORT, SMTP_LOGIN, SMTP_PASSWORD


def get_email_template(user_data: dict):
    email = EmailMessage()
    email['Subject'] = 'Cutuebu'
    email['From'] = SMTP_LOGIN
    email['To'] = user_data['email']

    email.set_content(
        '<div>'
        f'<h1>Здравствуйте, {user_data["username"]}! Чтобы подтвердить Вашу почту, перейдите по ссылке ниже</h1>'
        f'<a href="https://localhost:5173/verify/{user_data["id"]}/{user_data["token"]}">Тык</a>'
        '</div>',
        subtype='html'
    )
    return email


@celery.task
def send_verify_mail(user_data: dict):
    email = get_email_template(user_data)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(email)
