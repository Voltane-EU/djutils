from django.core import mail
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import get_template

def format_mail_message(template, subject, context):
    context.update({
        'subject': subject,
        'title': settings.TITLE,
        'http_host': settings.BASE_HTTP_HOST,
        'css': context.get('css'),
    })
    return get_template('mail/'+template).render(context)

def send_mail(subject, template, context, recipient_list, fail_silently=False):
    message = format_mail_message(template=template, subject=subject, context=context)
    return mail.send_mail(subject=subject, message=strip_tags(message), html_message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=recipient_list, fail_silently=fail_silently)

def mail_admins(subject, template, context, fail_silently=False):
    message = format_mail_message(template=template, subject=subject, context=context)
    return mail.mail_admins(subject=subject, message=strip_tags(message), html_message=message, fail_silently=fail_silently)
