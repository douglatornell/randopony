"""Unit test for RandoPony register app models.

"""
# Standard library:
from datetime import date
import unittest2 as unittest
import uuid


class TestBrevet(unittest.TestCase):
    """Unit tests for Brevet model object.
    """
    def _get_target_class(self):
        from randopony.register.models import Brevet
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


class TestClubEvent(unittest.TestCase):
    """Unit tests for ClubEvent model object.
    """
    def _get_target_class(self):
        from randopony.register.models import ClubEvent
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
        from randopony.register.models import BrevetRider
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
        from randopony.register.models import EventParticipant
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
