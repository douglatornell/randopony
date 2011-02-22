"""View functions for RandoPony top level (pasture) app.

"""
# Standard library:
from datetime import datetime
from datetime import timedelta
# Django:
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
# RandoPony:
from randopony.register.helpers import email2words
from randopony.register.models import Brevet


def home(request):
    """Display the welcome information with links to brevets and
    populaires lists in the sidebar.
    """
    seven_days_ago = datetime.today().date() - timedelta(days=7)
    brevet_list = Brevet.objects.exclude(
        date__lt=(seven_days_ago))
    context = RequestContext(request, {
        'admin_email': email2words(settings.ADMINS[0][1]),
        'brevets': brevet_list,
    })
    response = render_to_response('pasture/templates/derived/home.html', context)
    return response
