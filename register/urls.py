"""URL map for RandoPony site.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-05
"""
# Django:
from django.conf.urls.defaults import patterns
# Application:
import randopony.register.models as model


REGIONS = '(?i)%s' % '|'.join(model.REGIONS.keys())
EVENTS = '[12]000|1200|[2346]00|dinner|AGM'
DAYS = '(0*)[1-9]|[12][0-9]|3[01]'
MONTHS = '(?i)Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
YEAR = '20\d\d'

urlpatterns = patterns('randopony.register.views',
    (r'^$', 'home'),
    (r'^organizer_info/$', 'organizer_info'),
                       
    # Region brevet pages
    (r'^(?P<region>({0}))-events/$'.format(REGIONS), 'region_brevets'),
    # Brevet page with rider list
    (r'^(?P<region>({regions}))(?P<event>{events})/'
      '(?P<date>({days})({months})({year}))/$'
      .format(regions=REGIONS, events=EVENTS,
              days=DAYS, months=MONTHS, year=YEAR),
      'brevet'),
                       
    # Brevet page with rider pre-registration confirmation message
    (r'^(?P<region>({regions}))(?P<event>{events})/'
      '(?P<date>({days})({months})({year}))/(?P<rider_id>\d+)/$'
      .format(regions=REGIONS, events=EVENTS,
              days=DAYS, months=MONTHS, year=YEAR),
      'brevet'),
                       
    # Brevet page with rider pre-registration duplication message
    (r'^(?P<region>({regions}))(?P<event>{events})/'
      '(?P<date>({days})({months})({year}))/'
      '(?P<rider_id>\d+)/duplicate/$'
      .format(regions=REGIONS, events=EVENTS,
              days=DAYS, months=MONTHS, year=YEAR),
      'brevet'),
                       
    # Rider pre-registration form page
    (r'^(?P<region>({regions}))(?P<event>{events})/'
      '(?P<date>({days})({months})({year}))/form/$'
      .format(regions=REGIONS, events=EVENTS,
              days=DAYS, months=MONTHS, year=YEAR),
      'registration_form'),
)

urlpatterns += patterns('django.views.generic.simple',
    (r'^about_pony/$', 'direct_to_template',
     {'template': 'derived/about/about-pony.html'},
     'about_pony')
)
