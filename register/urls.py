"""URL map for RandoPony site.

"""
# Django:
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
# Application:
import randopony.register.helpers as h
import randopony.register.models as model
import randopony.register.views as views


REGIONS = '(?i)%s' % '|'.join(model.REGIONS.keys())
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
                       
    # Region brevet pages (REGIONS regex precludes making this a named URL)
    url(r'^(?P<region>({0}))-events/$'.format(REGIONS), views.region_brevets),
                       
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
    url('{0}/rider-emails/$'.format(event_pattern),
        views.brevet_rider_emails,
        name='rider-emails'),
                       
    # What's up with the pony page
    url(r'^about_pony/$', direct_to_template,
        {
            'template': 'derived/about-pony.html'
        },
        name='about_pony'),

    # Info for brevet organizers page
    url(r'^organizer_info/$', direct_to_template,
        {
            'template': 'derived/organizer-info.html',
            'extra_context': {
                'admin_email': h.email2words(settings.ADMINS[0][1])
            }
        },
        'organizer_info'),
)
