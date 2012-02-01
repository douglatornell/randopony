"""Functional tests for customized admin elements of RandoPony
register app.
"""
from __future__ import absolute_import
# Standard library:
from datetime import date
from datetime import time
from datetime import timedelta
# Django:
import django.test
from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail


class TestAdminBrevet(django.test.TestCase):
    """Functional tests for the add/change brevet admin form.
    """
    fixtures = ['brevets.yaml', 'email_addresses.yaml']

    def setUp(self):
        user = User.objects.create_superuser(
            'test_admin', 'test_admin@example.com', 'foobar42')
        user.save()
        self.client.login(username='test_admin', password='foobar42')


    def test_brevet_add_form_get(self):
        """GET request for add brevet form page works
        """
        response = self.client.get('/admin/register/brevet/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add brevet')


    def test_brevet_add_form(self):
        """Submission of brevet form adds brevet to database
        """
        from ..models import Brevet
        brevet_date = date.today() + timedelta(days=10)
        post_data = {
            'region': 'VI',
            'event': '600',
            'date': brevet_date,
            'route_name': 'Next Chance',
            'location': "Tim Horton's, Victoria",
            'time': time(5, 0),
            'organizer_email': 'mcroy@example.com',
        }
        response = self.client.post(
            '/admin/register/brevet/add/', post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select brevet to change')
        brevet = Brevet.objects.get(
            region='VI', event=600, date=brevet_date)
        for key, value in post_data.iteritems():
            self.assertEqual(brevet.__getattribute__(key), value)


    def test_brevet_add_2_org_email_no_space(self):
        """Comma separated organizer email addresses validate correctly
        """
        from ..models import Brevet
        brevet_date = date.today() + timedelta(days=10)
        post_data = {
            'region': 'VI',
            'event': '600',
            'date': brevet_date,
            'route_name': 'Next Chance',
            'location': "Tim Horton's, Victoria",
            'time': time(5, 0),
            'organizer_email': 'mcroy@example.com,dug.andrusiek@example.com'
        }
        self.client.post('/admin/register/brevet/add/', post_data)
        brevet = Brevet.objects.get(
            region='VI', event=600, date=brevet_date)
        self.assertEqual(
            brevet.organizer_email,
            'mcroy@example.com,dug.andrusiek@example.com')


    def test_brevet_add_2_org_email_with_space(self):
        """Comma-space separated organizer email addresses validate correctly
        """
        from ..models import Brevet
        brevet_date = date.today() + timedelta(days=10)
        post_data = {
            'region': 'VI',
            'event': '600',
            'date': brevet_date,
            'route_name': 'Next Chance',
            'location': "Tim Horton's, Victoria",
            'time': time(5, 0),
            'organizer_email': 'mcroy@example.com, dug.andrusiek@example.com'
        }
        self.client.post('/admin/register/brevet/add/', post_data)
        brevet = Brevet.objects.get(
            region='VI', event=600, date=brevet_date)
        self.assertEqual(
            brevet.organizer_email,
            'mcroy@example.com, dug.andrusiek@example.com')


    def test_brevet_notify_webmaster_1_brevet(self):
        """notify webmaster admin action sends email for 1 brevet
        """
        params = {
            u'action': [u'notify_webmaster'],
            u'_selected_action': [u'1'],
        }
        response = self.client.post(
            '/admin/register/brevet/', params, follow=True)
        self.assertContains(response, 'URL for 1 brevet sent to webmaster')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'RandoPony Pre-registration Page for LM300 01-May-2010')
        self.assertEqual(mail.outbox[0].to, ['webmaster@example.com'])
        self.assertEqual(
            mail.outbox[0].from_email, 'randopony@randonneurs.bc.ca')
        body = mail.outbox[0].body
        self.assertTrue(
            'pre-registration page for the LM300 01-May-2010 event' in body)
        self.assertTrue(
            'The URL is http://testserver/register/LM300/01May2010/' in body)
        self.assertTrue(
            'please send email to {0}'.format(settings.ADMINS[0][1])
            in body)


    def test_brevet_notify_webmaster_2_brevets(self):
        """notify webmaster admin action sends email for 2 brevets
        """
        params = {
            u'action': [u'notify_webmaster'],
            u'_selected_action': [u'1', u'2'],
        }
        response = self.client.post(
            '/admin/register/brevet/', params, follow=True)
        self.assertContains(response, 'URLs for 2 brevets sent to webmaster')
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].subject,
            'RandoPony Pre-registration Page for LM300 01-May-2010')
        self.assertEqual(
            mail.outbox[1].subject,
            'RandoPony Pre-registration Page for LM400 22-May-2010')


    def test_brevet_notify_brevet_organizer_1_brevet(self):
        """notify brevet organizer(s) admin action sends email for 1 brevet
        """
        params = {
            u'action': [u'notify_brevet_organizer'],
            u'_selected_action': [u'1'],
        }
        response = self.client.post(
            '/admin/register/brevet/', params, follow=True)
        self.assertContains(response, 'Email for 1 brevet sent to organizer(s)')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'RandoPony URLs for LM300 01-May-2010')
        self.assertEqual(mail.outbox[0].to, ['pumpkinrider@example.com'])
        self.assertEqual(
            mail.outbox[0].from_email, 'randopony@randonneurs.bc.ca')
        body = mail.outbox[0].body
        self.assertIn(
            'pre-registration page for the LM300 01-May-2010 brevet', body)
        self.assertIn(
            'The URL is <http://testserver/register/LM300/01May2010/>', body)
        self.assertIn(
            'The rider list URL is <https://spreadsheets.google.com/ccc?key=foo>',
            body)
        self.assertIn(
            'The riders email address list URL is '
            '<http://testserver/register/LM300/01May2010/rider-emails/'
            'dc554a2d-50ce-5c67-ba40-aa541ab3bf2d/>',
            body)
        self.assertTrue(
            'please send email to {0}'.format(settings.ADMINS[0][1])
            in body)


