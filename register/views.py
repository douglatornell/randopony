"""View functions for RandoPony site register app.

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
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import render_to_string
# Google Docs:
from gdata.spreadsheet.service import SpreadsheetsService
# RandoPony:
from ..helpers import email2words
from ..helpers import google_docs_login
import randopony.register.models as model


def _qualify_template(template):
    return os.path.join('register/templates', template)


def home(request):
    """Display the welcome information and list of regions in the sidebar.
    """
    seven_days_ago = datetime.today().date() - timedelta(days=7)
    brevet_list = model.Brevet.objects.exclude(date__lt=(seven_days_ago))
    regions = sorted(list(set([brevet.region for brevet in brevet_list])))
    region_list = [{
        'abbrev': region,
        'long_name': model.REGIONS[region]
        } for region in regions]
    template = _qualify_template('derived/home.html')
    context = RequestContext(request, {
        'regions': region_list,
        'admin_email': email2words(settings.ADMINS[0][1])
    })
    response = render_to_response(template, context)
    return response


def region_brevets(request, region):
    """Display a region image and the list of brevets in the sidebar.
    """
    seven_days_ago = datetime.today().date() - timedelta(days=7)
    brevet_list = model.Brevet.objects.filter(
            region=region
        ).exclude(
            date__lt=(seven_days_ago)
        )
    mapping = {
        'Club': {
            'file': 'AGM-Brunch.jpg',
            'alt': 'Brunch at Bedford House',
        },
        'LM': {
            'file': 'LowerMainlandQuartet.jpg',
            'alt': 'Harrison Hotspings Road',
        },
        'VI': {
            'file': 'VanIsDuo.jpg',
            'alt': 'Van Isle Duo',
        },
        'SI': {
            'file': 'SouthIntLivestock.jpg',
            'alt': 'Southern Interior Peloton',
        },
        'SW': {
            'file': 'SeaToSkyScenery.jpg',
            'alt': 'Sea to Sky Scenery',
        },
    }
    template = _qualify_template('derived/region_brevets.html')
    context = RequestContext(request, {
        'region': {
            'abbrev': region,
            'long_name': model.REGIONS[region]},
        'image': mapping[region],
        'brevets': brevet_list,
    })
    response = render_to_response(template, context)
    return response


def brevet(request, region, event, date, rider_id=None):
    """Display the brevet information, pre-registered riders list, and
    sometimes the registration confirmation, or duplicate registration
    flash message.
    """
    brevet = get_object_or_404(
        model.Brevet, region=region, event=event,
        date=datetime.strptime(date, '%d%b%Y').date())
    results_url = brevet.in_past
    if results_url:
        template = _qualify_template('derived/past_brevet.html')
        context = RequestContext(request, {
            'brevet': str(brevet),
            'results_url': results_url
        })
    else:
        rider_list = model.BrevetRider.objects.filter(
            brevet__region=region, brevet__event=event,
            brevet__date=brevet.date)
        try:
            rider = model.BrevetRider.objects.get(pk=int(rider_id))
            rider_email = email2words(rider.email)
        except (TypeError, model.BrevetRider.DoesNotExist, AttributeError):
            rider = rider_email = None
        template = _qualify_template('derived/brevet.html')
        context = RequestContext(request, {
            'brevet': brevet,
            'region': dict(abbrev=region, long_name=model.REGIONS[region]),
            'registration_closed': brevet.registration_closed,
            'brevet_started': brevet.started,
            'show_filler_photo': len(rider_list) < 15,
            'rider_list': rider_list,
            'rider': rider,
            'rider_email': rider_email,
            'duplicate_registration': request.path.endswith('duplicate/'),
        })
    response = render_to_response(template, context)
    return response


def registration_form(request, region, event, date):
    """Brevet registration form page.
    """
    brevet = get_object_or_404(
        model.Brevet, region=region, event=event,
        date=datetime.strptime(date, '%d%b%Y').date())
    if brevet.registration_closed:
        raise Http404
    form_class = (model.RiderForm if brevet.info_question
                  else model.RiderFormWithoutInfoQuestion)
    if request.method == 'POST':
        # Process submitted form data
        rider = form_class(
            request.POST, instance=model.BrevetRider(brevet=brevet))
        try:
            new_rider = rider.save(commit=False)
        except ValueError:
            # Validation error, so re-render form with rider inputs
            # and error messages
            form = rider
        else:
            url = _process_registration(brevet, new_rider, request)
            return redirect(url)
    else:
        # Unbound form to render entry form
        form = form_class()
    template = _qualify_template('derived/registration_form.html')
    context = RequestContext(request, {
        'brevet': brevet,
        'region_name': model.REGIONS[region],
        'form': form,
        'captcha_question': settings.REGISTRATION_FORM_CAPTCHA_QUESTION
    })
    response = render_to_response(template, context)
    return response


def brevet_rider_emails(request, region, event, date, uuid):
    """Display a comma separated list of email addresses for the
    riders that have pre-registered for a brevet.

    The URL that requests this view includes a namespace UUID for the
    brevet to provide a measure of protection from email address
    collecting 'bots.

    Requests for this view more than 7 days after the brevet will fail
    with a 404.
    """
    brevet_date = datetime.strptime(date, '%d%b%Y').date()
    brevet = get_object_or_404(
        model.Brevet, region=region, event=event, date=brevet_date)
    if uuid != str(brevet.uuid) or brevet.in_past:
        raise Http404
    rider_list = model.BrevetRider.objects.filter(
        brevet__region=region, brevet__event=event, brevet__date=brevet_date)
    email_list = (', '.join(rider.email for rider in rider_list)
                  or 'No riders have registered yet!')
    return HttpResponse(email_list, mimetype='text/plain')


def _process_registration(brevet, rider, request):
    """Process rider pre-registration for brevet.
    """
    brevet_page = 'register/{0.region}{0.event}/{1}'.format(
        brevet, brevet.date.strftime('%d%b%Y'))
    # Check for duplicate registration
    try:
        check_rider = model.BrevetRider.objects.get(
            first_name=rider.first_name, last_name=rider.last_name,
            email=rider.email, brevet=brevet)
        # Redirect to brevet page with duplicate flag to
        # trigger appropriate flash message
        return '/{0}/{1:d}/duplicate/'.format(brevet_page, check_rider.id)
    except model.BrevetRider.DoesNotExist:
        # Save new rider pre-registration and send emails to
        # rider and brevet organizer
        rider.save()
        _update_google_spreadsheet(brevet)
        host = request.get_host()
        _email_to_rider(brevet, rider, host)
        _email_to_organizer(brevet, rider, host)
        # Redirect to brevet page with rider record id to
        # trigger registration confirmation flash message
        return '/{0}/{1:d}/'.format(brevet_page, rider.id)


def _update_google_spreadsheet(brevet):
    """Update the rider list spreadsheet on Google docs, preserving
    the list's sorted by last name order.
    """
    client = google_docs_login(SpreadsheetsService)
    key = brevet.google_doc_id.split(':')[1]
    spreadsheet_list = client.GetListFeed(key)
    spreadsheet_rows = len(spreadsheet_list.entry)
    rider_list = model.BrevetRider.objects.filter(
        brevet__region=brevet.region, brevet__event=brevet.event,
        brevet__date=brevet.date)
    # Update the rows already in the spreadsheet
    for row, rider in enumerate(rider_list[:spreadsheet_rows]):
        rider_number = row + 1
        new_row_data = _make_spreadsheet_row_dict(rider_number, rider)
        client.UpdateRow(spreadsheet_list.entry[row], new_row_data)
        client.UpdateCell(rider_number + 1, 5, rider.info_answer, key)
    # Add remaining rows
    for row, rider in enumerate(rider_list[spreadsheet_rows:]):
        rider_number = spreadsheet_rows + row + 1
        row_data = _make_spreadsheet_row_dict(rider_number, rider)
        client.InsertRow(row_data, key)
        client.UpdateCell(rider_number + 1, 5, rider.info_answer, key)


def _make_spreadsheet_row_dict(rider_number, rider):
        row_data = {
            'ridernumber': str(rider_number),
            'lastname': rider.last_name,
            'firstname': rider.first_name,
            'clubmember': 'Y' if rider.club_member else 'N',
        }
        return row_data


def _email_to_rider(brevet, rider, host):
    """Send pre-registration confirmation email to rider.
    """
    brevet_page = reverse(
        'register:brevet',
        args=(brevet.region, brevet.event, brevet.date.strftime('%d%b%Y')))
    brevet_page_url = 'http://{0}{1}'.format(host, brevet_page)
    template = _qualify_template('email/to_rider.txt')
    email = mail.EmailMessage(
        subject='Pre-registration Confirmation for {0} Brevet'
                .format(brevet),
        body=render_to_string(
            template,
            {'brevet': brevet,
             'rider': rider,
             'brevet_page_url': brevet_page_url}),
        from_email=brevet.organizer_email,
        to=[rider.email],
        headers={
            'Sender': settings.REGISTRATION_EMAIL_FROM,
            'Reply-To': brevet.organizer_email}
    )
    email.send()


def _email_to_organizer(brevet, rider, host):
    """Send rider pre-registration notification email to event organizer(s).
    """
    brevet_page = reverse(
        'register:brevet',
        args=(brevet.region, brevet.event, brevet.date.strftime('%d%b%Y')))
    brevet_page_url = 'http://{0}{1}'.format(host, brevet_page)
    template = _qualify_template('email/to_organizer.txt')
    email = mail.EmailMessage(
        subject='{0} has Pre-registered for the {1}'
                .format(rider.full_name, brevet),
        body=render_to_string(
            template,
            {'brevet': brevet,
             'rider': rider,
             'brevet_page_url': brevet_page_url,
             'admin_email': settings.ADMINS[0][1]}),
        from_email=settings.REGISTRATION_EMAIL_FROM,
        to=[addr.strip() for addr in brevet.organizer_email.split(',')]
    )
    email.send()
