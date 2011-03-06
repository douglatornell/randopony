"""View functions for RandoPony populaires app.

"""
from __future__ import absolute_import
# Standard library:
from datetime import datetime
from datetime import timedelta
import os
# Django:
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
# Google Docs:
from gdata.spreadsheet.service import SpreadsheetsService
# RandoPony:
from ..helpers import email2words
from ..helpers import google_docs_login
from .models import Populaire
from .models import Rider
from .models import RiderForm


def _qualify_template(template):
    return os.path.join('populaires/templates', template)


def populaires_list(request):
    """Display the populaire re-registration welcome information and
    list of events in the sidebar.
    """
    seven_days_ago = datetime.today().date() - timedelta(days=7)
    pop_list = Populaire.objects.exclude(date__lt=(seven_days_ago))
    template = _qualify_template('derived/populaires_list.html')
    context = RequestContext(request, {
        'events': pop_list,
        'admin_email': email2words(settings.ADMINS[0][1]),
    })
    response = render_to_response(template, context)
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
        template = 'pasture/templates/derived/past_event.html'
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
        template = _qualify_template('derived/populaire.html')
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
    template = _qualify_template('derived/registration_form.html')
    context = RequestContext(request, {
        'populaire': pop,
        'form': form,
        'captcha_question': 
            'Are you a human? Are you a cyclist? Please prove it. '
            'A bicycle has ___ wheels. Fill in the blank:',
    })
    response = render_to_response(template, context)
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
        _update_google_spreadsheet(populaire)
        _email_to_rider(populaire, rider, request.get_host())
        _email_to_organizer(populaire, rider, request.get_host())
        url = reverse(
            'populaires:prereg-confirm',
            args=(populaire.short_name, populaire.date.strftime('%d%b%Y'),
                  rider.id))
    return url


def _update_google_spreadsheet(populaire):
    """Update the rider list spreadsheet on Google docs, preserving
    the list's sorted by last name order.
    """
    client = google_docs_login(SpreadsheetsService)
    key = populaire.google_doc_id.split(':')[1]
    spreadsheet_list = client.GetListFeed(key)
    spreadsheet_rows = len(spreadsheet_list.entry)
    rider_list = Rider.objects.filter(
        populaire__short_name=populaire.short_name,
        populaire__date=populaire.date)
    # Update the rows already in the spreadsheet
    for row, rider in enumerate(rider_list[:spreadsheet_rows]):
        rider_number = row + 1
        new_row_data = _make_spreadsheet_row_dict(rider_number, rider)
        client.UpdateRow(spreadsheet_list.entry[row], new_row_data)
    # Add remaining rows
    for row, rider in enumerate(rider_list[spreadsheet_rows:]):
        rider_number = spreadsheet_rows + row + 1
        row_data = _make_spreadsheet_row_dict(rider_number, rider)
        client.InsertRow(row_data, key)


def _make_spreadsheet_row_dict(rider_number, rider):
        row_data = {
            'ridernumber': str(rider_number),
            'lastname': rider.last_name,
            'firstname': rider.first_name,
            'distance': str(rider.distance),
        }
        return row_data


def _email_to_rider(populaire, rider, host):
    """Send pre-registration confirmation email to rider.
    """
    pop_page = reverse(
        'populaires:populaire',
        args=(populaire.short_name, populaire.date.strftime('%d%b%Y')))
    pop_page_url = 'http://{0}{1}'.format(host, pop_page)
    template = _qualify_template('email/to_rider.txt')
    email = mail.EmailMessage(
        subject='Pre-registration Confirmation for {0}'.format(populaire),
        body=render_to_string(
            template,
            {'populaire': populaire,
             'pop_page_url': pop_page_url}),
        from_email=populaire.organizer_email,
        to=[rider.email],
        headers={
            'Sender': settings.REGISTRATION_EMAIL_FROM,
            'Reply-To': populaire.organizer_email}
    )
    email.send()



def _email_to_organizer(populaire, rider, host):
    """Send rider pre-registration notification email to event organizer(s).
    """
    pop_page = reverse(
        'populaires:populaire',
        args=(populaire.short_name, populaire.date.strftime('%d%b%Y')))
    pop_page_url = 'http://{0}{1}'.format(host, pop_page)
    template = _qualify_template('email/to_organizer.txt')
    email = mail.EmailMessage(
        subject='{0} has Pre-registered for the {1}'
                .format(rider.full_name, populaire),
        body=render_to_string(
            template,
            {'populaire': populaire,
             'rider': rider,
             'pop_page_url': pop_page_url,
             'admin_email': settings.ADMINS[0][1]}),
        from_email=settings.REGISTRATION_EMAIL_FROM,
        to=[addr.strip() for addr in populaire.organizer_email.split(',')]
    )
    email.send()
