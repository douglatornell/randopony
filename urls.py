"""URL map for RandoPony site.

"""
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import handler500
from django.conf.urls.defaults import handler404
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    # Resolve '/' to the pasture (top level) app
    (r'', include('randopony.pasture.urls', namespace='pasture')),
    # Brevet pre-registration
    (r'^register/', include('randopony.register.urls', namespace='register')),
    # Populaire pre-registration
    (r'^populaires/',
     include('randopony.populaires.urls', namespace='populaires')),
    # Django auto-generated site admin
    (r'^admin/', include(admin.site.urls)),
)
