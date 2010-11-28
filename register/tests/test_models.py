"""Unit test for RandoPony register app models.

"""
# Standard library:
import unittest
from datetime import date


class TestBaseEvent(unittest.TestCase):
    """Unit tests for BaseEvent model object.
    """
    def _get_target_class(self):
        from randopony.register.models import BaseEvent
        return BaseEvent


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_club_event_unicode(self):
        """__unicode__ returns {event} {date} for club events
        """
        today = date.today()
        event = self._make_one(
            region='Club', event='AGM', date=today)
        self.assertEqual(
            unicode(event), u'AGM {0}'.format(today.strftime('%d-%b-%Y')))


    def test_riding_event_unicode(self):
        """__unicode__ returns {region}{event} {date} for riding events
        """
        today = date.today()
        event = self._make_one(
            region='LM', event='200', date=today)
        self.assertEqual(
            unicode(event), u'LM200 {0}'.format(today.strftime('%d-%b-%Y')))
