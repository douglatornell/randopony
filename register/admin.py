"""Admin configuration for RandoPony register app.
"""

# Django:
from django import forms
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.core.validators import validate_email
from django.template.loader import render_to_string
# Google Docs:
from gdata.docs.client import DocsClient
from gdata.spreadsheet.service import SpreadsheetsService
# RandoPony:
from .models import Brevet
from .models import BrevetRider
from .models import ClubEvent
from ..pasture.helpers import get_rider_list_template
from ..pasture.helpers import google_docs_login
from ..pasture.helpers import share_rider_list_publicly
from ..pasture.models import EmailAddress


class CustomBrevetAdminForm(forms.ModelForm):
    """Custom brevet admin forms to validate organizer email
    address(es).

    Facilitates multiple organizer addresses as a comma separated list.
    """
    class Meta:
        model = Brevet

    def clean_organizer_email(self):
        data = _clean_email_address_list(self.cleaned_data['organizer_email'])
        return data


class BrevetAdmin(admin.ModelAdmin):
    """Customize presentation of Brevet instance in admin.
    """
    form = CustomBrevetAdminForm
    # Set the order of the fields in the edit form
    fieldsets = [
        (None, {'fields': 'region event date route_name location '
                          'time alt_start_time organizer_email '
                          'info_question '
                          .split()}),
    ]
    # Display the brevets distance choices as radio buttons instead of
    # a select list
    radio_fields = {
        'event': admin.HORIZONTAL
    }
    actions = [
        'create_rider_list_spreadsheet',
        'notify_brevet_organizer',
        'notify_webmaster',
    ]

    def create_rider_list_spreadsheet(self, request, queryset):
        """Create a Google Docs rider list spreadsheet from the rider
        list template for the brevet(s) in the queryset.

        Handler for create_rider_list_spreadsheet admin action.
        """
        client = google_docs_login(DocsClient)
        docs_count = 0
        brevets_count = queryset.count()
        for brevet in queryset:
            if not brevet.google_doc_id:
                template = get_rider_list_template(
                    'Brevet Rider List Template', client)
                created_doc = client.copy_resource(template, unicode(brevet))
                share_rider_list_publicly(created_doc, client)
                brevet.google_doc_id = created_doc.resource_id.text
                brevet.save()
                self._update_rider_list_info_question(
                    brevet.google_doc_id, brevet.info_question)
                docs_count += 1
        if docs_count == 0:
            msg = 'No rider lists created!'
        elif docs_count == 1:
            msg = 'Rider list created for 1 brevet.'
        else:
            msg = 'Rider lists created for {0} brevets.'.format(docs_count)
        diff = brevets_count - docs_count
        if diff:
            if diff == 1:
                msg += ' Brevet already had a rider list.'
            else:
                msg += ' {0} brevets already had rider lists.'.format(diff)
        self.message_user(request, msg)
    description = 'Copy Google Docs rider list template for brevet'
    create_rider_list_spreadsheet.short_description = description

    def _update_rider_list_info_question(self, google_doc_id, info_question):
        client = google_docs_login(SpreadsheetsService)
        key = google_doc_id.split(':')[1]
        client.UpdateCell(1, 5, info_question, key)

    def notify_brevet_organizer(self, request, queryset):
        _notify_brevet_organizer(request, queryset)
        brevets_count = queryset.count()
        if brevets_count == 1:
            msg_bit = 'Email for 1 brevet'
        else:
            msg_bit = 'Emails for {0} brevets'.format(brevets_count)
        self.message_user(
            request, '{0} sent to organizer(s)'.format(msg_bit))
    description = 'Send email with brevet URLs to brevet organizer(s)'
    notify_brevet_organizer.short_description = description

    def notify_webmaster(self, request, queryset):
        _notify_webmaster(request, queryset)
        brevets_count = queryset.count()
        if brevets_count == 1:
            msg_bit = 'URL for 1 brevet'
        else:
            msg_bit = 'URLs for {0} brevets'.format(brevets_count)
        self.message_user(request, '{0} sent to webmaster'.format(msg_bit))
    description = 'Send email with URL for brevet to webmaster'
    notify_webmaster.short_description = description
admin.site.register(Brevet, BrevetAdmin)


class CustomClubEventAdminForm(forms.ModelForm):
    """Custom club event admin forms to validate organizer email
    address(es).

    Facilitates multiple organizer addresses as a comma separated list.
    """
    class Meta:
        model = ClubEvent

    def clean_organizer_email(self):
        data = _clean_email_address_list(self.cleaned_data['organizer_email'])
        return data


