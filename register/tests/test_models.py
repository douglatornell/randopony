"""Unit test for RandoPony register app models.
"""
from __future__ import absolute_import
# Standard library:
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
import uuid
# Mock:
from mock import patch
# Django:
from django.conf import settings
from django.utils import unittest


class TestBrevet(unittest.TestCase):
    """Unit tests for Brevet model object.
    """
    def _get_target_class(self):
        from ..models import Brevet
        return Brevet


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_unicode(self):
        """__unicode__ returns {region}{event} {date} for brevet
        """
        today = date.today()
        brevet = self._make_one(region='LM', event='200', date=today)
        self.assertEqual(
            unicode(brevet), u'LM200 {0}'.format(today.strftime('%d-%b-%Y')))


    def test_uuid_value(self):
        """uuid property returns URL namespace uuid for brevet
        """
        today = date.today()
        brevet = self._make_one(region='LM', event='200', date=today)
        brevet_uuid = uuid.uuid5(
            uuid.NAMESPACE_URL,
            '/register/LM200{0}'.format(today.strftime('%d%b%Y')))
        self.assertEqual(brevet.uuid, brevet_uuid)


    def test_registration_closed_false_week_before_brevet(self):
        """registration_closed property is False 7 days before brevet
        """
        from .. import models
        brevet = self._make_one(
            region='LM', event='200', date=date(2010, 4, 17))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2010, 4, 10, 11, 0)
            mock_datetime.combine = datetime.combine
            self.assertFalse(brevet.registration_closed)


    def test_registration_closed_true_evening_before_brevet(self):
        """registration_closed property is True evening before brevet
        """
        from .. import models
        brevet = self._make_one(
            region='LM', event='200', date=date(2010, 4, 17))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2010, 4, 16, 20, 0)
            mock_datetime.combine = datetime.combine
            self.assertTrue(brevet.registration_closed)


    def test_registration_closed_true_week_after_brevet(self):
        """registration_closed property is True 7 days after brevet
        """
        from .. import models
        brevet = self._make_one(
            region='LM', event='200', date=date(2010, 4, 17))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2010, 4, 24, 11, 0)
            mock_datetime.combine = datetime.combine
            self.assertTrue(brevet.registration_closed)


    def test_in_past_false_before_brevet(self):
        """in_past property is False before brevet start date
        """
        from .. import models
        brevet = self._make_one(
            region='LM', event='200', date=date(2010, 4, 17))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 1)
            self.assertFalse(brevet.in_past)


    def test_in_past_results_url_week_after_brevet(self):
        """in_past property is results URL on club site 8 days after brevet
        """
        from .. import models
        brevet = self._make_one(
            region='LM', event='200', date=date(2010, 4, 17))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2010, 4, 25)
            self.assertEqual(
                brevet.in_past,
                'http://randonneurs.bc.ca/results/10_times/10_times.html')


    def test_started_false_before_brevet(self):
        """started property is False before brevet start datetime
        """
        from .. import models
        brevet = self._make_one(
            region='LM', event='200', date=date(2010, 4, 17), time=time(7,0))
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2010, 4, 10, 11, 0)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.assertFalse(brevet.started)


    def test_started_true_1_plus_hr_after_start(self):
        """started property is True for > 1 hr after brevet start time
        """
        from .. import models
        brevet = self._make_one(
            region='LM', event='200', date=date(2010, 4, 17), time=time(7,0))
        with patch.object(models, 'datetime') as mock_datetime:
            # Server that hosts randopony is 2 hrs ahead of Pacific time
            mock_datetime.now.return_value = datetime(2010, 4, 17, 10, 1)
            mock_datetime.combine = datetime.combine
            mock_datetime.timedelta = timedelta
            self.assertTrue(brevet.started)


