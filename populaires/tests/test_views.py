"""View tests for RandoPony populaires app.

"""
from __future__ import absolute_import
# Standard library:
from contextlib import nested
from datetime import datetime
from datetime import timedelta
# Mock:
from mock import patch
# Django:
from django.test import TestCase
from django.core.urlresolvers import reverse


class TestPopulairesListView(TestCase):
    """Functional tests for populaires-list view.
    """
    fixtures = ['populaires']
    
    def test_populaires_list_get(self):
        """GET request for populaires-list view works
        """
        response = self.client.get(reverse('populaires:populaires-list'))
        self.assertContains(response, 'RandoPony::Populaires')


    def test_populaires_list_context(self):
        """populaires-list view has correct context
        """
        with patch('randopony.populaires.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 2, 26)
            response = self.client.get(reverse('populaires:populaires-list'))
        self.assertTrue(response.context['events'])
        self.assertTrue(response.context['admin_email'])


    def test_populaires_list_sidebar(self):
        """populaires-list view renders standard sidebar tabs
        """
        response = self.client.get(reverse('populaires:populaires-list'))
        self.assertContains(response, 'Populaires')
        self.assertContains(response, reverse('populaires:populaires-list'))
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'http://randonneurs.bc.ca')
        self.assertContains(response, 'Info for Event Organizers')
        self.assertContains(response, reverse('pasture:organizer-info'))
        self.assertContains(response, "What's up with the pony?")
        self.assertContains(response, reverse('pasture:about-pony'))


    def test_populaires_list_events_list(self):
        """populaires-list view renders list of events
        """
        with patch('randopony.populaires.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 2, 26)
            response = self.client.get(reverse('populaires:populaires-list'))
        self.assertContains(response, 'VicPop 27-Mar-2011')
        self.assertContains(
            response,
            reverse('populaires:populaire', args=('VicPop', '27Mar2011')))


    def test_populaires_list_excludes_past_events(self):
        """populaires-list view excludes past events
        """
        with patch('randopony.populaires.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 2, 26)
            response = self.client.get(reverse('populaires:populaires-list'))
        self.assertContains(response, 'VicPop 27-Mar-2011')
        self.assertNotContains(response, 'NewYearsPop 01-Jan-2011')


class TestPopulaire(TestCase):
    """Functional tests for populaire view.
    """
    fixtures = ['populaires', 'riders']

    def test_populaire_get(self):
        """GET request for populaire page works
        """
        response = self.client.get(
            reverse('populaires:populaire', args=('VicPop', '27Mar2011')))
        self.assertContains(response, 'RandoPony::VicPop 27-Mar-2011')


    def test_populaire_get_nonexistent_event_past(self):
        """GET request for nonexistent populaire in past fails with 404
        """
        response = self.client.get(
            reverse('populaires:populaire', args=('Nanaimo', '23Mar2001')))
        self.assertEqual(response.status_code, 404)


    def test_populaire_get_nonexistent_event_future(self):
        """GET request for nonexistent populaire in future fails with 404
        """
        response = self.client.get(
            reverse('populaires:populaire', args=('CanadaDay', '01Jul2099')))
        self.assertEqual(response.status_code, 404)



    def test_populaire_page_sidebar_w_entry_form(self):
        """populaire view renders correct sidebar for event w/ entry form URL
        """
        url = reverse(
            'populaires:populaire', args=('VicPop', '27Mar2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 2, 26)
            mock_datetime.now.return_value = datetime(2011, 2, 26, 12, 35)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Populaires')
        self.assertContains(response, reverse('populaires:populaires-list'))
        self.assertContains(response, 'VicPop 27-Mar-2011')
        self.assertContains(response, 'Register')
        self.assertContains(
            response, reverse('populaires:form', args=('VicPop', '27Mar2011')))
        self.assertContains(response, 'Entry Form (PDF)')
        self.assertContains(response, url)
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'http://randonneurs.bc.ca')
        self.assertContains(response, 'Info for Event Organizers')
        self.assertContains(response, reverse('pasture:organizer-info'))
        self.assertContains(response, "What's up with the pony?")
        self.assertContains(response, reverse('pasture:about-pony'))


    def test_populaire_page_sidebar_wo_entry_form(self):
        """populaire view renders correct sidebar for event w/o entry form URL
        """
        url = reverse(
            'populaires:populaire', args=('NewYearsPop', '01Jan2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 12, 26)
            mock_datetime.now.return_value = datetime(2010, 12, 26, 12, 35)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Populaires')
        self.assertContains(response, reverse('populaires:populaires-list'))
        self.assertContains(response, 'NewYearsPop 01-Jan-2011')
        self.assertContains(response, url)
        self.assertContains(response, 'Register')
        self.assertContains(
            response,
            reverse('populaires:form', args=('NewYearsPop', '01Jan2011')))
        self.assertNotContains(response, 'Entry Form (PDF)')
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'http://randonneurs.bc.ca')
        self.assertContains(response, 'Info for Event Organizers')
        self.assertContains(response, reverse('pasture:organizer-info'))
        self.assertContains(response, "What's up with the pony?")
        self.assertContains(response, reverse('pasture:about-pony'))


    def test_populaire_page_event_info(self):
        """populaire view renders event info correctly
        """
        url = reverse(
            'populaires:populaire', args=('VicPop', '27Mar2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 2, 26)
            mock_datetime.now.return_value = datetime(2011, 2, 26, 12, 35)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'VicPop 27-Mar-2011', 3)
        self.assertContains(response, 'Victoria Populaire')
        self.assertContains(response, '50 km, 100 km')
        self.assertContains(response, 'Sun 27-Mar-2011 at 10:00')
        self.assertContains(
            response, 'University of Victoria, Parking Lot 2 '
            '(Gabriola Road, near McKinnon Gym)')


    def test_populaire_page_no_riders(self):
        """populaire view has expected message when no riders are registered
        """
        url = reverse(
            'populaires:populaire', args=('VicPop', '27Mar2011'))
        with patch('randopony.populaires.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 2, 26)
            mock_datetime.now.return_value = datetime(2011, 2, 26, 12, 35)
            mock_datetime.strptime = datetime.strptime
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Be the first!')
        self.assertContains(
            response,
            reverse('populaires:form', args=('VicPop', '27Mar2011')), 2)


    def test_populaire_page_1_rider(self):
        """populaire view renders correct page body w/ 1 rider
        """
        url = reverse(
            'populaires:populaire', args=('NewYearsPop', '01Jan2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 12, 26)
            mock_datetime.now.return_value = datetime(2010, 12, 26, 12, 35)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, '1 Pre-registered Rider')
        self.assertContains(response, 'Mike Croy')
        self.assertContains(response, '60 km')
        self.assertNotContains(response, 'registered for this brevet. Cool!')
        self.assertNotContains(response, 'Be the first!')


    def test_populaire_page_2_riders(self):
        """populaires view renders correct page body w/ 2 riders
        """
        url = reverse(
            'populaires:populaire', args=('NanPop', '25Jun2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 3, 5)
            mock_datetime.now.return_value = datetime(2011, 3, 5, 16, 34)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, '2 Pre-registered Riders')


class TestRegistrationFormView(TestCase):
    """Functional tests for registration form view.
    """
    fixtures = ['populaires']

    def test_registration_form_get(self):
        """GET request for registration form page works
        """
        url = reverse(
            'populaires:form', args=('VicPop', '27Mar2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 3, 1)
            mock_datetime.now.return_value = datetime(2011, 3, 1, 18, 43)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)



    def test_registration_form_sidebar_w_entry_form(self):
        """registration form renders correct sidebar for event w/ entry form URL
        """
        url = reverse(
            'populaires:form', args=('VicPop', '27Mar2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 3, 1)
            mock_datetime.now.return_value = datetime(2011, 3, 1, 18, 43)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Populaires')
        self.assertContains(response, reverse('populaires:populaires-list'))
        self.assertContains(response, 'VicPop 27-Mar-2011')
        self.assertContains(response, 'Register')
        self.assertContains(
            response, reverse('populaires:form', args=('VicPop', '27Mar2011')))
        self.assertContains(response, 'Entry Form (PDF)')
        self.assertContains(response, url)
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'http://randonneurs.bc.ca')
        self.assertContains(response, 'Info for Event Organizers')
        self.assertContains(response, reverse('pasture:organizer-info'))
        self.assertContains(response, "What's up with the pony?")
        self.assertContains(response, reverse('pasture:about-pony'))



    def test_registration_form_sidebar_wo_entry_form(self):
        """registartion form sidebar correct for event w/o entry form URL
        """
        url = reverse(
            'populaires:form', args=('NewYearsPop', '01Jan2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 12, 26)
            mock_datetime.now.return_value = datetime(2010, 12, 26, 12, 35)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Populaires')
        self.assertContains(response, reverse('populaires:populaires-list'))
        self.assertContains(response, 'NewYearsPop 01-Jan-2011')
        self.assertContains(response, url)
        self.assertContains(response, 'Register')
        self.assertContains(
            response,
            reverse('populaires:form', args=('NewYearsPop', '01Jan2011')))
        self.assertNotContains(response, 'Entry Form (PDF)')
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'http://randonneurs.bc.ca')
        self.assertContains(response, 'Info for Event Organizers')
        self.assertContains(response, reverse('pasture:organizer-info'))
        self.assertContains(response, "What's up with the pony?")
        self.assertContains(response, reverse('pasture:about-pony'))



    def test_registration_form_body_multi_distance(self):
        """registration form has expected form fields for multi-distance event
        """
        url = reverse(
            'populaires:form', args=('VicPop', '27Mar2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 3, 1)
            mock_datetime.now.return_value = datetime(2011, 3, 1, 18, 43)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'First name:')
        self.assertContains(response, 'Last name:')
        self.assertContains(response, 'Email:')
        self.assertContains(response, 'Distance:')
        self.assertContains(response, '50 km')
        self.assertContains(response, '100 km')


    def test_brevet_registration_form_has_captcha(self):
        """registration form view renders captcha question
        """
        url = reverse(
            'populaires:form', args=('VicPop', '27Mar2011'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 3, 1)
            mock_datetime.now.return_value = datetime(2011, 3, 1, 18, 43)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(
            response, 'Are you a human? Are you a cyclist? Please prove it.')
        self.assertContains(
            response, 'A bicycle has ___ wheels. Fill in the blank:')



class TestRegistrationFunction(TestCase):
    """Functional tests of registration for populaires.
    """
    fixtures = ['populaires']

    def test_registration_form_clean_submit(self):
        """registration form submit w/ valid data redirects to pop pg w/ msg
        """
        from ..models import Rider
        url = reverse(
            'populaires:form', args=('VicPop', '27Mar2011'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'distance': 100,
            'captcha': 2
        }
        context_mgr = nested(
            patch('randopony.populaires.models.datetime'),
            patch('randopony.populaires.views._update_google_spreadsheet'),
        )
        with context_mgr as (mock_datetime, mock_update):
            mock_datetime.today.return_value = datetime(2011, 3, 1)
            mock_datetime.now.return_value = datetime(2011, 3, 1, 18, 43)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        rider_id = Rider.objects.order_by('-id')[0].id
        url = reverse(
            'populaires:prereg-confirm', args=('VicPop', '27Mar2011', rider_id))
        self.assertRedirects(response, url)
        self.assertContains(
            response, 'You have pre-registered for this event. Cool!')
        self.assertContains(response, 'djl@example.com')



class TestRiderEmailsView(TestCase):
    """Functional tests for rider email address list view.
    """
    fixtures = ['populaires', 'riders']

    def test_rider_emails_bad_uuid(self):
        """request for rider's emails with bad event uuid raises 404
        """
        url = reverse(
            'populaires:rider-emails', args=('VicPop', '27Mar2011', 'f00'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_rider_emails_event_past(self):
        """request for rider's emails for event >7 days ago raises 404
        """
        url = reverse(
            'populaires:rider-emails',
            args=('NewYearsPop', '01Jan2011',
                  'ccf79bf6-57bc-5084-94a9-2a6154efef53'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 3, 6)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_no_rider_emails_returns_msg(self):
        """request for rider's emails for event w/ no riders returns msg
        """
        url = reverse(
            'populaires:rider-emails',
            args=('VicPop', '27Mar2011',
                  '2fa8a5ff-d738-59c5-bea4-22fcfa4c9c6e'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 3, 6)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'No riders have registered yet!')


    def test_1_rider_email(self):
        """request for rider's emails for event w/ 1 rider returns address
        """
        url = reverse(
            'populaires:rider-emails',
            args=('NewYearsPop', '01Jan2011',
                  'ccf79bf6-57bc-5084-94a9-2a6154efef53'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 12, 26)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'mcroy@example.com')


    def test_2_rider_emails(self):
        """request for rider's emails for event w/ 2 riders returns list
        """
        url = reverse(
            'populaires:rider-emails',
            args=('NanPop', '25Jun2011',
                  '97b2109c-3281-5263-90fd-c782c17e7cf8'))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 3, 6)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertEqual(
            set(response.content.split(', ')),
            set('lringham@example.com rhesjedal@example.com'.split()))
