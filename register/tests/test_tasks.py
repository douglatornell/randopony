"""Asynchronous (celeryd) task tests for RandoPony register app.
"""
# Standard library:
from datetime import date
# Django:
import django.test
from django.conf import settings
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

    def test_email_to(self):
        """email to rider has correct to address
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].to, ['djl@douglatornell.ca'])

    def test_email_from(self):
        """email to rider has correct from address
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].from_email, 'randopony@randonneurs.bc.ca')

    def test_email_sender(self):
        """email to rider has correct sender address header
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].extra_headers['Sender'],
            'randopony@randonneurs.bc.ca')

    def test_email_reply_to(self):
        """email to rider has correct reply-to address header
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].extra_headers['Reply-To'], 'djl@douglatornell.ca')

    def test_email_reply_to_2_organizers(self):
        """email to rider has 2 organizers in reply-to header
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='VI', event=600, date=date(2010, 8, 7))
        rider = BrevetRider.objects.get(
            first_name='Ken', last_name='Bonner', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].extra_headers['Reply-To'],
            'mcroy@example.com, dug.andrusiek@example.com')

    def test_email_confirm_brevet_registration_msg(self):
        """email to rider has correct brevet pre-registration confirmation msg
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'pre-registered for the BC Randonneurs LM400 22-May-2010 brevet',
            mail.outbox[0].body)

    def test_email_brevet_url(self):
        """email to rider has correct brevet page url
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            '<http://testserver/register/LM400/22May2010/>',
            mail.outbox[0].body)

    def test_email_event_waiver_msg(self):
        """email to rider has correct event waiver message
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'print out the event waiver form',
            mail.outbox[0].body)

    def test_email_event_waiver_url(self):
        """email to rider has correct event waiver url
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            '<http://www.randonneurs.bc.ca/organize/eventform.pdf>',
            mail.outbox[0].body)

    def test_email_organizer_contact_msg(self):
        """email to rider has correct "reply to contact organizer" msg
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'auto-generated email, but you can reply to it '
            'to contact the brevet organizer',
            mail.outbox[0].body)

    def test_email_non_member_msg(self):
        """email to rider has correct non-member message
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=200, date=date(2012, 3, 17))
        rider = BrevetRider.objects.get(
            first_name='Fibber', last_name='McGee', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'indicated that you are NOT a member',
            mail.outbox[0].body)

    def test_email_membership_form_url(self):
        """email to rider has correct membership form & waiver url
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=200, date=date(2012, 3, 17))
        rider = BrevetRider.objects.get(
            first_name='Fibber', last_name='McGee', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            '<http://www.randonneurs.bc.ca/organize/'
            '2012_membership-and-waiver.pdf>',
            mail.outbox[0].body)


class TestEmailToOrganizer(django.test.TestCase):
    """Unit tests for email_to_organizer task function.
    """
    fixtures = ['brevets.yaml', 'riders.yaml',
                'email_addresses.yaml', 'links.yaml']

    def _get_target_function(self):
        from ..tasks import email_to_organizer
        return email_to_organizer

    def _send_one(self, *args, **kwargs):
        self._get_target_function()(*args, **kwargs)

    def test_email_subject(self):
        """email to organizer has correct subject
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
            'Doug Latornell has Pre-registered for the LM400 22-May-2010')

    def test_email_to(self):
        """email to organizer has correct to address
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].to, ['djl@douglatornell.ca'])

    def test_email_to_2_organizers(self):
        """email to organizer goes to multiple organizers
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='VI', event=600, date=date(2010, 8, 7))
        rider = BrevetRider.objects.get(
            first_name='Ken', last_name='Bonner', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].to,
            'mcroy@example.com dug.andrusiek@example.com'.split())

    def test_email_from(self):
        """email to organizer has correct from address
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].from_email, 'randopony@randonneurs.bc.ca')

    def test_email_confirm_brevet_registration_msg(self):
        """email to organizer has correct pre-registration confirmation msg
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'Doug Latornell <djl@douglatornell.ca> has pre-registered for the '
            'LM400 22-May-2010 brevet',
            mail.outbox[0].body)

    def test_email_is_club_member_msg(self):
        """email to organizer has correct club membership true msg
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'has indicated that zhe is a club member', mail.outbox[0].body)

    def test_email_non_member_msg(self):
        """email to organizer has correct non-member message
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=200, date=date(2012, 3, 17))
        rider = BrevetRider.objects.get(
            first_name='Fibber', last_name='McGee', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'has indicated that zhe is NOT a club member',
            mail.outbox[0].body)

    def test_email_member_before_start_msg(self):
        """email to organizer has msg re: joining club before brevet start
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=200, date=date(2012, 3, 17))
        rider = BrevetRider.objects.get(
            first_name='Fibber', last_name='McGee', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'join beforehand, or at the start', mail.outbox[0].body)

    def test_email_qualifying_info(self):
        """email to organizer has answer to qualifying info question
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'LM300 1-May-2010', mail.outbox[0].body)

    def test_email_admin_contact_msg(self):
        """email to organizer has correct admin contact email address msg
        """
        from ..models import Brevet
        from ..models import BrevetRider
        brevet = Brevet.objects.get(
            region='LM', event=400, date=date(2010, 5, 22))
        rider = BrevetRider.objects.get(
            first_name='Doug', last_name='Latornell', brevet=brevet)
        self._send_one(brevet.pk, rider.pk, 'testserver')
        self.assertIn(
            'please send email to <{0}>'.format(settings.ADMINS[0][1]),
            mail.outbox[0].body)