class TestClubEvent(unittest.TestCase):
    """Unit tests for ClubEvent model object.
    """
    def _get_target_class(self):
        from ..models import ClubEvent
        return ClubEvent


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_unicode(self):
        """__unicode__ returns {event} {date} for club event
        """
        today = date.today()
        event = self._make_one(
            region='Club', event='AGM', date=today)
        self.assertEqual(
            unicode(event), u'AGM {0}'.format(today.strftime('%d-%b-%Y')))


    def test_uuid_value(self):
        """uuid property returns URL namespace uuid for event
        """
        today = date.today()
        event = self._make_one(region='Club', event='AGM', date=today)
        event_uuid = uuid.uuid5(
            uuid.NAMESPACE_URL,
            '/register/AGM{0}'.format(today.strftime('%d%b%Y')))
        self.assertEqual(event.uuid, event_uuid)


class TestBrevetRider(unittest.TestCase):
    """Unit tests for BrevetRider model object.
    """
    def _get_target_class(self):
        from ..models import BrevetRider
        return BrevetRider


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_unicode(self):
        """__unicode__ returns {first_name} {last_name} for brevet rider
        """
        rider = self._make_one(
            first_name='Doug', last_name='Latornell')
        self.assertEqual(unicode(rider), u'Doug Latornell')


    def test_full_name(self):
        """full_name property returns {first_name} {last_name} for brevet rider
        """
        rider = self._make_one(
            first_name='Doug', last_name='Latornell')
        self.assertEqual(rider.full_name, u'Doug Latornell')


class TestEventParticipant(unittest.TestCase):
    """Unit tests for EventParticipant model object.
    """
    def _get_target_class(self):
        from ..models import EventParticipant
        return EventParticipant


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_unicode(self):
        """__unicode__ returns {first_name} {last_name} for event participant
        """
        person = self._make_one(
            first_name='Doug', last_name='Latornell')
        self.assertEqual(unicode(person), u'Doug Latornell')


    def test_full_name(self):
        """full_name property returns {first_name} {last_name} for participant
        """
        rider = self._make_one(
            first_name='Doug', last_name='Latornell')
        self.assertEqual(rider.full_name, u'Doug Latornell')


class TestRiderForm(unittest.TestCase):
    """Unit tests for RiderForm pre-registration form.
    """
    def _get_target_class(self):
        from ..models import RiderForm
        return RiderForm


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_form_has_captcha_answer_field(self):
        """pre-registration form has CAPTCHA answer field
        """
        form = self._make_one()
        self.assertIn('captcha', form.fields)


    def test_clean_captcha_correct_answer(self):
        """clean_captcha returns answer & no error messages
        """
        form = self._make_one()
        form.cleaned_data = {
            'captcha': settings.REGISTRATION_FORM_CAPTCHA_ANSWER
        }
        form._errors = {}
        answer = form.clean_captcha()
        self.assertEqual(answer, settings.REGISTRATION_FORM_CAPTCHA_ANSWER)
        self.assertFalse(form._errors)


    def test_clean_captcha_wrong_answer(self):
        """clean_captcha returns expected error message for wrong answer
        """
        form = self._make_one()
        form.cleaned_data = {'captcha': 42}
        form._errors = {}
        answer = form.clean_captcha()
        self.assertEqual(form._errors['captcha'][0], 'Wrong! See hint.')
        self.assertEqual(answer, 42)


    def test_info_answer_reqd(self):
        """pre-registration form requires info_answer field value
        """
        form = self._make_one()
        self.assertTrue(form.fields['info_answer'].required)


    def test_brevet_field_excluded(self):
        """pre-registration form excludes brevet field
        """
        form = self._make_one()
        self.assertNotIn('brevet', form.fields)


class TestRiderFormWithoutInfoQuestion(unittest.TestCase):
    """Unit tests for RiderFormWithoutInfoQuestion pre-registration form.
    """
    def _get_target_class(self):
        from ..models import RiderFormWithoutInfoQuestion
        return RiderFormWithoutInfoQuestion


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_info_answer_field_excluded(self):
        """pre-registration form excludes info_answer field
        """
        form = self._make_one()
        self.assertNotIn('info_answer', form.fields)
