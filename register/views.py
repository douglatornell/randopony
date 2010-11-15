"""View functions for RandoPony site register app.

"""
# Standard library:
from datetime import datetime, time, timedelta
# Django:
from django.conf import settings
from django.core import mail
from django.http import Http404
from django.shortcuts import render_to_response, redirect
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
    context = {
        'regions': region_list,
        'admin_email': h.email2words(settings.ADMINS[0][1])
    }
    return render_to_response(
        'derived/home/home.html',
        context, context_instance=RequestContext(request))


def region_brevets(request, region):
    """Display a region image and the list of brevets in the sidebar.
    """
    seven_days_ago = datetime.today().date() - timedelta(days=7)
    brevet_list = model.Brevet.objects.filter(
            region=region
        ).exclude(
            date__lt=(seven_days_ago)
        )
    context = {
        'region': {
            'abbrev': region,
            'long_name': model.REGIONS[region]
        },
        'brevets': brevet_list
    }
    return render_to_response(
        'derived/region_brevets/region_brevets.html',
        context, context_instance=RequestContext(request))


def _registration_closed(brevet_date):
    """ Registration for brevets closes at noon on the day before the
    event. Note that the webfaction server hosting randopony is 2
    hours ahead of Pacific time.
    """
    one_day = timedelta(days=1)
    server_tz_offset = 2
    noon = time(12 + server_tz_offset, 0)
    registration_closed = (
        datetime.now() >= datetime.combine(brevet_date - one_day, noon))
    return registration_closed


def brevet(request, region, event, date, rider_id=None):
    """Display the brevet information, pre-registered riders list, and
    sometimes the registration confirmation, or duplicate registration
    flash message.
    """
    brevet_date = datetime.strptime(date, '%d%b%Y').date()
    try:
        brevet = model.Brevet.objects.get(
            region=region, event=event, date=brevet_date)
    except model.Brevet.DoesNotExist:
        raise Http404
    # Display a page with a link to the year's results on the club
    # site for brevets more than 7 days in the past
    if brevet_date < datetime.today().date() - timedelta(days=7):
        date = '%s-%s-%s' % (date[:2], date[2:5], date[-4:])
        year_digits = date[-2:]
        results_url = (
            'http://randonneurs.bc.ca/results/%(year_digits)s_times/'
            '%(year_digits)s_times.html' % vars())
        return render_to_response(
            'derived/home/past_brevet.html',
            {'brevet': '%(region)s%(event)s %(date)s' % vars(),
             'results_url': results_url},
            context_instance=RequestContext(request))
    # Suppress the registration closed message 1 hour after the brevet
    # starts. Note that the webfaction server hosting randopony is 2
    # hours ahead of Pacific time.
    brevet_started = False
    if (datetime.now() >= datetime.combine(
            brevet_date, brevet.start_time) + timedelta(hours=3)):
        brevet_started = True
    # Get the rider instance to use for the confirmation message, if
    # applicable
    if rider_id is not None:
        rider = model.Rider.objects.get(pk=int(rider_id))
    else:
        rider = None
    rider_email = None if not rider else h.email2words(rider.email)
    duplicate_registration = (True if request.path.endswith('duplicate/')
                              else False)
    # Get the list of pre-registered riders
    rider_list = model.Rider.objects.filter(
        brevet__region=region, brevet__event=event,
        brevet__date=brevet_date)
    show_filler_photo = True if len(rider_list) < 15 else False
    return render_to_response(
        'derived/brevet/brevet.html',
        {'brevet': brevet, 'rider': rider, 'rider_list': rider_list,
         'region': dict(abbrev=region, long_name=model.REGIONS[region]),
         'rider_email': rider_email,
         'show_filler_photo': show_filler_photo,
         'duplicate_registration': duplicate_registration,
         'registration_closed': _registration_closed(brevet_date),
         'brevet_started': brevet_started},
        context_instance=RequestContext(request))


def registration_form(request, region, event, date):
    """Brevet registration form page.
    """
    brevet_date = datetime.strptime(date, '%d%b%Y').date()
    if _registration_closed(brevet_date):
        raise Http404
    try:
        brevet = model.Brevet.objects.get(
            region=region, event=event, date=brevet_date)
    except model.Brevet.DoesNotExist:
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
    context = {
        'brevet': brevet,
        'region_name': model.REGIONS[region],
        'form': form,
        'captcha_question': settings.REGISTRATION_FORM_CAPTCHA_QUESTION
    }
    response = render_to_response(
        'derived/register/registration_form.html',
        context, context_instance=RequestContext(request))
    return response


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


def about_pony(request):
    """About the randopony page.
    """
    return render_to_response(
        'derived/about/about-pony.html',
        context_instance=RequestContext(request))


def organizer_info(request):
    """Info page for brevet organizers about how to get their brevet
    listed on the randopony site.
    """
    admin_email = h.email2words(settings.ADMINS[0][1])
    return render_to_response(
        'derived/organizer-info/organizer-info.html',
        {'admin_email': admin_email},
        context_instance=RequestContext(request))
