"""View functions for RandoPony populaires app.

"""
from __future__ import absolute_import
# Standard library:
from datetime import datetime
from datetime import timedelta
# Django:
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
# RandoPony:
from ..helpers import email2words
from .models import Populaire


def populaires_list(request):
    """Display the populaire re-registration welcome information and
    list of events in the sidebar.
    """
    seven_days_ago = datetime.today().date() - timedelta(days=7)
    pop_list = Populaire.objects.exclude(date__lt=(seven_days_ago))
    context = RequestContext(request, {
        'events': pop_list,
        'admin_email': email2words(settings.ADMINS[0][1]),
    })
    response = render_to_response('derived/populaires_list.html', context)
    return response


def populaire(request, short_name, date, rider_id=None):
    """
    """
    pass
