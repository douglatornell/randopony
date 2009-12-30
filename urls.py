"""URL map for RandoPony site.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-05
"""
from django.conf.urls.defaults import *
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    # Resolve '/' to the register app until there are more apps
    (r'', include('randopony.register.urls')),
    # Brevet pre-registration
    (r'^register/', include('randopony.register.urls')),
    # Django auto-generated site admin
    (r'^admin/', include(admin.site.urls)),
)
