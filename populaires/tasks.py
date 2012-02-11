"""Asynchronous tasks for RandoPony populaires app.
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
from .models import Populaire
from .models import Rider
from ..pasture.helpers import google_docs_login
from ..pasture.models import EmailAddress


@task(ignore_result=True)
def update_google_spreadsheet(populaire_pk):
    """Update the rider list spreadsheet on Google docs, preserving
    the list's sorted by last name order.
    """
    populaire = Populaire.objects.get(pk=populaire_pk)
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


@task(ignore_result=True)
def email_to_rider(populaire_pk, rider_pk, host):
    """Send pre-registration confirmation email to rider.
    """
    populaire = Populaire.objects.get(pk=populaire_pk)
    rider = Rider.objects.get(pk=rider_pk)
    pop_page = reverse(
        'populaires:populaire',
        args=(populaire.short_name, populaire.date.strftime('%d%b%Y')))
    pop_page_url = 'http://{0}{1}'.format(host, pop_page)
    from_randopony = EmailAddress.objects.get(key='from_randopony').email
    email = mail.EmailMessage(
        subject='Pre-registration Confirmation for {0}'.format(populaire),
        body=render_to_string(
            'populaires/email/to_rider.txt',
            {'populaire': populaire,
             'pop_page_url': pop_page_url}),
        from_email=from_randopony,
        to=[rider.email],
        headers={
            'Sender': from_randopony,
            'Reply-To': populaire.organizer_email}
    )
    email.send()


@task(ignore_result=True)
def email_to_organizer(populaire_pk, rider_pk, host):
    """Send rider pre-registration notification email to event organizer(s).
    """
    populaire = Populaire.objects.get(pk=populaire_pk)
    rider = Rider.objects.get(pk=rider_pk)
    pop_page = reverse(
        'populaires:populaire',
        args=(populaire.short_name, populaire.date.strftime('%d%b%Y')))
    pop_page_url = 'http://{0}{1}'.format(host, pop_page)
    rider_list_url = (
        'https://spreadsheets.google.com/ccc?key={0}'
        .format(populaire.google_doc_id.split(':')[1]))
    from_randopony = EmailAddress.objects.get(key='from_randopony').email
    email = mail.EmailMessage(
        subject='{0} has Pre-registered for the {1}'
                .format(rider.full_name, populaire),
        body=render_to_string(
            'populaires/email/to_organizer.txt',
            {'populaire': populaire,
             'rider': rider,
             'pop_page_url': pop_page_url,
             'rider_list_url': rider_list_url,
             'admin_email': settings.ADMINS[0][1]}),
        from_email=from_randopony,
        to=[addr.strip() for addr in populaire.organizer_email.split(',')]
    )
    email.send()
