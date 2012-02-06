"""Asynchronous tasks for RandoPony register app.
"""
# Celery:
from celery.task import task
# Django:
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
# Google Docs:
from gdata.spreadsheet.service import SpreadsheetsService
# RandoPony:
from .models import Brevet
from .models import BrevetRider
from ..pasture.helpers import google_docs_login
from ..pasture.models import EmailAddress
from ..pasture.models import Link


@task(ignore_result=True)
def update_google_spreadsheet(brevet_pk):
    """Update the rider list spreadsheet on Google docs, preserving
    the list's sorted by last name order.
    """
    brevet = Brevet.objects.get(pk=brevet_pk)
    client = google_docs_login(SpreadsheetsService)
    key = brevet.google_doc_id.split(':')[1]
    spreadsheet_list = client.GetListFeed(key)
    spreadsheet_rows = len(spreadsheet_list.entry)
    rider_list = BrevetRider.objects.filter(
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


@task(ignore_result=True)
def email_to_rider(brevet_pk, rider_pk, host):
    """Send pre-registration confirmation email to rider.
    """
    brevet = Brevet.objects.get(pk=brevet_pk)
    rider = BrevetRider.objects.get(pk=rider_pk)
    brevet_page = reverse(
        'register:brevet',
        args=(brevet.region, brevet.event, brevet.date.strftime('%d%b%Y')))
    brevet_page_url = 'http://{0}{1}'.format(host, brevet_page)
    event_waiver_url = Link.objects.get(key='event_waiver_url').url
    membership_form_url = Link.objects.get(key='membership_form_url').url
    from_randopony = EmailAddress.objects.get(key='from_randopony').email
    email = mail.EmailMessage(
        subject='Pre-registration Confirmation for {0} Brevet'
                .format(brevet),
        body=render_to_string(
            'register/email/to_rider.txt',
            {'brevet': brevet,
             'rider': rider,
             'brevet_page_url': brevet_page_url,
             'event_waiver_url': event_waiver_url,
             'membership_form_url': membership_form_url,
             }),
        from_email=brevet.organizer_email,
        to=[rider.email],
        headers={
            'Sender': from_randopony,
            'Reply-To': brevet.organizer_email}
    )
    email.send()


@task(ignore_result=True)
def email_to_organizer(brevet_pk, rider_pk, host):
    """Send rider pre-registration notification email to event organizer(s).
    """
    brevet = Brevet.objects.get(pk=brevet_pk)
    rider = BrevetRider.objects.get(pk=rider_pk)
    brevet_page = reverse(
        'register:brevet',
        args=(brevet.region, brevet.event, brevet.date.strftime('%d%b%Y')))
    brevet_page_url = 'http://{0}{1}'.format(host, brevet_page)
    from_randopony = EmailAddress.objects.get(key='from_randopony').email
    email = mail.EmailMessage(
        subject='{0} has Pre-registered for the {1}'
                .format(rider.full_name, brevet),
        body=render_to_string(
            'register/email/to_organizer.txt',
            {'brevet': brevet,
             'rider': rider,
             'brevet_page_url': brevet_page_url,
             'admin_email': settings.ADMINS[0][1]}),
        from_email=from_randopony,
        to=[addr.strip() for addr in brevet.organizer_email.split(',')]
    )
    email.send()