class ClubEventAdmin(admin.ModelAdmin):
    """Customize presentation of ClubEvent instance in admin.
    """
    form = CustomClubEventAdminForm
    # Set the order of the fields in the edit form
    fieldsets = [
        (None, {'fields': 'region event date location time organizer_email '
                          'info_question '
                          .split()}),
    ]
    # Display the event type choices as radio buttons instead of a
    # select list
    radio_fields = {'event': admin.HORIZONTAL}

    actions = ['notify_webmaster']

    def notify_webmaster(self, request, queryset):
        _notify_webmaster(request, queryset)
        events_count = queryset.count()
        if events_count == 1:
            msg_bit = 'URL for 1 event'
        else:
            msg_bit = 'URLs for {0} events'.format(events_count)
        self.message_user(request, '{0} sent to webmaster'.format(msg_bit))
    description = 'Send email with URL for event to webmaster'
    notify_webmaster.short_description = description
admin.site.register(ClubEvent, ClubEventAdmin)


class RiderAdmin(admin.ModelAdmin):
    """Customize presentation of Entrant instance in admin.
    """
    # Set the fields to display in the change-list, and its filter
    # sidebar, searching by name and brevet
    list_display = ['brevet', 'full_name']
    list_filter = ['brevet']
    search_fields = ['^first_name',  '^last_name']
    # Set the grouping and order of the fields in the edit form
    fieldsets = [
        (None, {'fields': ['brevet', 'first_name', 'last_name', 'email']}),
        ('Qualifying info', {'fields': ['club_member', 'info_answer']})
    ]
admin.site.register(BrevetRider, RiderAdmin)


def _clean_email_address_list(data):
    """Custom validator for a comma separated list of email addresses.
    """
    for email in (email.strip() for email in data.split(',')):
        validate_email(email)
    return data


def _notify_webmaster(request, queryset):
    """Send email message to club webmaster containing the URL of the
    pre-registration page for the event(s) in the queryset.

    Handler for notify_webmaster admin action.
    """
    webmaster_email = EmailAddress.objects.get(key='webmaster').email
    from_randopony = EmailAddress.objects.get(key='from_randopony').email
    for event in queryset:
        event_page = reverse(
            'register:brevet',
            args=(event.region, event.event, event.date.strftime('%d%b%Y')))
        host = request.get_host()
        event_page_url = 'http://{0}{1}'.format(host, event_page)
        email = mail.EmailMessage(
            subject='RandoPony Pre-registration Page for {0}'.format(event),
            body=render_to_string(
                'register/email/to_webmaster.txt',
                {'event': event,
                 'event_page_url': event_page_url,
                 'admin_email': settings.ADMINS[0][1],
                }
            ),
            from_email=from_randopony,
            to=[webmaster_email],
        )
        email.send()


def _notify_brevet_organizer(request, queryset):
    """Send email message to brevet organizer(s) containing the URLs
    of the:

    * pre-registration page
    * Google Docs rider list spreadsheet
    * pre-registered riders email address list

    for the brevet(s) in the queryset.
    """
    host = request.get_host()
    from_randopony = EmailAddress.objects.get(key='from_randopony').email
    for brevet in queryset:
        brevet_page = reverse(
            'register:brevet',
            args=(brevet.region, brevet.event, brevet.date.strftime('%d%b%Y')))
        brevet_page_url = 'http://{0}{1}'.format(host, brevet_page)
        rider_list_url = (
            'https://spreadsheets.google.com/ccc?key={0}'
            .format(brevet.google_doc_id.split(':')[1]))
        rider_emails_url = (
            'http://{0}{1}rider-emails/{2}/'
            .format(host, brevet_page, brevet.uuid))
        email = mail.EmailMessage(
            subject='RandoPony URLs for {0}'.format(brevet),
            body=render_to_string(
                'register/email/URLs_to_organizer.txt',
                {'brevet': brevet,
                 'brevet_page_url': brevet_page_url,
                 'rider_list_url': rider_list_url,
                 'rider_emails_url': rider_emails_url,
                 'admin_email': settings.ADMINS[0][1],
                },
            ),
            from_email=from_randopony,
            to=[addr.strip() for addr in brevet.organizer_email.split(',')],
        )
        email.send()
