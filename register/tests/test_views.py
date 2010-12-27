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
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
# Application:
import randopony.register.models as model


class TestHomeView(django.test.TestCase):
    fixtures = ['brevets']

    def test_home_get(self):
        """GET request for root page of register app works
        """
        response = self.client.get(reverse('register:home'))
        self.assertContains(response, 'RandoPony::Registration')


    def test_home_context(self):
        """home view has correct context
        """
        with patch('randopony.register.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.get(reverse('register:home'))
        self.assertTrue(response.context['regions'])
        self.assertTrue(response.context['admin_email'])


    def test_home_base_sidebar(self):
        """home view renders brevets list
        """
        response = self.client.get(reverse('register:home'))
        self.assertContains(response, 'Home')
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'Info for Brevet Organizers')
        self.assertContains(response, "What's up with the pony?")


    def test_home_regions_list(self):
        """home view renders regions list
        """
        with patch('randopony.register.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.get(reverse('register:home'))
        self.assertContains(response, 'Lower Mainland')
        self.assertContains(response, 'Vancouver Island')
        self.assertNotContains(response, 'Southern Interior')
        self.assertNotContains(response, 'Peace Region')
        self.assertNotContains(response, 'Club Events')
        self.assertNotContains(response, 'Super Week')


class TestRegionBrevetsView(django.test.TestCase):
    fixtures = ['brevets']

    def test_region_brevets_get(self):
        """GET request for region brevets list page of register app works
        """
        response = self.client.get('/register/LM-events/')
        self.assertContains(response, 'RandoPony::Lower Mainland')


    def test_region_brevets_context(self):
        """region_brevets view has correct context
        """
        with patch('randopony.register.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.get('/register/LM-events/')
        self.assertTrue(response.context['region'])
        self.assertTrue(response.context['brevets'])


    def test_region_brevets_list(self):
        """region_brevets view renders brevets list
        """
        with patch('randopony.register.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.get('/register/LM-events/')
        for brevet in model.Brevet.objects.filter(region='LM'):
            self.assertContains(response, unicode(brevet))


    def test_region_brevets_list_excludes_past_events(self):
        """region_brevets view excludes past events correctly
        """
        with patch('randopony.register.views.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 27)
            response = self.client.get('/register/LM-events/')
        self.assertContains(response, 'LM400 22-May-2010')
        self.assertNotContains(response, 'LM200 17-Apr-2010')


class TestBrevetView(django.test.TestCase):
    fixtures = ['brevets', 'riders']

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
        url = reverse('register:brevet', args=('LM', 300, '01May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
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
        url = reverse('register:brevet', args=('LM', 300, '01May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 5, 9)
            mock_datetime.now.return_value = datetime(2010, 5, 9, 19, 21)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(
            response, 'brevet is over, and the RandoPony has moved on!')
        self.assertContains(
            response,
            'http://randonneurs.bc.ca/results/10_times/10_times.html')
        self.assertNotContains(response, 'Be the first!')


    def test_brevet_started_page(self):
        """registration closed message suppressed 1 hour after brevet s
        """
        url = reverse('register:brevet', args=('LM', 300, '01May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
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
        url = reverse('register:brevet', args=('LM', 300, '01May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Be the first!')


    def test_brevet_page_1_rider(self):
        """brevet view renders correct page body with 1 registered rider
        """
        url = reverse('register:brevet', args=('LM', 400, '22May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
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
        url = reverse('register:brevet', args=('LM', 200, '17Apr2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, '2 Pre-registered')


    def test_brevet_page_prereg_confirmation(self):
        """brevet view w/ rider id includes pre-registration confirmation msg
        """
        url = reverse(
            'register:prereg-confirm', args=('LM', 400, '22May2010', 1))
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'for this event. Cool!')


    def test_brevet_page_duplicate_prereg(self):
        """brevet view includes duplicate pre-registration msg when appropos
        """
        url = reverse(
            'register:prereg-duplicate', args=('LM', 400, '22May2010', 1))
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(response, 'Hmm... Someone using the name')


class TestRegistrationFormView(django.test.TestCase):
    fixtures = ['brevets']

    def test_registration_form_get(self):
        """GET request for registration form page works
        """
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


    def test_brevet_registration_form_sidebar(self):
        """registration form view renders correct sidebar
        """
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
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
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
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
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertNotContains(response, 'Brevet info:')


    def test_brevet_registration_form_has_captcha(self):
        """registration form view renders captcha question
        """
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.get(url)
        self.assertContains(
            response, 'Are you a human? Are you a randonneur? Please prove it.')
        self.assertContains(
            response, 'A Super Randonneur series consists of brevets of '
            '200 km, 300 km, ___ km, and 600 km. Fill in the blank:')


class TestRegistrationFunction(django.test.TestCase):
    fixtures = ['brevets', 'riders']

    def test_registration_form_clean_submit(self):
        """registration from submit w/ valid data redirects to brevet pg w/ msg
        """
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        rider_id = model.BrevetRider.objects.order_by('-id')[0].id
        url = reverse(
            'register:prereg-confirm', args=('LM', 300, '01May2010', rider_id))
        self.assertRedirects(response, url)
        self.assertContains(
            response, 'You have pre-registered for this event. Cool!')
        self.assertContains(
            response, 'djl at example dot com')
        self.assertNotContains(
            response, 'You must be a member of the club to ride')


    def test_registration_form_clean_submit_non_member(self):
        """registration from submit redirects to brevet pg w/ non-member msg
        """
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        rider_id = model.BrevetRider.objects.order_by('-id')[0].id
        url = reverse(
            'register:prereg-confirm', args=('LM', 300, '01May2010', rider_id))
        self.assertRedirects(response, url)
        self.assertContains(
            response, 'You have pre-registered for this event. Cool!')
        self.assertContains(
            response, 'fibber at example dot com')
        self.assertContains(
            response, 'You must be a member of the club to ride')


    def test_registration_form_first_name_required(self):
        """registration form first name field must not be empty
        """
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
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
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Fibber',
            'email': 'fibber@example.com',
            'club_member': False,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
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
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'club_member': True,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
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
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'LatMcGeeornell',
            'email': 'fibber',
            'club_member': False,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
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
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        self.assertContains(response, 'This field is required.')
        self.assertNotContains(response, 'Hint')


    def test_registration_form_captcha_answer_required(self):
        """registration form CAPTCHA answer field must not be empty
        """
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'qual_info': 'LM300',
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.post(url, params)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'Hint')


    def test_registration_form_captcha_answer_is_int(self):
        """registration form CAPTCHA answer field must not be empty
        """
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'qual_info': 'LM300',
            'captcha': 'afdga'
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.post(url, params)
        self.assertContains(response, 'Enter a whole number.')
        self.assertContains(response, 'Hint')


    def test_registration_form_captcha_answer_not_empty(self):
        """registration form CAPTCHA answer field must not be empty
        """
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'qual_info': 'LM300',
            'captcha': 'afdga'
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.post(url, params)
        self.assertContains(response, 'Enter a whole number.')
        self.assertContains(response, 'Hint')


    def test_registration_form_captcha_answer_wrong(self):
        """registration form CAPTCHA wrong answer
        """
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'qual_info': 'LM300',
            'captcha': 200
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            response = self.client.post(url, params)
        self.assertContains(response, 'Wrong! See hint.')
        self.assertContains(response, 'Hint')


    def test_registration_form_handles_duplicate_entry(self):
        """registration form rejects duplicate entry w/ msg on brevet page
        """
        # Register for the brevet
        brevet = model.Brevet.objects.get(
            region='LM', event=300, date=date(2010, 5, 1))
        model.BrevetRider(
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
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            response = self.client.post(url, params, follow=True)
        # Confirm the redriect, and flash message content
        rider = model.BrevetRider.objects.filter(
            first_name='Doug', last_name='Latornell',
            email='djl@example.com', brevet=brevet)
        url = reverse(
            'register:prereg-duplicate',
            args=('LM', 300, '01May2010', rider[0].id))
        self.assertRedirects(response, url)
        self.assertContains(
            response, 'Hmm... Someone using the name <kbd>Doug Latornell</kbd>')
        self.assertContains(
            response, 'email address <kbd>djl at example dot com</kbd>')
        self.assertNotContains(
            response, 'You must be a member of the club to ride')


    def test_registration_form_sends_email_for_club_member(self):
        """successful registration sends emails to member/rider & organizer
        """
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.client.post(url, params)
        self.assertEqual(len(mail.outbox), 2)
        # Email to rider
        self.assertEqual(
            mail.outbox[0].subject,
            'Pre-registration Confirmation for LM300 01-May-2010 Brevet')
        self.assertEqual(mail.outbox[0].to, ['djl@example.com'])
        self.assertEqual(
            mail.outbox[0].from_email, 'pumpkinrider@example.com')
        self.assertTrue(
            'pre-registered for the BC Randonneurs LM300 01-May-2010 brevet'
            in mail.outbox[0].body)
        self.assertTrue(
            'http://testserver/register/LM300/01May2010/'
            in mail.outbox[0].body)
        self.assertTrue(
            'print out the event waiver form' in mail.outbox[0].body)
        self.assertTrue(
            'auto-generated email, but you can reply to it '
            'to contact the brevet organizer'
            in mail.outbox[0].body)
        # Email to organizer
        self.assertEqual(
            mail.outbox[1].subject,
            'Doug Latornell has Pre-registered for the LM300 01-May-2010')
        self.assertEqual(mail.outbox[1].to, ['pumpkinrider@example.com'])
        self.assertEqual(
            mail.outbox[1].from_email, settings.REGISTRATION_EMAIL_FROM)
        self.assertTrue(
            'Doug Latornell (djl@example.com) has pre-registered for the '
            'LM300 01-May-2010 brevet'
            in mail.outbox[1].body)
        self.assertTrue(
            'has indicated that zhe is a club member' in mail.outbox[1].body)
        self.assertTrue(
            'please send email to {0}'.format(settings.ADMINS[0][1])
            in mail.outbox[1].body)


    def test_registration_form_sends_email_for_non_member(self):
        """successful registration sends emails to non-member/rider & organizer
        """
        url = reverse('register:form', args=('VI', 600, '07Aug2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 8, 1)
            mock_datetime.now.return_value = datetime(2010, 8, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.client.post(url, params)
        self.assertEqual(len(mail.outbox), 2)
        # Email to rider
        self.assertEqual(mail.outbox[0].to, ['fibber@example.com'])
        self.assertTrue(
            'indicated that you are NOT a member' in mail.outbox[0].body)
        # Email to organizer
        self.assertTrue(
            'has indicated that zhe is NOT a club member'
            in mail.outbox[1].body)
        self.assertTrue(
            'join beforehand, or at the start' in mail.outbox[1].body)
         

    def test_registration_form_sends_email_with_qualifying_info(self):
        """successful registration email to organizer includes qualifying info
        """
        url = reverse('register:form', args=('LM', 400, '22May2010'))
        params = {
            'first_name': 'Fibber',
            'last_name': 'McGee',
            'email': 'fibber@example.com',
            'club_member': False,
            'info_answer': 'LM300',
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.client.post(url, params)
        self.assertEqual(len(mail.outbox), 2)
        # Email to rider
        self.assertEqual(
            mail.outbox[0].subject,
            'Pre-registration Confirmation for LM400 22-May-2010 Brevet')
        self.assertTrue(
            'http://testserver/register/LM400/22May2010/'
            in mail.outbox[0].body)
        # Email to organizer
        self.assertEqual(
            mail.outbox[1].subject,
            'Fibber McGee has Pre-registered for the LM400 22-May-2010')
        self.assertTrue(
            'Fibber McGee has answered LM300.' in mail.outbox[1].body)


    def test_registration_form_email_has_rider_address(self):
        """registration email to organizer contains rider email address
        """
        url = reverse('register:form', args=('LM', 300, '01May2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            mock_datetime.now.return_value = datetime(2010, 4, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.client.post(url, params)
        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue('djl@example.com' in mail.outbox[1].body)


    def test_registration_form_email_to_2_organizers(self):
        """registration email goes to multiple organizers
        """
        url = reverse('register:form', args=('VI', 600, '07Aug2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 8, 1)
            mock_datetime.now.return_value = datetime(2010, 8, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.client.post(url, params)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            set(mail.outbox[1].to),
            set('mcroy@example.com dug.andrusiek@example.com'.split()))


    def test_registration_form_email_replyto_2_organizers(self):
        """registration email to rider has 2 organizers in reply-to header
        """
        url = reverse('register:form', args=('VI', 600, '07Aug2010'))
        params = {
            'first_name': 'Doug',
            'last_name': 'Latornell',
            'email': 'djl@example.com',
            'club_member': True,
            'captcha': 400
        }
        with patch('randopony.register.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 8, 1)
            mock_datetime.now.return_value = datetime(2010, 8, 1, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.client.post(url, params)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].from_email,
            'mcroy@example.com, dug.andrusiek@example.com')
        self.assertEqual(
            mail.outbox[0].extra_headers['Reply-To'],
            'mcroy@example.com, dug.andrusiek@example.com')
        self.assertEqual(
            mail.outbox[0].extra_headers['Sender'],
            settings.REGISTRATION_EMAIL_FROM)


class TestRiderEmailsView(django.test.TestCase):
    fixtures = ['brevets', 'riders']

    def test_no_rider_emails_raises_404(self):
        """request for rider's emails for event w/ no riders raises 404
        """
        url = reverse('register:rider-emails', args=('LM', '200', '20Nov2010'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_rider_emails_event_past(self):
        """request for rider's emails for event >7 days ago raises 404
        """
        url = reverse('register:rider-emails', args=('LM', '300', '01May2009'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_1_rider_email(self):
        """request for rider's emails for event w/ 1 rider returns address
        """
        url = reverse('register:rider-emails', args=('LM', 400, '22May2010'))
        response = self.client.get(url)
        self.assertContains(response, 'djl@douglatornell.ca')


    def test_2_rider_emails(self):
        """request for rider's emails for event w/ 2 riders returns list
        """
        url = reverse('register:rider-emails', args=('LM', '200', '17Apr2010'))
        response = self.client.get(url)
        self.assertEqual(
            set(response.content.split(', ')),
            set('sea@susanallen.ca fibber.mcgee@example.com'.split()))


class TestAboutPonyView(django.test.TestCase):
    def test_about_pony_get(self):
        """GET request for about RandoPony page works
        """
        response = self.client.get(reverse('about_pony'))
        self.assertEqual(response.status_code, 200)


    def test_about_pony_sidebar(self):
        """organizer_info view renders expected sidebar
        """
        response = self.client.get(reverse('about_pony'))
        self.assertTrue('Home' in response.content)
        self.assertTrue('randonneurs.bc.ca' in response.content)
        self.assertTrue('Info for Brevet Organizers' in response.content)
        self.assertTrue("What's up with the pony?" in response.content)


class TestOrganizerInfoView(django.test.TestCase):
    def test_organizer_info_get(self):
        """GET request for orgainzers info page works
        """
        response = self.client.get(reverse('organizer_info'))
        self.assertEqual(response.status_code, 200)


    def test_organizer_info_sidebar(self):
        """organizer_info view renders expected sidebar
        """
        response = self.client.get(reverse('organizer_info'))
        self.assertTrue('Home' in response.content)
        self.assertTrue('randonneurs.bc.ca' in response.content)
        self.assertTrue('Info for Brevet Organizers' in response.content)
        self.assertTrue("What's up with the pony?" in response.content)
