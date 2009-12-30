"""Admin configuration for RandoPony site register app.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-05
"""
# Django:
from django.contrib import admin
# Application:
from randopony.register.models import Brevet, Rider


class BrevetAdmin(admin.ModelAdmin):
    """Customize presentation of Brevet instance in admin.
    """
    # Set the grouping and order of the fields in the edit form
    fieldsets = [
        (None, {'fields': ['region', 'distance', 'date', 'route_name',
                           'start_location', 'start_time', 
                           'organizer_email','qual_info_question' ]}),
    ]
    # Display the brevets distance choices as radio buttons instead of
    # a select list
    radio_fields = {'distance': admin.HORIZONTAL}


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
        ('Qualifying info', {'fields': ['club_member', 'qual_info']})
    ]


admin.site.register(Brevet, BrevetAdmin)
admin.site.register(Rider, RiderAdmin)
