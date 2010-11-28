"""Unit test for RandoPony register app models.

"""
# Standard library:
import unittest
from datetime import date


class TestBrevet(unittest.TestCase):
    """Unit tests for Brevet model object.
    """
    def _get_target_class(self):
        from randopony.register.models import Brevet
        return Brevet


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_unicode(self):
        """__unicode__ returns {region}{event} {date} for brevets
        """
        today = date.today()
        event = self._make_one(
            region='LM', event='200', date=today)
        self.assertEqual(
            unicode(event), u'LM200 {0}'.format(today.strftime('%d-%b-%Y')))


class TestClubEvent(unittest.TestCase):
    """Unit tests for ClubEvent model object.
    """
    def _get_target_class(self):
        from randopony.register.models import ClubEvent
        return ClubEvent


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_unicode(self):
        """__unicode__ returns {event} {date} for club events
        """
        today = date.today()
        event = self._make_one(
            region='Club', event='AGM', date=today)
        self.assertEqual(
            unicode(event), u'AGM {0}'.format(today.strftime('%d-%b-%Y')))
