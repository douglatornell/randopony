"""View functions for RandoPony site register app.

"""
# Standard library:
from datetime import datetime
from datetime import time
from datetime import timedelta
# Django:
from django.conf import settings
from django.core import mail
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import render_to_string
# Application:
import randopony.register.helpers as h
import randopony.register.models as model


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
    context = RequestContext(request, {
        'regions': region_list,
        'admin_email': h.email2words(settings.ADMINS[0][1])
    })
    response = render_to_response('derived/home.html', context)
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
    context = RequestContext(request, {
        'region': {
            'abbrev': region,
            'long_name': model.REGIONS[region]},
        'image': mapping[region],
        'brevets': brevet_list,
    })
    response = render_to_response('derived/region_brevets.html', context)
    return response


def _brevet_started(brevet):
    """Start window for brevet closes 1 hour after brevet start time.

    Note that the webfaction server hosting randopony is 2 hours ahead
    of Pacific time.
    """
    brevet_date_time = datetime.combine(brevet.date, brevet.time)
    server_tz_offset = 2
    one_hour = timedelta(hours=1 + server_tz_offset)
    brevet_started = datetime.now() >= brevet_date_time + one_hour
    return brevet_started


def _brevet_in_past(brevet):
    """Render a page with a link to the year's results on the club
    site for brevets more than 7 days in the past.
    """
    results_url = None
    today = datetime.today().date()
    seven_days = timedelta(days=7)
    if brevet.date < today - seven_days:
        results_url = (
            'http://randonneurs.bc.ca/results/{0}_times/{0}_times.html'
            .format(str(brevet.date.year)[-2:]))
    return results_url


def brevet(request, region, event, date, rider_id=None):
    """Display the brevet information, pre-registered riders list, and
    sometimes the registration confirmation, or duplicate registration
    flash message.
    """
    brevet = get_object_or_404(
        model.Brevet, region=region, event=event,
        date=datetime.strptime(date, '%d%b%Y').date())
    results_url = _brevet_in_past(brevet)
    if results_url:
        template = 'derived/past_brevet.html'
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
            rider_email = h.email2words(rider.email)
        except (TypeError, model.BrevetRider.DoesNotExist, AttributeError):
            rider = rider_email = None
        template = 'derived/brevet.html'
        context = RequestContext(request, {
            'brevet': brevet,
            'region': dict(abbrev=region, long_name=model.REGIONS[region]),
            'registration_closed': brevet.registration_closed,
            'brevet_started': _brevet_started(brevet),
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
    if _registration_closed(brevet):
        raise Http404
    form_class = (model.RiderForm if brevet.info_question
                  else model.RiderFormWithoutQualification)
    if request.method == 'POST':
        # Process submitted form data
        rider = form_class(
            request.POST, instance=model.Rider(brevet=brevet))
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
    context = RequestContext(request, {
        'brevet': brevet,
        'region_name': model.REGIONS[region],
        'form': form,
        'captcha_question': settings.REGISTRATION_FORM_CAPTCHA_QUESTION
    })
    response = render_to_response('derived/registration_form.html', context)
    return response


def brevet_rider_emails(request, region, event, date):
    """
    """
    rider_list = model.Rider.objects.filter(
        brevet__region=region, brevet__event=event,
        brevet__date=datetime.strptime(date, '%d%b%Y').date())
    if not rider_list:
        raise Http404
    email_list = ', '.join(rider.email for rider in rider_list)
    return HttpResponse(email_list, mimetype='text/plain')


def _process_registration(brevet, rider, request):
    """Process rider pre-registration for brevet.
    """
    brevet_page = 'register/{0.region}{0.event}/{1}'.format(
        brevet, brevet.date.strftime('%d%b%Y'))
    # Check for duplicate registration
    try:
        check_rider = model.Rider.objects.get(
            name=rider.name, email=rider.email, brevet=brevet)
        # Redirect to brevet page with duplicate flag to
        # trigger appropriate flash message
        return '/{0}/{1:d}/duplicate/'.format(brevet_page, check_rider.id)
    except model.Rider.DoesNotExist:
        # Save new rider pre-registration and send emails to
        # rider and brevet organizer
        rider.save()
        host = request.get_host()
        _email_to_rider(brevet, rider, host)
        _email_to_organizer(brevet, rider, host)
        # Redirect to brevet page with rider record id to
        # trigger registration confirmation flash message
        return '/{0}/{1:d}/'.format(brevet_page, rider.id)


def _email_to_rider(brevet, rider, host):
    """Send pre-registration confirmation email to rider.
    """
    brevet_page = 'register/{0.region}{0.event}/{1}'.format(
        brevet, brevet.date.strftime('%d%b%Y'))
    brevet_page_uri = 'http://{0}/{1}/'.format(host, brevet_page)
    email = mail.EmailMessage(
        subject='Pre-registration Confirmation for {0} Brevet'
                .format(brevet),
        body=render_to_string(
            'email/to_rider.txt',
            {'brevet': brevet,
             'rider': rider,
             'brevet_page_uri': brevet_page_uri}),
        from_email=brevet.organizer_email,
        to=[rider.email],
        headers={
            'Sender': settings.REGISTRATION_EMAIL_FROM,
            'Reply-To': brevet.organizer_email})
    email.send()


def _email_to_organizer(brevet, rider, host):
    """Send rider pre-registration notification email to event organizer(s).
    """
    brevet_page = 'register/{0.region}{0.event}/{1}'.format(
        brevet, brevet.date.strftime('%d%b%Y'))
    brevet_page_uri = 'http://{0}/{1}/'.format(host, brevet_page)
    email = mail.EmailMessage(
    subject='{0} has Pre-registered for the {1}'
            .format(rider.name, brevet),
    body=render_to_string(
        'email/to_organizer.txt',
        {'brevet': brevet,
         'rider': rider,
         'brevet_page_uri': brevet_page_uri,
         'admin_email': settings.ADMINS[0][1]}),
    from_email=settings.REGISTRATION_EMAIL_FROM,
    to=[addr.strip() for addr in brevet.organizer_email.split(',')])
    email.send()
