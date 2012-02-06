"""Unit tests for helpers module.

"""
# Django:
import django.test
# RandoPony:
from ..helpers import email2words


class TestHelpers(django.test.TestCase):
    def test_email2words(self):
        """email2words translates email address to words
        """
        self.assertEqual(
            email2words('djl@example.bc.ca'), 'djl at example dot bc dot ca')
