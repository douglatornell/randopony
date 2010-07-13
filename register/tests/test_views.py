"""View tests for RandoPony register app.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-06
"""
# Standard library:
from datetime import date, datetime, timedelta
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
        response = self.client.get(
            reverse('randopony.register.views.home'))
        self.assertContains(response, 'RandoPony::Registration')


    def test_home_context(self):
        """home view has correct context
        """
        response = self.client.get(
            reverse('randopony.register.views.home'))
        self.assertTrue(response.context['regions'])
        self.assertTrue(response.context['admin_email'])


    def test_home_base_sidebar(self):
        """home view renders brevets list
        """
        response = self.client.get(
            reverse('randopony.register.views.home'))
        self.assertContains(response, 'Home')
        self.assertContains(response, 'randonneurs.bc.ca')
        self.assertContains(response, 'Info for Brevet Organizers')
        self.assertContains(response, "What's up with the pony?")


    def test_home_regions_list(self):
        """home view renders regions list
        """
        response = self.client.get(
            reverse('randopony.register.views.home'))
        self.assertContains(response, 'Lower Mainland')
        self.assertNotContains(response, 'Vancouver Island')


class TestRegionBrevetsView(django.test.TestCase):
    fixtures = ['brevets']

    def setUp(self):
        for brevet in model.Brevet.objects.all():
            today = date.today()
            if brevet.date <= today:
                brevet.date = brevet.date.replace(year=today.year + 1)
            brevet.save()

    def test_region_brevets_get(self):
        """GET request for root page of register app works
        """
        response = self.client.get('/register/LM-brevets/')
        self.assertEqual(response.status_code, 200)


    def test_region_brevets_context(self):
        """home view has correct context
        """
        response = self.client.get('/register/LM-brevets/')
        self.assertTrue(response.context['region'])
        self.assertTrue(response.context['brevets'])


    def test_region_brevets_list(self):
        """region_brevets view renders brevets list
        """
        response = self.client.get('/register/LM-brevets/')
        for brevet in model.Brevet.objects.all():
            self.assertTrue(unicode(brevet) in response.content)


    def test_region_brevets_past_events(self):
        """region_brevets view excludes past events correctly
        """
        today = date.today()
        brevets = model.Brevet.objects.all()
        recent_brevet = brevets[0]
        recent_brevet.date = today - timedelta(days=2)
        recent_brevet.save()
        older_brevet = brevets[1]
        older_brevet.date = today - timedelta(days=10)
        older_brevet.save()
        response = self.client.get('/register/LM-brevets/')
        self.assertTrue(unicode(recent_brevet) in response.content)
        self.assertFalse(unicode(older_brevet) in response.content)


class TestBrevetView(django.test.TestCase):
    fixtures = ['brevets', 'riders']

    def setUp(self):
        for brevet in model.Brevet.objects.all():
            today = date.today()
            if brevet.date <= today:
                brevet.date = brevet.date.replace(year=today.year + 1)
            brevet.save()

    def test_brevet_get(self):
        """GET request for brevet page works
        """
        response = self.client.get(
            '/register/',
            {'region': 'LM', 'distance': 300, 'date':'01May2010'})
        self.assertEqual(response.status_code, 200)


    def test_brevet_page_sidebar(self):
        """brevet view renders correct sidebar
        """
        response = self.client.get('/register/LM300/01May2010/')
        self.assertTrue('LM300 01-May-2010' in response.content)
        self.assertTrue('Register' in response.content)
        self.assertTrue('Event Entry Form (PDF)' in response.content)
        self.assertTrue('Club Membership Form (PDF)' in response.content)


    def test_past_brevet_page(self):
        """page for brevet >7 days ago is pointer to club site
        """
        response = self.client.get('/register/LM400/05May2009/')
        self.assertContains(
            response, 'brevet is over, and the RandoPony has moved on!')
        self.assertContains(
            response, 'http://randonneurs.bc.ca/results/09_times/09_times.html')


    def test_brevet_page_no_riders(self):
        """brevet page has expected msg when no riders are registered
        """
        response = self.client.get('/register/LM300/01May2010/')
        self.assertContains(response, 'Be the first!')


    def test_brevet_page_1_rider(self):
        """brevet view renders correct page body with 1 registered rider
        """
        response = self.client.get('/register/LM400/22May2010/')
        self.assertContains(response, 'Manning Park')
        self.assertContains(response, '1 Pre-registered Rider')
        self.assertContains(response, 'Doug Latornell')
        self.assertNotContains(response, 'registered for this brevet. Cool!')
        self.assertNotContains(response, 'Be the first!')


    def test_brevet_page_2_riders(self):
        """brevet view renders correct page body with 2 registered riders
        """
        response = self.client.get('/register/LM200/17Apr2010/')
        self.assertContains(response, '2 Pre-registered Riders')


    def test_brevet_page_confirmation(self):
        """brevet view renders correct sidebar
        """
        response = self.client.get('/register/LM400/22May2010/1/')
        self.assertTrue('for this brevet. Cool!' in response.content)


