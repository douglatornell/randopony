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
    # Region brevet pages
    (r'^(?P<region>(%(REGIONS)s))-events/$' % vars(), 'region_brevets'),
    # Brevet page with rider list
    (r'^(?P<region>(%(REGIONS)s))(?P<event>%(EVENTS)s)/'
      '(?P<date>(%(DAYS)s)(%(MONTHS)s)(%(YEAR)s))/$' % vars(),
      'brevet'),
    # Brevet page with rider pre-registration confirmation message
    (r'^(?P<region>(%(REGIONS)s))(?P<event>%(EVENTS)s)/'
      '(?P<date>(%(DAYS)s)(%(MONTHS)s)(%(YEAR)s))/(?P<rider_id>\d+)/$' % vars(),
      'brevet'),
    # Brevet page with rider pre-registration duplication message
    (r'^(?P<region>(%(REGIONS)s))(?P<event>%(EVENTS)s)/'
      '(?P<date>(%(DAYS)s)(%(MONTHS)s)(%(YEAR)s))/'
      '(?P<rider_id>\d+)/duplicate/$' % vars(),
      'brevet'),
    # Rider pre-registration form page
    (r'^(?P<region>(%(REGIONS)s))(?P<event>%(EVENTS)s)/'
      '(?P<date>(%(DAYS)s)(%(MONTHS)s)(%(YEAR)s))/form/$' % vars(),
      'registration_form'),
    (r'^organizer_info/$', 'organizer_info'),
    (r'^about_pony/$', 'about_pony'),
)
