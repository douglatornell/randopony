"""URL map for RandoPony top level (pasture) app.
"""
# Django:
from django.conf import settings
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.views.generic.base import TemplateView
# RandoPony:
from . import views
from .helpers import email2words


class OrganizerInfoTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(
            OrganizerInfoTemplateView, self).get_context_data(**kwargs)
        context.update({
            'admin_email': email2words(settings.ADMINS[0][1])
        })
        return context


urlpatterns = patterns(
    '',
    # Site home page
    url(r'^$', views.home, name='home'),

    # Info for event organizers page
    url(r'^organizer-info/$',
        OrganizerInfoTemplateView.as_view(
            template_name='pasture/organizer_info.html'),
        name='organizer-info'),

    # What's up with the pony page
    url(r'^about-pony/$',
        TemplateView.as_view(template_name='pasture/about_pony.html'),
        name='about-pony'),
)
