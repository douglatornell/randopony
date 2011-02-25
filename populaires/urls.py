"""URL map for RandoPony populaires app.

"""
from __future__ import absolute_import
# Django:
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
# RandoPony:
from . import views


DAYS = '(0*)[1-9]|[12][0-9]|3[01]'
MONTHS = '(?i)Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
YEAR = '20\d\d'

event_pattern = (
    r'^(?P<short_name>\w+)/(?P<date>({days})({months})({year}))/$'
      .format(days=DAYS, months=MONTHS, year=YEAR)
)


urlpatterns = patterns(
    '',
    # Populaires app home page; list of events available for pre-registration
    url(r'^$', views.event_list, name='event_list'),

    # Populaire page with rider list
    url('{0}'.format(event_pattern), views.populaire, name='populaire'),
)
