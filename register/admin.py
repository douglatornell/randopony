"""Admin configuration for RandoPony site register app.

"""
# Django:
from django import forms
from django.contrib import admin
from django.core.validators import validate_email
# Application:
from randopony.register.models import Brevet, Rider


class CustomBrevetAdminForm(forms.ModelForm):
    """Custom admin form to validate organizer email address(es).

    Facilitates multiple organizer addresses as a comma separated list.
    """
    class Meta:
        model = Brevet

    def clean_organizer_email(self):
        data = self.cleaned_data['organizer_email']
        for email in (email.strip() for email in data.split(',')):
            validate_email(email)
        return data


class BrevetAdmin(admin.ModelAdmin):
    """Customize presentation of Brevet instance in admin.
    """
    form = CustomBrevetAdminForm
    # Set the order of the fields in the edit form
    fieldsets = [
        (None, {'fields': ['region', 'event', 'date', 'route_name',
                           'start_location', 'start_time',  'alt_start_time',
                           'organizer_email','info_question' ]}),
    ]
    # Display the brevets distance choices as radio buttons instead of
    # a select list
    radio_fields = {'event': admin.HORIZONTAL}
        


class RiderAdmin(admin.ModelAdmin):
    """Customize presentation of Entrant instance in admin.
    """
    # Set the fields to display in the change-list, and its filter
    # sidebar, searching by name and brevet
    list_display = ['brevet', 'name']
    list_filter = ['brevet']
    search_fields = ['name']
    # Set the grouping and order of the fields in the edit form
    fieldsets = [
        (None, {'fields': ['brevet', 'name', 'email']}),
        ('Qualifying info', {'fields': ['club_member', 'info_answer']})
    ]


admin.site.register(Brevet, BrevetAdmin)
admin.site.register(Rider, RiderAdmin)
