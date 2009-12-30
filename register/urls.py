"""URL map for RandoPony site.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-05
"""
from django.conf.urls.defaults import *


REGIONS = '(?i)LM|PR|SI|VI'
DISTANCES = '[2|3|4|6|10|12|20]00'
DAYS = '(0*)[1-9]|[12][0-9]|3[01]'
MONTHS = '(?i)Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
YEAR = '20\d\d'

urlpatterns = patterns('randopony.register.views',
    (r'^$', 'home'),
    # Brevet page with rider list
    (r'^(?P<region>(%(REGIONS)s))(?P<distance>%(DISTANCES)s)/'
      '(?P<date>(%(DAYS)s)(%(MONTHS)s)(%(YEAR)s))/$' % vars(),
      'brevet'),
    # Brevet page with rider pre-registration confirmation message
    (r'^(?P<region>(%(REGIONS)s))(?P<distance>%(DISTANCES)s)/'
      '(?P<date>(%(DAYS)s)(%(MONTHS)s)(%(YEAR)s))/(?P<rider_id>\d+)/$' % vars(),
      'brevet'),
    # Brevet page with rider pre-registration duplication message
    (r'^(?P<region>(%(REGIONS)s))(?P<distance>%(DISTANCES)s)/'
      '(?P<date>(%(DAYS)s)(%(MONTHS)s)(%(YEAR)s))/'
      '(?P<rider_id>\d+)/duplicate/$' % vars(),
      'brevet'),
    # Rider pre-registration form page
    (r'^(?P<region>(%(REGIONS)s))(?P<distance>%(DISTANCES)s)/'
      '(?P<date>(%(DAYS)s)(%(MONTHS)s)(%(YEAR)s))/form/$' % vars(),
      'registration_form'),
    (r'^organizer_info/$', 'organizer_info'),
    (r'^about_pony/$', 'about_pony'),
)
