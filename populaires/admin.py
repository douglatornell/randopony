"""Admin configuation for RandoPony populaires app.

"""
from __future__ import absolute_import
# Django:
from django import forms
from django.conf import settings
from django.contrib import admin
from django.core import mail
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.template.loader import render_to_string
# Google Docs:
from gdata.docs.client import DocsClient
# RandoPony:
from .models import Populaire
from ..helpers import get_rider_list_template
from ..helpers import google_docs_login
from ..helpers import share_rider_list_publicly
        

class CustomBrevetAdminForm(forms.ModelForm):
    """Custom brevet admin forms to validate organizer email
    address(es).

    Facilitates multiple organizer addresses as a comma separated list.
    """
    class Meta:
        model = Populaire

    def clean_organizer_email(self):
        data = _clean_email_address_list(self.cleaned_data['organizer_email'])
        return data


class PopulaireAdmin(admin.ModelAdmin):
    """Customize presentation of Populaire instance in admin.
    """
    # Set the fields that appear on the edit form, and the order they
    # appear in
    fieldsets = [(None, {'fields': 'event_name '
                                   'short_name '
                                   'date '
                                   'location '
                                   'time '
                                   'organizer_email '
                                   'registration_closes '
                                   'entry_form_url '
                                   'entry_form_url_label '
                                   .split()}),
    ]
    actions = [
        'create_rider_list_spreadsheet',
        'notify_webmaster',
#         'notify_populaire_organizer',
    ]

    
    def create_rider_list_spreadsheet(self, request, queryset):
        """Create a Google Docs rider list spreadsheet from the rider
        list template for the populaire(s) in the queryset.
        
        Handler for create_rider_list_spreadsheet admin action.
        """
        client = google_docs_login(DocsClient)
        docs_count = 0
        pop_count = queryset.count()
        for pop in queryset:
            if not pop.google_doc_id:
                template = get_rider_list_template(
                    'Populaire Rider List Template', client)
                created_doc = client.copy(template, unicode(pop))
                share_rider_list_publicly(created_doc, client)
                pop.google_doc_id = created_doc.resource_id.text
                pop.save()
                docs_count += 1
        if docs_count == 0:
            msg = 'No rider lists created!'
        elif docs_count == 1:
            msg = 'Rider list created for 1 populaire.'
        else:
            msg = 'Rider lists created for {0} populaires.'.format(docs_count)
        diff = pop_count - docs_count
        if diff:
            if diff == 1:
                msg += ' Populaire already had a rider list.'
            else:
                msg += ' {0} populaires already had rider lists.'.format(diff)
        self.message_user(request, msg)


    def notify_webmaster(self, request, queryset):
        _notify_webmaster(request, queryset)
        brevets_count = queryset.count()
        if brevets_count == 1:
            msg_bit = 'URL for 1 populaire'
        else:
            msg_bit = 'URLs for {0} populaires'.format(brevets_count)
        self.message_user(request, '{0} sent to webmaster'.format(msg_bit))

admin.site.register(Populaire, PopulaireAdmin)


def _clean_email_address_list(data):
    """Custom validator for a comma separated list of email addresses.
    """
    for email in (email.strip() for email in data.split(',')):
        validate_email(email)
    return data


def _notify_webmaster(request, queryset):
    """Send email message to club webmaster containing the URL of the
    pre-registration page for the populaire(s) in the queryset.

    Handler for notify_webmaster admin action.
    """
    for pop in queryset:
        pop_page = reverse(
            'populaires:populaire',
            args=(pop.short_name, pop.date.strftime('%d%b%Y')))
        host = request.get_host()
        pop_page_url = 'http://{0}{1}'.format(host, pop_page)
        email = mail.EmailMessage(
            subject='RandoPony Pre-registration Page for {0}'.format(pop),
            body=render_to_string(
                'populaires/templates/email/to_webmaster.txt',
                {'event': pop,
                 'event_page_url': pop_page_url,
                 'admin_email': settings.ADMINS[0][1],
                }
            ),
            from_email=settings.REGISTRATION_EMAIL_FROM,
            to=[settings.WEBMASTER_EMAIL],
        )
        email.send()

