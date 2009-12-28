"""URL map for RandoPony site.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-05
"""
from django.conf.urls.defaults import *
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    (r'^register/', include('randopony.register.urls')),
    (r'^admin/', include(admin.site.urls)),
)
