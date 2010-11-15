"""Funcitonal tests for customized admin elements of RandoPony
register app.

"""
# Standard library:
from datetime import date, time, timedelta
# Django:
import django.test
from django.contrib.auth.models import User
# Application:
import randopony.register.models as models


class TestAdminBrevet(django.test.TestCase):
    """Functional tests for the add/change brevet admin form.
    """
    def setUp(self):
        user = User.objects.create_superuser(
            'test_admin', 'test_admin@example.com', 'foobar42')
        user.save()
        response = self.client.login(username='test_admin', password='foobar42')

        
    def test_brevet_add_form_get(self):
        """GET request for add brevet form page works
        """
        response = self.client.get('/admin/register/brevet/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add brevet')


    def test_brevet_add_form(self):
        """Submission of brevet form adds brevet to database
        """
        brevet_date = date.today() + timedelta(days=10)
        post_data = {
            'region': 'VI',
            'event': '600',
            'date': brevet_date,
            'route_name': 'Next Chance',
            'start_location': "Tim Horton's, Victoria",
            'start_time': time(5, 0),
            'organizer_email': 'mcroy@example.com',
        }
        response = self.client.post(
            '/admin/register/brevet/add/', post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select brevet to change')
        brevet = models.Brevet.objects.get(
            region='VI', event=600, date=brevet_date)
        for key, value in post_data.iteritems():
            self.assertEqual(brevet.__getattribute__(key), value)


    def test_brevet_add_2_org_email_no_space(self):
        """Comma separated organizer email addresses validate correctly
        """
        brevet_date = date.today() + timedelta(days=10)
        post_data = {
            'region': 'VI',
            'event': '600',
            'date': brevet_date,
            'route_name': 'Next Chance',
            'start_location': "Tim Horton's, Victoria",
            'start_time': time(5, 0),
            'organizer_email': 'mcroy@example.com,dug.andrusiek@example.com'
        }
        self.client.post('/admin/register/brevet/add/', post_data)
        brevet = models.Brevet.objects.get(
            region='VI', event=600, date=brevet_date)
        self.assertEqual(
            brevet.organizer_email,
            'mcroy@example.com,dug.andrusiek@example.com')


    def test_brevet_add_2_org_email_with_space(self):
        """Comma-space separated organizer email addresses validate correctly
        """
        brevet_date = date.today() + timedelta(days=10)
        post_data = {
            'region': 'VI',
            'event': '600',
            'date': brevet_date,
            'route_name': 'Next Chance',
            'start_location': "Tim Horton's, Victoria",
            'start_time': time(5, 0),
            'organizer_email': 'mcroy@example.com, dug.andrusiek@example.com'
        }
        self.client.post('/admin/register/brevet/add/', post_data)
        brevet = models.Brevet.objects.get(
            region='VI', event=600, date=brevet_date)
        self.assertEqual(
            brevet.organizer_email,
            'mcroy@example.com, dug.andrusiek@example.com')
