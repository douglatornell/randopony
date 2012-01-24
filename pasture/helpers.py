"""Helper functions for the RandoPony apps.

"""
# Google Docs:
import gdata.acl.data
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


def get_rider_list_template(template_name, client):
    docs = client.GetDocList()
    for doc in docs.entry:
        if doc.title.text == template_name:
            template = doc
            break
    return template


def share_rider_list_publicly(doc, client):
    scope = gdata.acl.data.AclScope(type='default')
    role = gdata.acl.data.AclRole(value='reader')
    acl_entry = gdata.acl.data.AclEntry(scope=scope, role=role)
    client.Post(acl_entry, doc.get_acl_feed_link().href)
