"""View functions for RandoPony top level (pasture) app.

"""
# Django:
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
# RandoPony:
from randopony.register.helpers import email2words


def home(request):
    """Display the welcome information with links to brevets and
    populaires lists in the sidebar.
    """
    context = RequestContext(request, {
        'admin_email': email2words(settings.ADMINS[0][1]),
    })
    response = render_to_response('pasture/templates/derived/home.html', context)
    return response
