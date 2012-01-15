"""URL map for RandoPony brevets & events registration app.
"""
# Django:
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
# RandoPony:
from randopony.register import models
from randopony.register import views


REGIONS = '{0}'.format('|'.join(models.REGIONS.keys()))
EVENTS = '[12]000|1200|[2346]00|dinner|AGM'
DAYS = '(0*)[1-9]|[12][0-9]|3[01]'
MONTHS = '(?i)Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
YEAR = '20\d\d'

event_pattern = (
    r'^(?P<region>({regions}))(?P<event>{events})/'
      '(?P<date>({days})({months})({year}))'
      .format(regions=REGIONS, events=EVENTS,
              days=DAYS, months=MONTHS, year=YEAR)
)

urlpatterns = patterns('',
    # Register app home page
    url(r'^$', views.home, name='home'),

    # Region brevet pages
    url(r'(?P<region>({0}))-events/$'.format(REGIONS),
        views.region_brevets,
        name='region-brevets'),

    # Brevet page with rider list
    url('{0}/$'.format(event_pattern), views.brevet, name='brevet'),

    # Brevet page with rider pre-registration confirmation message
    url('{0}/(?P<rider_id>\d+)/$'.format(event_pattern),
        views.brevet,
        name='prereg-confirm'),

    # Brevet page with rider pre-registration duplication message
    url('{0}/(?P<rider_id>\d+)/duplicate/$'.format(event_pattern),
        views.brevet,
        name='prereg-duplicate'),

    # Rider pre-registration form page
    url('{0}/form/$'.format(event_pattern),
        views.registration_form,
        name='form'),

    # List of rider email addresses for brevet
    url('{0}/rider-emails/(?P<uuid>[a-f0-9\-]+)/$'.format(event_pattern),
        views.brevet_rider_emails,
        name='rider-emails'),
)
