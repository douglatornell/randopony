"""View tests for RandoPony register app.
"""
# Standard library:
from datetime import date
from datetime import datetime
from datetime import timedelta
# Mock:
from mock import patch
# Django:
import django.test
from django.core.urlresolvers import reverse


class TestHomeView(django.test.TestCase):
    """Functional tests for home view.
    """
    fixtures = ['brevets.yaml']

    def test_home_get(self):
        """GET request for root page of register app works
        """
        response = self.client.get(reverse('register:home'))
        self.assertContains(response, 'RandoPony::Brevets')

    def test_home_context(self):
        """home view has correct context
        """
        from .. import views
        with patch.object(views, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.get(reverse('register:home'))
        self.assertTrue(response.context['regions'])
        self.assertTrue(response.context['admin_email'])

    def test_home_base_sidebar(self):
        """home view renders standard sidebar tabs
        """
        response = self.client.get(reverse('register:home'))
        self.assertContains(response, 'Brevets')
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'Info for Event Organizers')
        self.assertContains(response, "What's up with the pony?")

    def test_home_regions_list(self):
        """home view renders regions list
        """
        from .. import views
        with patch.object(views, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.get(reverse('register:home'))
        self.assertContains(response, 'Lower Mainland')
        self.assertContains(response, 'Vancouver Island')
        self.assertNotContains(response, 'Southern Interior')
        self.assertNotContains(response, 'Peace Region')
        self.assertNotContains(response, 'Club Events')
        self.assertNotContains(response, 'Super Week')


class TestRegionBrevetsView(django.test.TestCase):
    """Functional tests for region_brevets view.
    """
    fixtures = ['brevets.yaml']

    def test_region_brevets_get(self):
        """GET request for region brevets list page of register app works
        """
        response = self.client.get('/register/LM-events/')
        self.assertContains(response, 'RandoPony::Lower Mainland')

    def test_region_brevets_context(self):
        """region_brevets view has correct context
        """
        from .. import views
        with patch.object(views, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.get('/register/LM-events/')
        self.assertTrue(response.context['region'])
        self.assertTrue(response.context['brevets'])

    def test_region_brevets_list(self):
        """region_brevets view renders brevets list
        """
        from .. import views
        from ..models import Brevet
        with patch.object(views, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.get('/register/LM-events/')
        for brevet in Brevet.objects.filter(region='LM'):
            self.assertContains(response, unicode(brevet))

    def test_region_brevets_list_excludes_past_events(self):
        """region_brevets view excludes past events correctly
        """
        from .. import views
        with patch.object(views, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 27)
            response = self.client.get('/register/LM-events/')
        self.assertContains(response, 'LM400 22-May-2010')
        self.assertNotContains(response, 'LM200 17-Apr-2010')


class TestBrevetView(django.test.TestCase):
    """Functional tests for brevet view.
    """
    fixtures = ['brevets.yaml', 'riders.yaml', 'links.yaml']

    def test_brevet_get(self):
        """GET request for brevet page works
        """
        url = reverse('register:brevet', args=('LM', 300, '01May2010'))
        response = self.client.get(url)
        self.assertContains(response, 'RandoPony::LM300 01-May-2010')

    def test_brevet_get_nonexistent_brevet_past(self):
        """GET request for nonexistent brevet in past fails with 404
        """
        url = reverse('register:brevet', args=('LM', 200, '13Mar2001'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_brevet_get_nonexistent_brevet_future(self):
        """GET request for nonexistent brevet in future fails with 404
        """
        url = reverse('register:brevet', args=('LM', 200, '25Dec2099'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_brevet_page_sidebar(self):
        """brevet view renders correct sidebar
        """
        from .. import models
        url = reverse('register:brevet', args=('LM', 300, '01May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'RandoPony::LM300 01-May-2010')
        self.assertContains(response, 'Register')
        self.assertContains(response, 'Event Entry Form (PDF)')
        self.assertContains(response, 'Club Membership Form (PDF)')

    def test_past_brevet_page(self):
        """page for brevet >7 days ago is pointer to club site
        """
        from .. import models
        url = reverse('register:brevet', args=('LM', 300, '01May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 5, 9)
            mock_datetime.now.return_value = datetime(2010, 5, 9, 19, 21)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(
            response,
            'The LM300 01-May-2010 event is over, and the RandoPony '
            'has moved on!')
        self.assertContains(
            response,
            'http://randonneurs.bc.ca/results/10_times/10_times.html')
        self.assertNotContains(response, 'Be the first!')

    def test_brevet_started_page(self):
        """registration closed message suppressed 1 hour after brevet s
        """
        from .. import models
        url = reverse('register:brevet', args=('LM', 300, '01May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertNotContains(
            response, 'Pre-registration for this event is closed')

    def test_brevet_page_no_riders(self):
        """brevet page has expected msg when no riders are registered
        """
        from .. import models
        url = reverse('register:brevet', args=('LM', 300, '01May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Be the first!')

    def test_brevet_page_1_rider(self):
        """brevet view renders correct page body with 1 registered rider
        """
        from .. import models
        url = reverse('register:brevet', args=('LM', 400, '22May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Manning Park')
        self.assertContains(response, '1 Pre-registered')
        self.assertContains(response, 'Doug Latornell')
        self.assertNotContains(response, 'registered for this brevet. Cool!')
        self.assertNotContains(response, 'Be the first!')

    def test_brevet_page_2_riders(self):
        """brevet view renders correct page body with 2 registered riders
        """
        from .. import models
        url = reverse('register:brevet', args=('LM', 200, '17Apr2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, '2 Pre-registered')

    def test_brevet_page_prereg_confirmation(self):
        """brevet view w/ rider id includes pre-registration confirmation msg
        """
        from .. import models
        url = reverse(
            'register:prereg-confirm', args=('LM', 400, '22May2010', 1))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'for this event. Cool!')

    def test_brevet_page_duplicate_prereg(self):
        """brevet view includes duplicate pre-registration msg when appropos
        """
        from .. import models
        url = reverse(
            'register:prereg-duplicate', args=('LM', 400, '22May2010', 1))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Hmm... Someone using the name')


class TestRegistrationFormView(django.test.TestCase):
    """Functional tests for registration form view.
    """
    fixtures = ['brevets.yaml', 'links.yaml']

    def test_registration_form_get(self):
        """GET request for registration form page works
        """
        from .. import models
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_brevet_registration_form_sidebar(self):
        """registration form view renders correct sidebar
        """
        from .. import models
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'LM400 22-May-2010')
        self.assertContains(response, 'Register')
        self.assertContains(response, 'Event Entry Form (PDF)')
        self.assertContains(response, 'Club Membership Form (PDF)')

    def test_brevet_registration_form_body_with_qual_info(self):
        """registration form view renders page with qual info question
        """
        from .. import models
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Manning Park')
        self.assertContains(response, 'First name:')
        self.assertContains(response, 'Last name:')
        self.assertContains(response, 'Email:')
        self.assertContains(response, 'Club member?')
        self.assertContains(
            response, 'recent 300 km brevet; e.g. LM300 1-May-')
        self.assertContains(response, 'Brevet info:')

    def test_brevet_registration_form_body_wo_qual_info(self):
        """registration form view renders correct page w/o qual info question
        """
        from .. import models
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertNotContains(response, 'Brevet info:')

    def test_brevet_registration_form_has_captcha(self):
        """registration form view renders captcha question
        """
        from .. import models
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(
            response,
            'Are you a human? Are you a randonneur? Please prove it.')
        self.assertContains(
            response, 'A Super Randonneur series consists of brevets of '
            '200 km, 300 km, ___ km, and 600 km. Fill in the blank:')


class TestRegistrationFunction(django.test.TestCase):
    """Functional tests of registration for brevets.
    """
    fixtures = ['brevets.yaml', 'riders.yaml',
                'email_addresses.yaml', 'links.yaml']

    def test_registration_form_clean_submit(self):
        """registration form submit w/ valid data redirects to brevet pg w/ msg
        """
        from .. import models
        from .. import views
        from ..models import BrevetRider
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        datetime_patch = patch.object(models, 'datetime')
        ugs_patch = patch.object(views, 'update_google_spreadsheet')
        with datetime_patch as mock_datetime, ugs_patch:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        rider = BrevetRider.objects.order_by('-id')[0]
        self.assertEqual(rider.lowercase_last_name, 'latornell')
        url = reverse(
            'register:prereg-confirm',
            args=('LM', 300, '01May2010', rider.id))
        self.assertRedirects(response, url)
        self.assertContains(
            response, 'You have pre-registered for this event. Cool!')
        self.assertContains(response, 'djl@example.com')
        self.assertNotContains(
            response, 'You must be a member of the club to ride')

    def test_registration_form_clean_submit_non_member(self):
        """registration from submit redirects to brevet pg w/ non-member msg
        """
        from .. import models
        from .. import views
        from ..models import BrevetRider
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'captcha': 400
        }
        datetime_patch = patch.object(models, 'datetime')
        ugs_patch = patch.object(views, 'update_google_spreadsheet')
        with datetime_patch as mock_datetime, ugs_patch:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        rider_id = BrevetRider.objects.order_by('-id')[0].id
        url = reverse(
            'register:prereg-confirm', args=('LM', 300, '01May2010', rider_id))
        self.assertRedirects(response, url)
        self.assertContains(
            response, 'You have pre-registered for this event. Cool!')
        self.assertContains(response, 'fibber@example.com')
        self.assertContains(
            response, 'You must be a member of the club to ride')

    def test_registration_form_first_name_required(self):
        """registration form first name field must not be empty
        """
        from .. import models
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'captcha': 400
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        self.assertContains(response, 'This field is required.')
        self.assertNotContains(response, 'Hint')

    def test_registration_form_last_name_required(self):
        """registration form last name field must not be empty
        """
        from .. import models
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Fibber',
            'email': 'fibber@example.com',
            'club_member': False,
            'captcha': 400
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        self.assertContains(response, 'This field is required.')
        self.assertNotContains(response, 'Hint')

    def test_registration_form_email_required(self):
        """registration form email field must not be empty
        """
        from .. import models
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'club_member': True,
            'captcha': 400
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params)
        self.assertContains(response, 'This field is required.')
        self.assertNotContains(response, 'Hint')

    def test_registration_form_email_valid(self):
        """registration form email field must be valid
        """
        from .. import models
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'LatMcGeeornell',
            'email': 'fibber',
            'club_member': False,
            'captcha': 400
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params)
        self.assertContains(response, 'Enter a valid e-mail address.')
        self.assertNotContains(response, 'Hint')

    def test_registration_form_qual_info_required(self):
        """registration form qualifying info field must not be empty
        """
        from .. import models
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'captcha': 400
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        self.assertContains(response, 'This field is required.')
        self.assertNotContains(response, 'Hint')

    def test_registration_form_captcha_answer_required(self):
        """registration form CAPTCHA answer field must not be missing
        """
        from .. import models
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'qual_info': 'LM300',
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.post(url, params)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'Hint')

    def test_registration_form_captcha_answer_is_int(self):
        """registration form CAPTCHA answer field must be an integer
        """
        from .. import models
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'qual_info': 'LM300',
            'captcha': 'afdga',
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.post(url, params)
        self.assertContains(response, 'Enter a whole number.')
        self.assertContains(response, 'Hint')

    def test_registration_form_captcha_answer_not_empty(self):
        """registration form CAPTCHA answer field must not be empty
        """
        from .. import models
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'qual_info': 'LM300',
            'captcha': ''
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.post(url, params)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'Hint')

    def test_registration_form_captcha_answer_wrong(self):
        """registration form CAPTCHA wrong answer
        """
        from .. import models
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'qual_info': 'LM300',
            'captcha': 200
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.post(url, params)
        self.assertContains(response, 'Wrong! See hint.')
        self.assertContains(response, 'Hint')

    def test_registration_form_handles_duplicate_entry(self):
        """registration form rejects duplicate entry w/ msg on brevet page
        """
        from .. import models
        from ..models import Brevet
        from ..models import BrevetRider
        # Register for the brevet
        brevet = Brevet.objects.get(
            region='LM', event=300, date=date(2010, 5, 1))
        BrevetRider(
            first_name='Doug',
            last_name='Latornell',
            email='djl@example.com',
            brevet=brevet).save()
        # Try to register again
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        # Confirm the redriect, and flash message content
        rider = BrevetRider.objects.filter(
            first_name='Doug', last_name='Latornell',
            email='djl@example.com', brevet=brevet)
        url = reverse(
            'register:prereg-duplicate',
            args=('LM', 300, '01May2010', rider[0].id))
        self.assertRedirects(response, url)
        self.assertContains(
            response,
            'Hmm... Someone using the name <kbd>Doug Latornell</kbd>')
        self.assertContains(
            response, 'email address <kbd>djl@example.com</kbd>')
        self.assertNotContains(
            response, 'You must be a member of the club to ride')

    def test_registration_queues_update_google_spreadsheet_task(self):
        """successful registration queues task to update rider list
        """
        from .. import models
        from .. import views
        from ..models import Brevet
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        datetime_patch = patch.object(models, 'datetime')
        task_patch = patch.object(views, 'update_google_spreadsheet')
        with datetime_patch as mock_datetime, task_patch as mock_task:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.client.post(url, params)
        brevet = Brevet.objects.get(
            region='LM', event=300, date=date(2010, 5, 1))
        mock_task.delay.assert_called_once_with(brevet.pk)

    def test_registration_queues_email_to_rider_task(self):
        """successful registration queues task to send email to rider
        """
        from .. import models
        from .. import views
        from ..models import Brevet
        from ..models import BrevetRider
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        datetime_patch = patch.object(models, 'datetime')
        ugs_patch = patch.object(views, 'update_google_spreadsheet')
        task_patch = patch.object(views, 'email_to_rider')
        with datetime_patch as mock_datetime, ugs_patch, \
             task_patch as mock_task:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.client.post(url, params)
        brevet = Brevet.objects.get(
            region='LM', event=300, date=date(2010, 5, 1))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        mock_task.delay.assert_called_once_with(
            brevet.pk, rider.pk, 'testserver')

    def test_registration_queues_email_to_organizer_task(self):
        """successful registration queues task to send email to organizer
        """
        from .. import models
        from .. import views
        from ..models import Brevet
        from ..models import BrevetRider
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        datetime_patch = patch.object(models, 'datetime')
        ugs_patch = patch.object(views, 'update_google_spreadsheet')
        task_patch = patch.object(views, 'email_to_organizer')
        with datetime_patch as mock_datetime, ugs_patch, \
             task_patch as mock_task:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.client.post(url, params)
        brevet = Brevet.objects.get(
            region='LM', event=300, date=date(2010, 5, 1))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        mock_task.delay.assert_called_once_with(
            brevet.pk, rider.pk, 'testserver')


class TestRiderEmailsView(django.test.TestCase):
    """Functional tests for rider email address list view.
    """
    fixtures = ['brevets.yaml', 'riders.yaml']

    def test_rider_emails_bad_uuid(self):
        """request for rider's emails with bad brevet uuid raises 404
        """
        url = reverse(
            'register:rider-emails', args=('LM', '200', '17Apr2010', 'f00'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_rider_emails_event_past(self):
        """request for rider's emails for event >7 days ago raises 404
        """
        from .. import models
        url = reverse(
            'register:rider-emails',
            args=('LM', '200', '17Apr2010',
                  'eb45e7d4-46b5-5efc-9d17-8d25a74fcae0'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 27)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_rider_emails_returns_msg(self):
        """request for rider's emails for event w/ no riders returns msg
        """
        from .. import models
        url = reverse(
            'register:rider-emails',
            args=('LM', '300', '01May2010',
                  'dc554a2d-50ce-5c67-ba40-aa541ab3bf2d'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'No riders have registered yet!')

    def test_1_rider_email(self):
        """request for rider's emails for event w/ 1 rider returns address
        """
        from .. import models
        url = reverse(
            'register:rider-emails',
            args=('LM', 400, '22May2010',
                  'eb280730-b798-5560-a665-b849a908feb7'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'djl@douglatornell.ca')

    def test_2_rider_emails(self):
        """request for rider's emails for event w/ 2 riders returns list
        """
        from .. import models
        url = reverse(
            'register:rider-emails',
            args=('LM', '200', '17Apr2010',
                  'eb45e7d4-46b5-5efc-9d17-8d25a74fcae0'))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertEqual(
            set(response.content.split(', ')),
            set('sea@susanallen.ca fibber.mcgee@example.com'.split()))
