"""URL map for RandoPony populaires app.
"""
# Django:
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
# RandoPony:
from . import views


DAYS = '(0*)[1-9]|[12][0-9]|3[01]'
MONTHS = '(?i)Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
YEAR = '20\d\d'

event_pattern = (
    r'^(?P<short_name>\w+)/(?P<date>({days})({months})({year}))'
      .format(days=DAYS, months=MONTHS, year=YEAR)
)

urlpatterns = patterns(
    '',
    # Populaires app home page; list of events available for pre-registration
    url(r'^$', views.populaires_list, name='populaires-list'),

    # Populaire page with rider list
    url('{0}/$'.format(event_pattern), views.populaire, name='populaire'),

    # Populaire page with rider pre-registration confirmation message
    url('{0}/(?P<rider_id>\d+)/$'.format(event_pattern),
        views.populaire, name='prereg-confirm'),

    # Populaire page with rider pre-registration duplication message
    url('{0}/(?P<rider_id>\d+)/duplicate/$'.format(event_pattern),
        views.populaire, name='prereg-duplicate'),

    # Populaire re-registration form page
    url('{0}/form/$'.format(event_pattern),
        views.registration_form, name='form'),

    # List of rider email addresses for populaire
    url('{0}/rider-emails/(?P<uuid>[a-f0-9\-]+)/$'.format(event_pattern),
        views.rider_emails, name='rider-emails'),
)
