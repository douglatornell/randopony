"""View functions for RandoPony populaires app.

"""
from __future__ import absolute_import
# Standard library:
from datetime import datetime
from datetime import timedelta
# Django:
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
# RandoPony:
from ..helpers import email2words
from .models import Populaire
from .models import Rider
from .models import RiderForm


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
    """Display the populaire information, pre-registered riders list,
    and sometime the registration confirmation, or duplicate
    registration flash message.
    """
    pop = get_object_or_404(
        Populaire, short_name=short_name,
        date=datetime.strptime(date, '%d%b%Y').date())
    rider_list = Rider.objects.filter(
        populaire__short_name=short_name, populaire__date=pop.date)
    template = 'derived/populaire.html'
    context = RequestContext(request, {
        'populaire': pop,
        'registration_closed': pop.registration_closed,
        'show_filler_photo': len(rider_list) < 15,
        'rider_list': rider_list,
    })
    response = render_to_response(template, context)
    return response


def registration_form(request, short_name, date):
    """Display populaire pre-registration form page.
    """
    pop = get_object_or_404(
        Populaire, short_name=short_name,
        date=datetime.strptime(date, '%d%b%Y').date())
    if pop.registration_closed:
        raise Http404
    distance_choices = [(int(dist.strip('kms').strip()), dist.strip())
                        for dist in pop.distance.split(',')]
    if request.method == 'POST':
        rider = RiderForm(
            request.POST, distance_choices=distance_choices,
            instance=Rider(populaire=pop))
        try:
            new_rider = rider.save(commit=False)
        except ValueError:
            # Validation error, so re-render form with rider inputs
            # and error messages
            form = rider
        else:
            pass
    else:
        # Unbound form to render entry form
        form = RiderForm(distance_choices=distance_choices)
    template = 'populaires/templates/derived/registration_form.html'
    context = RequestContext(request, {
        'populaire': pop,
        'form': form,
        'captcha_question': 
            'Are you a human? Are you a cyclist? Please prove it. '
            'A bicycle has ___ wheels. Fill in the blank:',
    })
    response = render_to_response(template, context)
    return response
