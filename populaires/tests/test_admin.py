"""Functional tests for customized admin elements of RandoPony
populaires app.

"""
from __future__ import absolute_import
# Standard library:
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
# Django:
import django.test
from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail


class TestAdminPopulaire(django.test.TestCase):
    """Functional tests for the add/change populaire admin form.
    """
    fixtures = ['populaires']
    
    def setUp(self):
        user = User.objects.create_superuser(
            'test_admin', 'test_admin@example.com', 'foobar42')
        user.save()
        self.client.login(username='test_admin', password='foobar42')

        
    def test_populaire_add_form_get(self):
        """GET request for add populaire form page works
        """
        response = self.client.get('/admin/populaires/populaire/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add populaire')


    def test_populaire_add_form(self):
        """submission of populaire form adds populaire to database
        """
        from ..models import Populaire
        pop_date = date.today() + timedelta(days=10)
        post_data = {
            'event_name': 'Victoria Populaire',
            'short_name': 'VicPop',
            'date': pop_date,
            'location': 'University of Victoria, Parking Lot #2 '
                        '(Gabriola Road, near McKinnon Gym)',
            'time': time(10, 0),
            'organizer_email': 'mjansson@islandnet.com',
            'registration_closes': datetime.combine(pop_date - timedelta(days=4), time(12, 0)),
            'entry_form_url': 'http://www.randonneurs.bc.ca/VicPop/'
                              'VicPop11_registration.pdf',
            'entry_form_url_label': 'Entry Form (PDF)',
        }
        response = self.client.post(
            '/admin/populaires/populaire/add/', post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select populaire to change')
        pop = Populaire.objects.get(short_name='VicPop', date=pop_date)
        for key, value in post_data.iteritems():
            self.assertEqual(pop.__getattribute__(key), value)


    def test_populaire_notify_webmaster(self):
        """notify webmaster admin action sends email
        """
        params = {
            u'action': [u'notify_webmaster'],
            u'_selected_action': [u'1'],
        }
        response = self.client.post(
            '/admin/populaires/populaire/', params, follow=True)
        self.assertContains(response, 'URL for 1 populaire sent to webmaster')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'RandoPony Pre-registration Page for VicPop 27-Mar-2011')
        self.assertEqual(mail.outbox[0].to, [settings.WEBMASTER_EMAIL])
        self.assertEqual(
            mail.outbox[0].from_email, settings.REGISTRATION_EMAIL_FROM)
        body = mail.outbox[0].body
        self.assertTrue(
            'pre-registration page for the VicPop 27-Mar-2011 event' in body)
        self.assertTrue(
            'The URL is http://testserver/populaires/VicPop/27Mar2011/'
            in body)
        self.assertTrue(
            'please send email to {0}'.format(settings.ADMINS[0][1])
            in body)
