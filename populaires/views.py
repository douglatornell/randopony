"""View functions for RandoPony populaires app.
"""
# Standard library:
from datetime import datetime
from datetime import timedelta
# Django:
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
# RandoPony:
from .models import Populaire
from .models import Rider
from .models import RiderForm
from .tasks import update_google_spreadsheet
from .tasks import email_to_rider
from .tasks import email_to_organizer
from ..pasture.helpers import email2words


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
    response = render_to_response('populaires/populaires_list.html', context)
    return response


def populaire(request, short_name, date, rider_id=None):
    """Display the populaire information, pre-registered riders list,
    and sometime the registration confirmation, or duplicate
    registration flash message.
    """
    pop = get_object_or_404(
        Populaire, short_name=short_name,
        date=datetime.strptime(date, '%d%b%Y').date())
    if pop.in_past:
        template = 'pasture/past_event.html'
        context = RequestContext(request, {
            'event': pop,
            'results_url': pop.in_past,
        })
    else:
        rider_list = Rider.objects.filter(
            populaire__short_name=short_name, populaire__date=pop.date)
        try:
            rider = Rider.objects.get(pk=int(rider_id))
        except (Rider.DoesNotExist, TypeError):
            rider = None
        template = 'populaires/populaire.html'
        context = RequestContext(request, {
            'populaire': pop,
            'registration_closed': pop.registration_closed,
            'event_started': pop.started,
            'rider': rider,
            'duplicate_registration': request.path.endswith('duplicate/'),
            'rider_list': rider_list,
            'show_filler_photo': len(rider_list) < 15,
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
            url = _process_registration(pop, new_rider, request)
            return redirect(url)
    else:
        # Unbound form to render entry form
        form = RiderForm(distance_choices=distance_choices)
    context = RequestContext(request, {
        'populaire': pop,
        'form': form,
        'captcha_question':
            'Are you a human? Are you a cyclist? Please prove it. '
            'A bicycle has ___ wheels. Fill in the blank:',
    })
    response = render_to_response('populaires/registration_form.html', context)
    return response


def _process_registration(populaire, rider, request):
    """Process rider pre-registration for populaire.
    """
    try:
        # Check for duplicate registration
        check_rider = Rider.objects.get(
            first_name=rider.first_name, last_name=rider.last_name,
            email=rider.email, populaire=populaire)
        url = reverse(
            'populaires:prereg-duplicate',
            args=(populaire.short_name, populaire.date.strftime('%d%b%Y'),
                  check_rider.id))
    except Rider.DoesNotExist:
        # Save new rider pre-registration and send emails to
        # rider and brevet organizer
        rider.save()
        update_google_spreadsheet.delay(populaire.pk)
        email_to_rider.delay(populaire.pk, rider.pk, request.get_host())
        email_to_organizer.delay(populaire.pk, rider.pk, request.get_host())
        url = reverse(
            'populaires:prereg-confirm',
            args=(populaire.short_name, populaire.date.strftime('%d%b%Y'),
                  rider.id))
    return url


def rider_emails(request, short_name, date, uuid):
    """Display a comma separated list of email addresses for the
    riders that have pre-registered for a populaire.

    The URL that requests this view includes a namespace UUID for the
    populaire to provide a measure of protection from email address
    collecting 'bots.

    Requests for this view more than 7 days after the populaire will
    fail with a 404.
    """
    pop = get_object_or_404(
        Populaire, short_name=short_name,
        date=datetime.strptime(date, '%d%b%Y').date())
    if uuid != str(pop.uuid) or pop.in_past:
        raise Http404
    rider_list = Rider.objects.filter(
        populaire__short_name=short_name, populaire__date=pop.date)
    email_list = (', '.join(rider.email for rider in rider_list)
                  or 'No riders have registered yet!')
    return HttpResponse(email_list, mimetype='text/plain')
