"""Asynchronous (celeryd) task tests for RandoPony register app.
"""
# Standard library:
from datetime import date
# Django:
import django.test
from django.core import mail


class TestEmailToRider(django.test.TestCase):
    """Unit tests for email_to_rider task function.
    """
    fixtures = ['brevets.yaml', 'riders.yaml',
                'email_addresses.yaml', 'links.yaml']

    def _get_target_function(self):
        from ..tasks import email_to_rider
        return email_to_rider

    def _send_one(self, *args, **kwargs):
        self._get_target_function()(*args, **kwargs)

    def test_email_subject(self):
        """email to rider has correct subject
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].subject,
            'Pre-registration Confirmation for LM400 22-May-2010 Brevet')
