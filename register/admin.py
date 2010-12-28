"""Admin configuration for RandoPony site register app.

"""
# Django:
from django import forms
from django.contrib import admin
from django.core.validators import validate_email
# Model classes:
from randopony.register.models import Brevet
from randopony.register.models import BrevetRider
from randopony.register.models import ClubEvent


def clean_email_address_list(data):
    """Custom validator for a comma separated list of email addresses.
    """
    for email in (email.strip() for email in data.split(',')):
        validate_email(email)
    return data


class CustomBrevetAdminForm(forms.ModelForm):
    """Custom brevet admin forms to validate organizer email
    address(es).

    Facilitates multiple organizer addresses as a comma separated list.
    """
    class Meta:
        model = Brevet

    def clean_organizer_email(self):
        data = clean_email_address_list(self.cleaned_data['organizer_email'])
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
admin.site.register(Brevet, BrevetAdmin)


class CustomClubEventAdminForm(forms.ModelForm):
    """Custom club event admin forms to validate organizer email
    address(es).

    Facilitates multiple organizer addresses as a comma separated list.
    """
    class Meta:
        model = ClubEvent

    def clean_organizer_email(self):
        data = clean_email_address_list(self.cleaned_data['organizer_email'])
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
