"""View functions for RandoPony site register app.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-05
"""
# Standard library:
from datetime import datetime
# Django:
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
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
    sometimes the registration confirmation flash message.
    """
    # Get the brevet instance to render
    brevet_date = datetime.strptime(date, '%d%b%Y').date()
    brevet = model.Brevet.objects.get(
        region=region, distance=distance, date=brevet_date)
    # Get the rider instance to use for the confirmation message, if
    # applicable
    if rider_id is not None:
        try:
            rider = model.Rider.objects.get(pk=int(rider_id))
        except:
            raise
    else:
        rider = None
    rider_email = None if not rider else h.email2words(rider.email)
    # Get the list of pre-registered riders
    rider_list = model.Rider.objects.filter(
        brevet__region=region, brevet__distance=distance,
        brevet__date=brevet_date)
    return render_to_response(
        'derived/brevet/brevet.html',
        {'brevet': brevet, 'rider': rider, 'rider_list': rider_list,
         'rider_email': rider_email},
        context_instance=RequestContext(request))


def registration_form(request, region, distance, date):
    """Brevet registration form page.
    """
    # Get the brevet instance that the rider is registering for
    brevet_date = datetime.strptime(date, '%d%b%Y').date()
    brevet = model.Brevet.objects.get(region=region, distance=distance,
                                date=brevet_date)
    # Get the CAPTCHA questions from the settings
    captcha_question = settings.REGISTRATION_FORM_CAPTCHA_QUESTION
    # Choose the appropriate registration form class
    if brevet.qual_info_reqd:
        form_class = model.RiderForm
    else:
        form_class = model.RiderFormWithoutQualification
    if request.method == 'POST':
        # Process submitted form data
        try:
            rider = model.Rider(brevet=brevet)
            rider = form_class(request.POST, instance=rider)
            rider = rider.save()
            return redirect(
                '/register/%(region)s%(distance)s/%(date)s/%(rider_id)d/'
                % {'region': region, 'distance': distance, 'date': date,
                   'rider_id': rider.id})
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
    return render_to_response(
        'derived/organizer-info/organizer-info.html',
        context_instance=RequestContext(request))
