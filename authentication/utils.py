import logging

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags


class Utils:
    @staticmethod
    def email_sender(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], from_email=data['from_email'],
                             to=(data['to_email'],))
        email.send()

    @staticmethod
    def send_verification_email(domain, user, access_token):
        current_site = domain
        access_token = access_token
        verification_link = reverse('email_verify', args=(access_token,))
        absurl = f"http://{current_site}{verification_link}"
        from_email = settings.EMAIL_HOST_USER
        email_body = f'Hello {user.first_name} {user.surname} Use link below to verify your account\n {absurl}'
        data = {'to_email': user.email,
                'from_email': from_email,
                'email_body': email_body,
                'email_subject': "Email verification"}
        Utils.email_sender(data)

    @staticmethod
    def send_password_update_email(user):
        from_email = settings.EMAIL_HOST_USER
        email_body = (f'Hello {user.first_name} {user.surname}. This is automatically generated email,'
                      f' your password was successfully changed ')
        data = {'to_email': user.email,
                'from_email': from_email,
                'email_body': email_body,
                'email_subject': "Password update"}
        Utils.email_sender(data)

    @staticmethod
    # @shared_task
    def send_password_reset_email(email, reset_link):
        subject = 'Password Reset'
        html_message = render_to_string('password_reset_email.html', {'reset_link': reset_link})
        plain_message = strip_tags(html_message)
        try:
            email_message = EmailMultiAlternatives(subject, plain_message, settings.EMAIL_HOST_USER, [email])
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()
        except:
            logger = logging.getLogger('email_sending')
            logger.error(f'Error during email sending to {email}.')
