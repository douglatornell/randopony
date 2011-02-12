"""Helper functions for the randopony register app.

"""
# Django:
from django.conf import settings


def email2words(email):
    """Return a slightly obfuscated version of the email address.

    Replaces @ with ' at ', and . with ' dot '.
    """
    return email.replace('@', ' at ').replace('.', ' dot ')


def google_docs_login(service):
    client = service()
    client.ssl = True
    client.ClientLogin(
        settings.GOOGLE_DOCS_EMAIL, settings.GOOGLE_DOCS_PASSWORD, 'randopony')
    return client
