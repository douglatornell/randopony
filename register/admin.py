"""Admin configuration for RandoPony site register app.

"""
# Django:
from django import forms
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.core.validators import validate_email
from django.template.loader import render_to_string
# Google docs:
import gdata.acl.data
import gdata.docs.client
# Model classes:
from randopony.register.models import Brevet
from randopony.register.models import BrevetRider
from randopony.register.models import ClubEvent
        

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
    radio_fields = {'event': admin.HORIZONTAL}

    actions = ['notify_webmaster', 'create_rider_list_spreadsheet']

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

    def _google_docs_login(self, service):
        client = service()
        client.ssl = True
        client.ClientLogin(
            settings.GOOGLE_DOCS_EMAIL, settings.GOOGLE_DOCS_PASSWORD,
            'randopony')
        return client

    def _get_rider_list_template(self, client):
        docs = client.GetDocList()
        for doc in docs.entry:
            if doc.title.text == 'Brevet Rider List Template':
                template = doc
                break
        return template

    def _share_rider_list_publicly(self, doc, client):
        scope = gdata.acl.data.AclScope(type='default')
        role = gdata.acl.data.AclRole(value='reader')
        acl_entry = gdata.acl.data.AclEntry(scope=scope, role=role)
        client.Post(acl_entry, doc.get_acl_feed_link().href)

    def create_rider_list_spreadsheet(self, request, queryset):
        client = self._google_docs_login(gdata.docs.client.DocsClient)
        docs_count = 0
        brevets_count = queryset.count()
        for brevet in queryset:
            if not brevet.google_doc_id:
                template = self._get_rider_list_template(client)
                created_doc = client.copy(template, unicode(brevet))
                self._share_rider_list_publicly(created_doc, client)
                brevet.google_doc_id = created_doc.resource_id.text
                brevet.save()
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
                msg += ' {0} brevets already had rider lists.'
        self.message_user(request, msg)
    description = 'Copy Google Docs rider list template for brevet(s)'
    create_rider_list_spreadsheet.short_description = description
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

    Handle for notify_webmaster admin actions.
    """
    for event in queryset:
        event_page = reverse(
            'register:brevet',
            args=(event.region, event.event, event.date.strftime('%d%b%Y')))
        host = request.get_host()
        event_page_url = 'http://{0}{1}'.format(host, event_page)
        email = mail.EmailMessage(
            subject='RandoPony Pre-registration Page for {0}'.format(event),
            body=render_to_string(
                'email/to_webmaster.txt',
                {'event': event,
                 'event_page_url': event_page_url,
                 'admin_email': settings.ADMINS[0][1]}
            ),
            from_email=settings.REGISTRATION_EMAIL_FROM,
            to=[settings.WEBMASTER_EMAIL],
        )
        email.send()