class TestRegistrationFormView(django.test.TestCase):
    fixtures = ['brevets']

    def test_registration_form_get(self):
        """GET request for registration from page works
        """
        response = self.client.get('/register/LM400/22May2010/form/')
        self.assertEqual(response.status_code, 200)


    def test_brevet_registration_form_sidebar(self):
        """registration form view renders correct sidebar
        """
        response = self.client.get('/register/LM400/22May2010/')
        self.assertTrue('LM400 22-May-2010' in response.content)
        self.assertTrue('Register' in response.content)
        self.assertTrue('Event Entry Form (PDF)' in response.content)
        self.assertTrue('Club Membership Form (PDF)' in response.content)


    def test_brevet_registration_form_body_with_qual_info(self):
        """registration form view renders page with qual info question
        """
        response = self.client.get('/register/LM400/22May2010/form/')
        self.assertTrue('Manning Park' in response.content)
        self.assertTrue('Name:' in response.content)
        self.assertTrue('Email:' in response.content)
        self.assertTrue('Club member?' in response.content)
        self.assertTrue(
            'recent 300 km brevet; e.g. LM300 1-May-' in response.content)
        self.assertTrue('Qualifying info:' in response.content)


    def test_brevet_registration_form_body_wo_qual_info(self):
        """registration form view renders correct page w/o qual info question
        """
        response = self.client.get('/register/LM300/01May2010/form/')
        self.assertFalse('Qualifying info:' in response.content)


    def test_brevet_registration_form_has_captcha(self):
        """registration form view renders captcha question
        """
        response = self.client.get('/register/LM300/01May2010/form/')
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
        response = self.client.post('/register/LM300/01May2010/form/',
                                    {'name': 'Doug Latornell',
                                     'email': 'djl@example.com',
                                     'club_member': True,
                                     'captcha': 400},
                                    follow=True)
        rider_id = model.Rider.objects.order_by('-id')[0].id
        self.assertRedirects(
            response, '/register/LM300/01May2010/%(rider_id)d/' % vars())
        self.assertContains(
            response, 'You have pre-registered for this brevet. Cool!')
        self.assertContains(
            response, 'djl at example dot com')
        self.assertNotContains(
            response, 'You must be a member of the club to ride')


    def test_registration_form_clean_submit_non_member(self):
        """registration from submit redirects to brevet pg w/ non-member msg
        """
        response = self.client.post('/register/LM300/01May2010/form/',
                                    {'name': 'Fibber McGee',
                                     'email': 'fibber@example.com',
                                     'club_member': False,
                                     'captcha': 400},
                                    follow=True)
        rider_id = model.Rider.objects.order_by('-id')[0].id
        self.assertRedirects(
            response, '/register/LM300/01May2010/%(rider_id)d/' % vars())
        self.assertContains(
            response, 'You have pre-registered for this brevet. Cool!')
        self.assertContains(
            response, 'fibber at example dot com')
        self.assertContains(
            response, 'You must be a member of the club to ride')


    def test_registration_form_name_required(self):
        """registration form name field must not be empty
        """
        response = self.client.post('/register/LM300/01May2010/form/',
                                     {'email': 'fibber@example.com',
                                      'club_member': False,
                                      'captcha': 400})
        self.assertContains(response, 'This field is required.')
        self.assertNotContains(response, 'Hint')


    def test_registration_form_email_required(self):
        """registration form email field must not be empty
        """
        response = self.client.post('/register/LM300/01May2010/form/',
                                     {'name': 'Fibber McGee',
                                      'club_member': False,
                                      'captcha': 400})
        self.assertContains(response, 'This field is required.')
        self.assertNotContains(response, 'Hint')


    def test_registration_form_email_valid(self):
        """registration form email field must be valid
        """
        response = self.client.post('/register/LM300/01May2010/form/',
                                     {'name': 'Fibber McGee',
                                      'email': 'fibber',
                                      'club_member': False,
                                      'captcha': 400})
        self.assertContains(response, 'Enter a valid e-mail address.')
        self.assertNotContains(response, 'Hint')


    def test_registration_form_qual_info_required(self):
        """registration form qualifying info field must not be empty
        """
        response = self.client.post('/register/LM400/22May2010/form/',
                                     {'name': 'Fibber McGee',
                                      'email': 'fibber@example.com',
                                      'club_member': False,
                                      'captcha': 400})
        self.assertContains(response, 'This field is required.')
        self.assertNotContains(response, 'Hint')


    def test_registration_form_captcah_answer_required(self):
        """registration form CAPTCHA answer field must not be empty
        """
        response = self.client.post('/register/LM400/22May2010/form/',
                                     {'name': 'Fibber McGee',
                                      'email': 'fibber@example.com',
                                      'club_member': False,
                                      'qual_info': 'LM300'})
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'Hint')


    def test_registration_form_captcha_answer_is_int(self):
        """registration form CAPTCHA answer field must not be empty
        """
        response = self.client.post('/register/LM400/22May2010/form/',
                                     {'name': 'Fibber McGee',
                                      'email': 'fibber@example.com',
                                      'club_member': False,
                                      'qual_info': 'LM300',
                                      'captcha': 'afdga'})
        self.assertContains(response, 'Enter a whole number.')
        self.assertContains(response, 'Hint')


    def test_registration_form_captcha_answer_not_empty(self):
        """registration form CAPTCHA answer field must not be empty
        """
        response = self.client.post('/register/LM400/22May2010/form/',
                                     {'name': 'Fibber McGee',
                                      'email': 'fibber@example.com',
                                      'club_member': False,
                                      'qual_info': 'LM300',
                                      'captcha': 'afdga'})
        self.assertContains(response, 'Enter a whole number.')
        self.assertContains(response, 'Hint')


    def test_registration_form_captcha_answer_wrong(self):
        """registration form CAPTCHA wrong answer
        """
        response = self.client.post('/register/LM400/22May2010/form/',
                                     {'name': 'Fibber McGee',
                                      'email': 'fibber@example.com',
                                      'club_member': False,
                                      'qual_info': 'LM300',
                                      'captcha': 200})
        self.assertContains(response, 'Wrong! See hint.')
        self.assertContains(response, 'Hint')


    def test_registration_form_handles_duplicate_entry(self):
        """registration form rejects duplicate entry w/ msg on brevet page
        """
        # Register for the brevet
        brevet_date = datetime.strptime('01May2010', '%d%b%Y').date()
        brevet = model.Brevet.objects.get(
            region='LM', distance=300, date=brevet_date)
        model.Rider(
            name='Doug Latornell',
            email='djl@example.com',
            brevet=brevet).save()
        # Try to register again
        response = self.client.post('/register/LM300/01May2010/form/',
                                    {'name': 'Doug Latornell',
                                     'email': 'djl@example.com',
                                     'club_member': True,
                                     'captcha': 400},
                                    follow=True)
        # Confirm the redriect, and flash message content
        rider_query = model.Rider.objects.filter(
            name='Doug Latornell', email='djl@example.com', brevet=brevet)
        self.assertRedirects(
            response, '/register/LM300/01May2010/%(rider_id)d/duplicate/'
            % {'rider_id': rider_query[0].id})
        self.assertContains(
            response, 'Hmm... Someone using the name <kbd>Doug Latornell</kbd>')
        self.assertContains(
            response, 'email address <kbd>djl at example dot com</kbd>')
        self.assertNotContains(
            response, 'You must be a member of the club to ride')


    def test_registration_form_sends_email_to_club_member(self):
        """successful registration sends emails to member/rider & organizer
        """
        self.client.post('/register/LM300/01May2010/form/',
                         {'name': 'Doug Latornell',
                          'email': 'djl@example.com',
                          'club_member': True,
                          'captcha': 400})
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
            'Doug Latornell has pre-registered for the LM300 01-May-2010 brevet'
            in mail.outbox[1].body)
        self.assertTrue(
            'has indicated that zhe is a club member' in mail.outbox[1].body)
        self.assertTrue(
            'please send email to %s' % settings.ADMINS[0][1]
            in mail.outbox[1].body)


    def test_registration_form_sends_email_to_non_member(self):
        """successful registration sends emails to non-member/rider & organizer
        """
        self.client.post('/register/LM300/01May2010/form/',
                         {'name': 'Fibber McGee',
                          'email': 'fibber@example.com',
                          'club_member': False,
                          'captcha': 400})
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
        self.client.post('/register/LM400/22May2010/form/',
                         {'name': 'Fibber McGee',
                          'email': 'fibber@example.com',
                          'club_member': False,
                          'qual_info': 'LM300',
                          'captcha': 400})
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
            'listed LM300 as their qualification' in mail.outbox[1].body)