class TestAdminClubEvent(django.test.TestCase):
    """Functional tests for the add/change brevet admin form.
    """
    fixtures = ['club_events.yaml', 'email_addresses.yaml']

    def setUp(self):
        user = User.objects.create_superuser(
            'test_admin', 'test_admin@example.com', 'foobar42')
        user.save()
        self.client.login(username='test_admin', password='foobar42')


    def test_club_event_add_form_get(self):
        """GET request for add brevet form page works
        """
        response = self.client.get('/admin/register/clubevent/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add club event')


    def test_club_event_add_form(self):
        """Submission of club event form adds club event to database
        """
        from ..models import ClubEvent
        event_date = date.today() + timedelta(days=10)
        post_data = {
            'region': 'Club',
            'event': 'dinner',
            'date': event_date,
            'location': "Tim Horton's, Victoria",
            'time': time(18, 0),
            'organizer_email': 'mcroy@example.com',
        }
        response = self.client.post(
            '/admin/register/clubevent/add/', post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select club event to change')
        event = ClubEvent.objects.get(
            region='Club', event='dinner', date=event_date)
        for key, value in post_data.iteritems():
            self.assertEqual(event.__getattribute__(key), value)


    def test_club_event_add_2_org_email_no_space(self):
        """Comma separated organizer email addresses validate correctly
        """
        from ..models import ClubEvent
        event_date = date.today() + timedelta(days=10)
        post_data = {
            'region': 'Club',
            'event': 'dinner',
            'date': event_date,
            'location': "Tim Horton's, Victoria",
            'time': time(18, 0),
            'organizer_email': 'mcroy@example.com,dug.andrusiek@example.com'
        }
        self.client.post('/admin/register/clubevent/add/', post_data)
        event = ClubEvent.objects.get(
            region='Club', event='dinner', date=event_date)
        self.assertEqual(
            event.organizer_email,
            'mcroy@example.com,dug.andrusiek@example.com')


    def test_club_event_add_2_org_email_with_space(self):
        """Comma-space separated organizer email addresses validate correctly
        """
        from ..models import ClubEvent
        event_date = date.today() + timedelta(days=10)
        post_data = {
            'region': 'Club',
            'event': 'dinner',
            'date': event_date,
            'location': "Tim Horton's, Victoria",
            'time': time(18, 0),
            'organizer_email': 'mcroy@example.com, dug.andrusiek@example.com'
        }
        self.client.post('/admin/register/clubevent/add/', post_data)
        event = ClubEvent.objects.get(
            region='Club', event='dinner', date=event_date)
        self.assertEqual(
            event.organizer_email,
            'mcroy@example.com, dug.andrusiek@example.com')


    def test_club_event_notify_webmaster_1_event(self):
        """notify webmaster admin action sends email for 1 club event
        """
        params = {
            u'action': [u'notify_webmaster'],
            u'_selected_action': [u'1'],
        }
        response = self.client.post(
            '/admin/register/clubevent/', params, follow=True)
        self.assertContains(response, 'URL for 1 event sent to webmaster')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'RandoPony Pre-registration Page for Dinner 16-Mar-2010')
        self.assertEqual(mail.outbox[0].to, ['webmaster@example.com'])
        self.assertEqual(
            mail.outbox[0].from_email, 'randopony@randonneurs.bc.ca')
        body = mail.outbox[0].body
        self.assertTrue(
            'pre-registration page for the Dinner 16-Mar-2010 event' in body)
        self.assertTrue(
            'The URL is http://testserver/register/ClubDinner/16Mar2010/'
            in body)
        self.assertTrue(
            'please send email to {0}'.format(settings.ADMINS[0][1])
            in body)


    def test_club_event_notify_webmaster_2_events(self):
        """notify webmaster admin action sends email for 2 club events
        """
        params = {
            u'action': [u'notify_webmaster'],
            u'_selected_action': [u'1', u'2'],
        }
        response = self.client.post(
            '/admin/register/clubevent/', params, follow=True)
        self.assertContains(response, 'URLs for 2 events sent to webmaster')
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].subject,
            'RandoPony Pre-registration Page for Dinner 16-Mar-2010')
        self.assertEqual(
            mail.outbox[1].subject,
            'RandoPony Pre-registration Page for AGM 03-Oct-2010')
