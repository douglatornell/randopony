"""Unit test for RandoPony pasture app models.
"""
# Django:
from django.utils import unittest


class TestEmailAddress(unittest.TestCase):
    """Unit tests for EmailAddress model object.
    """
    def _get_target_calss(self):
        from ..models import EmailAddress
        return EmailAddress


    def _make_one(self, *args, **kwargs):
        return self._get_target_calss()(*args, **kwargs)


    def test_unicode(self):
        """__unicode__ returns "key <email_address>" for EmailAddress
        """
        email_address = self._make_one(key='webmaster', email='webmaster@example.com')
        self.assertEqual(unicode(email_address), 'webmaster <webmaster@example.com>')
