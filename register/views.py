"""View functions for RandoPony site register app.
"""
# Standard library:
from datetime import datetime
from datetime import timedelta
# Django:
from django.conf import settings
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
# RandoPony:
from .models import Brevet
from .models import BrevetRider
from .models import REGIONS
from .models import RiderForm
from .models import RiderFormWithoutInfoQuestion
from .tasks import email_to_rider
from .tasks import email_to_organizer
from .tasks import update_google_spreadsheet
from ..pasture.helpers import email2words
from ..pasture.models import Link


def home(request):
    """Display the welcome information and list of regions in the sidebar.
    """
    seven_days_ago = datetime.today().date() - timedelta(days=7)
    brevet_list = Brevet.objects.exclude(date__lt=(seven_days_ago))
    regions = sorted(list(set([brevet.region for brevet in brevet_list])))
    region_list = [{
        'abbrev': region,
        'long_name': REGIONS[region]
        } for region in regions]
    context = RequestContext(request, {
        'regions': region_list,
        'admin_email': email2words(settings.ADMINS[0][1])
    })
    response = render_to_response('register/home.html', context)
    return response


def region_brevets(request, region):
    """Display a region image and the list of brevets in the sidebar.
    """
    seven_days_ago = datetime.today().date() - timedelta(days=7)
    brevet_list = Brevet.objects.filter(
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
    context = RequestContext(request, {
        'region': {
            'abbrev': region,
            'long_name': REGIONS[region]},
        'image': mapping[region],
        'brevets': brevet_list,
    })
    response = render_to_response('register/region_brevets.html', context)
    return response


def brevet(request, region, event, date, rider_id=None):
    """Display the brevet information, pre-registered riders list, and
    sometimes the registration confirmation, or duplicate registration
    flash message.
    """
    brevet = get_object_or_404(
        Brevet, region=region, event=event,
        date=datetime.strptime(date, '%d%b%Y').date())
    if brevet.in_past:
        template = 'pasture/past_event.html'
        context = RequestContext(request, {
            'event': brevet,
            'results_url': brevet.in_past
        })
    else:
        rider_list = BrevetRider.objects.filter(
            brevet__region=region, brevet__event=event,
            brevet__date=brevet.date)
        try:
            rider = BrevetRider.objects.get(pk=int(rider_id))
            rider_email = rider.email
        except (TypeError, BrevetRider.DoesNotExist, AttributeError):
            rider = rider_email = None
        template = 'register/brevet.html'
        event_waiver_url = Link.objects.get(key='event_waiver_url').url
        membership_form_url = Link.objects.get(key='membership_form_url').url
        context = RequestContext(request, {
            'brevet': brevet,
            'region': dict(abbrev=region, long_name=REGIONS[region]),
            'registration_closed': brevet.registration_closed,
            'brevet_started': brevet.started,
            'show_filler_photo': len(rider_list) < 15,
            'rider_list': rider_list,
            'rider': rider,
            'rider_email': rider_email,
            'duplicate_registration': request.path.endswith('duplicate/'),
            'event_waiver_url': event_waiver_url,
            'membership_form_url': membership_form_url,
        })
    response = render_to_response(template, context)
    return response


def registration_form(request, region, event, date):
    """Brevet registration form page.
    """
    brevet = get_object_or_404(
        Brevet, region=region, event=event,
        date=datetime.strptime(date, '%d%b%Y').date())
    if brevet.registration_closed:
        raise Http404
    form_class = (RiderForm if brevet.info_question
                  else RiderFormWithoutInfoQuestion)
    if request.method == 'POST':
        # Process submitted form data
        rider = form_class(
            request.POST, instance=BrevetRider(brevet=brevet))
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
    event_waiver_url = Link.objects.get(key='event_waiver_url').url
    membership_form_url = Link.objects.get(key='membership_form_url').url
    context = RequestContext(request, {
        'brevet': brevet,
        'region_name': REGIONS[region],
        'form': form,
        'captcha_question': settings.REGISTRATION_FORM_CAPTCHA_QUESTION,
        'event_waiver_url': event_waiver_url,
        'membership_form_url': membership_form_url,
    })
    response = render_to_response('register/registration_form.html', context)
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
        Brevet, region=region, event=event, date=brevet_date)
    if uuid != str(brevet.uuid) or brevet.in_past:
        raise Http404
    rider_list = BrevetRider.objects.filter(
        brevet__region=region, brevet__event=event, brevet__date=brevet_date)
    email_list = (', '.join(rider.email for rider in rider_list)
                  or 'No riders have registered yet!')
    return HttpResponse(email_list, mimetype='text/plain')


def _process_registration(brevet, rider, request):
    """Process rider pre-registration for brevet.
    """
    brevet_page = 'register/{0.region}{0.event}/{0.date:%d%b%Y}'.format(brevet)
    # Check for duplicate registration
    try:
        check_rider = BrevetRider.objects.get(
            first_name=rider.first_name, last_name=rider.last_name,
            email=rider.email, brevet=brevet)
        # Redirect to brevet page with duplicate flag to
        # trigger appropriate flash message
        return '/{0}/{1:d}/duplicate/'.format(brevet_page, check_rider.pk)
    except BrevetRider.DoesNotExist:
        # Save new rider pre-registration and send emails to
        # rider and brevet organizer
        rider.save()
        update_google_spreadsheet.delay(brevet.pk)
        host = request.get_host()
        email_to_rider.delay(brevet.pk, rider.pk, host)
        email_to_organizer.delay(brevet.pk, rider.pk, host)
        # Redirect to brevet page with rider record id to
        # trigger registration confirmation flash message
        return '/{0}/{1:d}/'.format(brevet_page, rider.pk)
