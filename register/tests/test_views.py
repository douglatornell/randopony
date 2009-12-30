"""View tests for RandoPony register app.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-06
"""
# Standard library:
from datetime import datetime
# Django:
import django.test
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
        self.failUnlessEqual(response.status_code, 200)


    def test_home_context(self):
        """home view has correct context
        """
        response = self.client.get(
            reverse('randopony.register.views.home'))
        self.failUnless(response.context['brevets'])
        self.failUnless(response.context['admin_email'])


    def test_home_base_sidebar(self):
        """home view renders brevets list
        """
        response = self.client.get(
            reverse('randopony.register.views.home'))
        self.failUnless('Home' in response.content)
        self.failUnless('randonneurs.bc.ca' in response.content)
        self.failUnless('Info for Brevet Organizers' in response.content)
        self.failUnless("What's up with the pony?" in response.content)


    def test_home_brevet_list(self):
        """home view renders brevets list
        """
        response = self.client.get(
            reverse('randopony.register.views.home'))
        self.failUnless('LM300 01-May-2010' in response.content)
        self.failUnless('LM400 22-May-2010' in response.content)


class TestBrevetView(django.test.TestCase):
    fixtures = ['brevets', 'riders']

    def test_brevet_get(self):
        """GET request for brevet page works
        """
        response = self.client.get(
            '/register/',
            {'region': 'LM', 'distance': 300, 'date':'01May2010'})
        self.failUnlessEqual(response.status_code, 200)


    def test_brevet_page_sidebar(self):
        """brevet view renders correct sidebar
        """
        response = self.client.get('/register/LM300/01May2010/')
        self.failUnless('LM300 01-May-2010' in response.content)
        self.failUnless('Register' in response.content)
        self.failUnless('Event Entry Form (PDF)' in response.content)
        self.failUnless('Club Membership Form (PDF)' in response.content)


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
        self.failUnless('for this brevet. Cool!' in response.content)


class TestRegistrationFormView(django.test.TestCase):
    fixtures = ['brevets']

    def test_registration_form_get(self):
        """GET request for registration from page works
        """
        response = self.client.get('/register/LM400/22May2010/form/')
        self.failUnlessEqual(response.status_code, 200)


    def test_brevet_registration_form_sidebar(self):
        """registration form view renders correct sidebar
        """
        response = self.client.get('/register/LM400/22May2010/')
        self.failUnless('LM400 22-May-2010' in response.content)
        self.failUnless('Register' in response.content)
        self.failUnless('Event Entry Form (PDF)' in response.content)
        self.failUnless('Club Membership Form (PDF)' in response.content)


    def test_brevet_registration_form_body_with_qual_info(self):
        """registration form view renders page with qual info question
        """
        response = self.client.get('/register/LM400/22May2010/form/')
        self.failUnless('Manning Park' in response.content)
        self.failUnless('Name:' in response.content)
        self.failUnless('Email:' in response.content)
        self.failUnless('Club member?' in response.content)
        self.failUnless(
            'recent 300 km brevet; e.g. LM300 1-May-' in response.content)
        self.failUnless('Qualifying info:' in response.content)


    def test_brevet_registration_form_body_wo_qual_info(self):
        """registration form view renders correct page w/o qual info question
        """
        response = self.client.get('/register/LM300/01May2010/form/')
        self.failIf('Qualifying info:' in response.content)


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
        brevet_date = datetime.strptime('01May2010', '%d%b%Y').date()
        brevet = model.Brevet.objects.get(
            region='LM', distance=300, date=brevet_date)
        model.Rider(
            name='Doug Latornell',
            email='djl@example.com',
            brevet=brevet).save()
        response = self.client.post('/register/LM300/01May2010/form/',
                                    {'name': 'Doug Latornell',
                                     'email': 'djl@example.com',
                                     'club_member': True,
                                     'captcha': 400},
                                    follow=True)
        rider_query = model.Rider.objects.filter(
            name='Doug Latornell', email='djl@example.com', brevet=brevet)
        rider_id = rider_query[0].id
        self.assertRedirects(
            response, '/register/LM300/01May2010/%(rider_id)d/duplicate/'
            % vars())
        self.assertContains(
            response, 'Hmm... Someone using the name <kbd>Doug Latornell</kbd>')
        self.assertContains(
            response, 'email address <kbd>djl at example dot com</kbd>')
        self.assertNotContains(
            response, 'You must be a member of the club to ride')


class TestAboutPonyView(django.test.TestCase):
    def test_about_pony_get(self):
        """GET request for about RandoPony page works
        """
        response = self.client.get(
            reverse('randopony.register.views.about_pony'))
        self.failUnlessEqual(response.status_code, 200)


    def test_about_pony_sidebar(self):
        """organizer_info view renders expected sidebar
        """
        response = self.client.get(
            reverse('randopony.register.views.about_pony'))
        self.failUnless('Home' in response.content)
        self.failUnless('randonneurs.bc.ca' in response.content)
        self.failUnless('Info for Brevet Organizers' in response.content)
        self.failUnless("What's up with the pony?" in response.content)


class TestOrganizerInfoView(django.test.TestCase):
    def test_organizer_info_get(self):
        """GET request for orgainzers info page works
        """
        response = self.client.get(
            reverse('randopony.register.views.organizer_info'))
        self.failUnlessEqual(response.status_code, 200)


    def test_organizer_info_sidebar(self):
        """organizer_info view renders expected sidebar
        """
        response = self.client.get(
            reverse('randopony.register.views.organizer_info'))
        self.failUnless('Home' in response.content)
        self.failUnless('randonneurs.bc.ca' in response.content)
        self.failUnless('Info for Brevet Organizers' in response.content)
        self.failUnless("What's up with the pony?" in response.content)
