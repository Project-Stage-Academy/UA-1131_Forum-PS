from django.core.mail import EmailMessage


class Utils:
    @staticmethod
    def send_verification_email(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], from_email=data['from_email'],
                             to=(data['to_email'],))
        email.send()