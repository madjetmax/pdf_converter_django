from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task(mail_subject, message, from_email, to_emails):

    send_mail(
        mail_subject, 
        message, 
        from_email,
        to_emails
    )