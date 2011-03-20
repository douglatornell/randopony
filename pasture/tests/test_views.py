"""View tests for RandoPony pasture app.

"""
# Django:
import django.test
from django.core.urlresolvers import reverse


class TestHomeView(django.test.TestCase):
    """Functional tests for home view.
    """
    def test_home_get(self):
        """GET request for root page of pasture app works
        """
        response = self.client.get(reverse('pasture:home'))
        self.assertContains(response, 'RandoPony')


    def test_home_context(self):
        """home view has correct context
        """
        response = self.client.get(reverse('pasture:home'))
        self.assertTrue(response.context['admin_email'])


    def test_home_base_sidebar(self):
        """home view renders standard sidebar links
        """
        response = self.client.get(reverse('pasture:home'))
        self.assertContains(response, 'Home')
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'Info for Event Organizers')
        self.assertContains(response, "What's up with the pony?")

        
class TestAboutPonyView(django.test.TestCase):
    """Functional tests for about RandoPony view.
    """
    def test_about_pony_get(self):
        """GET request for about RandoPony page works
        """
        response = self.client.get(reverse('pasture:about-pony'))
        self.assertEqual(response.status_code, 200)


    def test_about_pony_sidebar(self):
        """organizer_info view renders expected sidebar
        """
        response = self.client.get(reverse('pasture:about-pony'))
        self.assertTrue('Home' in response.content)
        self.assertTrue('randonneurs.bc.ca' in response.content)
        self.assertTrue('Info for Event Organizers' in response.content)
        self.assertTrue("What's up with the pony?" in response.content)


class TestOrganizerInfoView(django.test.TestCase):
    """Functional tests for info for event organizer's view.
    """
    def test_organizer_info_get(self):
        """GET request for orgainzers info page works
        """
        response = self.client.get(reverse('pasture:organizer-info'))
        self.assertEqual(response.status_code, 200)


    def test_organizer_info_sidebar(self):
        """organizer_info view renders expected sidebar
        """
        response = self.client.get(reverse('pasture:organizer-info'))
        self.assertTrue('Home' in response.content)
        self.assertTrue('randonneurs.bc.ca' in response.content)
        self.assertTrue('Info for Event Organizers' in response.content)
        self.assertTrue("What's up with the pony?" in response.content)
