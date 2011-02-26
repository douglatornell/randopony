"""View tests for RandoPony populaires app.

"""
from __future__ import absolute_import
# Standard library:
from datetime import datetime
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
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'Info for Event Organizers')
        self.assertContains(response, "What's up with the pony?")


    def test_populaires_list_events_list(self):
        """populaires-list view renders list of events
        """
        with patch('randopony.populaires.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 2, 26)
            response = self.client.get(reverse('populaires:populaires-list'))
        self.assertContains(response, 'VicPop 27-Mar-2011')


    def test_populaires_list_excludes_past_events(self):
        """populaires-list view excludes past events
        """
        with patch('randopony.populaires.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 2, 26)
            response = self.client.get(reverse('populaires:populaires-list'))
        self.assertContains(response, 'VicPop 27-Mar-2011')
        self.assertNotContains(response, 'NewYearsPop 01-Jan-2011')
