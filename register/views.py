"""View functions for RandoPony site register app.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-05
"""
# Standard library:
from datetime import datetime
# Django:
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
# Application:
import randopony.register.helpers as h
import randopony.register.models as model


def home(request):
    """Display the welcome information and list of brevets.
    """
    brevet_list = model.Brevet.objects.all()
    admin_email = h.email2words(settings.ADMINS[0][1])
    return render_to_response(
        'derived/home/home.html',
        {'brevets': brevet_list, 'admin_email': admin_email},
        context_instance=RequestContext(request))


def brevet(request, region, distance, date, rider_id=None):
    """Display the brevet information, pre-registered riders list, and
    sometimes the registration confirmation, or duplicate registration
    flash message.
    """
    # Get the brevet instance to render
    brevet_date = datetime.strptime(date, '%d%b%Y').date()
    brevet = model.Brevet.objects.get(
        region=region, distance=distance, date=brevet_date)
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
        brevet__region=region, brevet__distance=distance,
        brevet__date=brevet_date)
    return render_to_response(
        'derived/brevet/brevet.html',
        {'brevet': brevet, 'rider': rider, 'rider_list': rider_list,
         'rider_email': rider_email,
         'duplicate_registration': duplicate_registration},
        context_instance=RequestContext(request))


def registration_form(request, region, distance, date):
    """Brevet registration form page.
    """
    # Get the brevet instance that the rider is registering for
    brevet_date = datetime.strptime(date, '%d%b%Y').date()
    brevet = model.Brevet.objects.get(region=region, distance=distance,
                                date=brevet_date)
    # Get the CAPTCHA question from the settings
    captcha_question = settings.REGISTRATION_FORM_CAPTCHA_QUESTION
    # Choose the appropriate registration form class
    if brevet.qual_info_question:
        form_class = model.RiderForm
    else:
        form_class = model.RiderFormWithoutQualification
    if request.method == 'POST':
        # Process submitted form data
        try:
            rider = model.Rider(brevet=brevet)
            rider = form_class(request.POST, instance=rider)
            new_rider = rider.save(commit=False)
            # Check for duplicate registration
            try:
                check_rider = model.Rider.objects.get(
                    name=new_rider.name, email=new_rider.email, brevet=brevet)
                # Redirect to brevet page with duplicate flag to
                # trigger appropriate flash message
                return redirect(
                    '/register/%(region)s%(distance)s/%(date)s/'
                    '%(rider_id)d/duplicate/'
                    % {'region': region, 'distance': distance, 'date': date,
                       'rider_id': check_rider.id})
            except model.Rider.DoesNotExist:
                # Save new rider pre-registration and send emails to
                # rider and brevet organizer
                new_rider.save()
                brevet_page_uri = '/'.join(
                    ('http:/',
                     request.META['HTTP_HOST'],
                     'register/%(region)s%(distance)s/%(date)s/' % vars()))
                mail.send_mail(
                    'Pre-registration Confirmation for %(brevet)s Brevet'
                    % vars(),
                    render_to_string(
                        'email/to_rider.txt',
                        {'brevet': brevet, 'rider': new_rider,
                         'brevet_page_uri': brevet_page_uri}),
                    brevet.organizer_email,
                    [new_rider.email])
                mail.send_mail(
                    '%(name)s has Pre-registered for the %(brevet)s'
                    % dict(name=new_rider.name, brevet=brevet),
                    render_to_string(
                        'email/to_organizer.txt',
                        {'brevet': brevet, 'rider': new_rider,
                         'brevet_page_uri': brevet_page_uri,
                         'admin_email': settings.ADMINS[0][1]}),
                    settings.REGISTRATION_EMAIL_FROM,
                    [brevet.organizer_email])
                # Redirect to brevet page with rider record id to
                # trigger registartion confirmation flash message
                return redirect(
                    '/register/%(region)s%(distance)s/%(date)s/%(rider_id)d/'
                    % {'region': region, 'distance': distance, 'date': date,
                       'rider_id': new_rider.id})
        except ValueError:
            # Validation error, so re-render form with rider inputs
            # and error messages
            form = rider
    else:
        # Unbound form to render entry form
        form = form_class()
    return render_to_response(
        'derived/register/registration_form.html',
        {'brevet': brevet, 'form': form, 'captcha_question': captcha_question},
        context_instance=RequestContext(request))


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
