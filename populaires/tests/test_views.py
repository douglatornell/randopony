"""View tests for RandoPony populaires app.

"""
from __future__ import absolute_import
# Standard library:
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
            mock_datetime.now.return_value = datetime(2010, 12, 26, 12, 35)
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
            mock_datetime.today.return_value = datetime(2011, 12, 27)
            mock_datetime.now.return_value = datetime(2011, 12, 27, 14, 4)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, '2 Pre-registered Riders')