class TestAboutPonyView(django.test.TestCase):
    def test_about_pony_get(self):
        """GET request for about RandoPony page works
        """
        response = self.client.get(
            reverse('randopony.register.views.about_pony'))
        self.assertEqual(response.status_code, 200)


    def test_about_pony_sidebar(self):
        """organizer_info view renders expected sidebar
        """
        response = self.client.get(
            reverse('randopony.register.views.about_pony'))
        self.assertTrue('Home' in response.content)
        self.assertTrue('randonneurs.bc.ca' in response.content)
        self.assertTrue('Info for Brevet Organizers' in response.content)
        self.assertTrue("What's up with the pony?" in response.content)


class TestOrganizerInfoView(django.test.TestCase):
    def test_organizer_info_get(self):
        """GET request for orgainzers info page works
        """
        response = self.client.get(
            reverse('randopony.register.views.organizer_info'))
        self.assertEqual(response.status_code, 200)


    def test_organizer_info_sidebar(self):
        """organizer_info view renders expected sidebar
        """
        response = self.client.get(
            reverse('randopony.register.views.organizer_info'))
        self.assertTrue('Home' in response.content)
        self.assertTrue('randonneurs.bc.ca' in response.content)
        self.assertTrue('Info for Brevet Organizers' in response.content)
        self.assertTrue("What's up with the pony?" in response.content)
