"""URL map for RandoPony top level (pasture) app.

"""
# Django:
from django.conf import settings
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.views.generic.simple import direct_to_template
# RandoPony:
from randopony.register.helpers import email2words
from randopony.pasture import views


urlpatterns = patterns(
    '',
    # Site home page
    url(r'^$', views.home, name='home'),

    # Info for event organizers page
    url(r'^organizer-info/$', direct_to_template,
        {
            'template': 'derived/organizer_info.html',
            'extra_context': {
                'admin_email': email2words(settings.ADMINS[0][1])
            }
        },
        'organizer-info'),
                       
    # What's up with the pony page
    url(r'^about-pony/$', direct_to_template,
        {
            'template': 'derived/about_pony.html'
        },
        name='about-pony'),
)
