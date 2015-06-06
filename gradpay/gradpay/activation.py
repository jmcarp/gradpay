from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

import settings


def send_activation_email(survey):

    # Build email context
    mail_context = {
        'activation_key': survey.activation_key,
        'site': Site.objects.get_current(),
    }

    # Build email subject
    subject = render_to_string('activation_email_subject.txt', mail_context)
    subject = ''.join(subject.splitlines())

    # Build email message
    message = render_to_string('activation_email.txt', mail_context)

    # Send email
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [survey.email])
