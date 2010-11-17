"""Unit tests for helpers module.

"""
# Python 2.6 with future features:
from __future__ import absolute_import
# Django:
import django.test
# Application:
import register.helpers as h


class TestHelpers(django.test.TestCase):
    def test_email2words(self):
        """email2words translates email address to words
        """
        self.assertEqual(
            h.email2words('djl@example.bc.ca'), 'djl at example dot bc dot ca')
