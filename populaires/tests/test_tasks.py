"""Asynchronous (celeryd) task tests for RandoPony populaires app.
"""
# Django:
import django.test
from django.conf import settings
from django.core import mail


class TestEmailToRider(django.test.TestCase):
    """Unit tests for email_to_rider task function.
    """
    fixtures = ['populaires.yaml', 'riders.yaml', 'email_addresses.yaml']

    def _get_target_function(self):
        from ..tasks import email_to_rider
        return email_to_rider

    def _send_one(self, *args, **kwargs):
        self._get_target_function()(*args, **kwargs)

    def test_email_subject(self):
        """email to rider has correct subject
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].subject,
            'Pre-registration Confirmation for VicPop 27-Mar-2011')

    def test_email_to(self):
        """email to rider has correct to address
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].to, ['mjanson@example.com'])

    def test_email_from(self):
        """email to rider has correct from address
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].from_email, 'randopony@randonneurs.bc.ca')

    def test_email_sender(self):
        """email to rider has correct sender address header
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].extra_headers['Sender'],
            'randopony@randonneurs.bc.ca')

    def test_email_reply_to(self):
        """email to rider has correct reply-to address header
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].extra_headers['Reply-To'], 'mjansson@example.com')

    def test_email_reply_to_2_organizers(self):
        """email to rider has 2 organizers in reply-to header
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='CanadaDay')
        rider = Rider.objects.get(
            first_name='Susan', last_name='Barr', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].extra_headers['Reply-To'],
            'aliholt@example.com, rogerholt@example.com')

    def test_email_confirm_populaire_registration_msg(self):
        """email to rider has correct populaire pre-reg confirmation msg
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            'pre-registered for the BC Randonneurs '
            'Victoria Populaire on March 27, 2011.',
            mail.outbox[0].body)

    def test_email_populaire_url(self):
        """email to rider has correct populaire page url
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            '<http://testserver/populaires/VicPop/27Mar2011/>',
            mail.outbox[0].body)

    def test_email_organizer_contact_msg(self):
        """email to rider has correct "reply to contact organizer" msg
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            'auto-generated email, but you can reply to it '
            'to contact the populaire organizer(s).',
            mail.outbox[0].body)

    def test_email_event_waiver_msg(self):
        """email to rider has event waiver message when there is a specific one
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            'print out the event waiver form from the club web site',
            mail.outbox[0].body)

    def test_email_no_event_waiver_msg(self):
        """email to rider has no event waiver message when no specific one
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='NanPop')
        rider = Rider.objects.get(
            first_name='Ryder', last_name='Hesjedal', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertNotIn(
            'print out the event waiver form from the club web site',
            mail.outbox[0].body)

    def test_email_event_waiver_url(self):
        """email to rider has correct event waiver url
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            '<http://www.randonneurs.bc.ca/VicPop/VicPop11_registration.pdf>',
            mail.outbox[0].body)


class TestEmailToOrganizer(django.test.TestCase):
    """Unit tests for email_to_organizer task function.
    """
    fixtures = ['populaires.yaml', 'riders.yaml', 'email_addresses.yaml']

    def _get_target_function(self):
        from ..tasks import email_to_organizer
        return email_to_organizer

    def _send_one(self, *args, **kwargs):
        self._get_target_function()(*args, **kwargs)

    def test_email_subject(self):
        """email to organizer has correct subject
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].subject,
            'Mikael Janson has Pre-registered for the VicPop 27-Mar-2011')

    def test_email_to(self):
        """email to organizer has correct to address
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].to, ['mjansson@example.com'])

    def test_email_to_2_organizers(self):
        """email to organizer goes to multiple organizers
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='CanadaDay')
        rider = Rider.objects.get(
            first_name='Susan', last_name='Barr', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].to,
            'aliholt@example.com rogerholt@example.com'.split())

    def test_email_from(self):
        """email to organizer has correct from address
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertEqual(
            mail.outbox[0].from_email, 'randopony@randonneurs.bc.ca')

    def test_email_confirm_organizer_registration_msg(self):
        """email to organizer has correct pre-registration confirmation msg
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            'Mikael Janson <mjanson@example.com> has pre-registered for the '
            'VicPop.',
            mail.outbox[0].body)

    def test_email_populaire_url(self):
        """email to organizer has correct populaire page url
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            '<http://testserver/populaires/VicPop/27Mar2011/>',
            mail.outbox[0].body)

    def test_email_rider_list_spreadsheet_url(self):
        """email to organizer has correct rider list spreadsheet url
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            'https://spreadsheets.google.com/ccc?key=foo',
            mail.outbox[0].body)

    def test_email_distance_selected(self):
        """email to organizer has correct distance selected by rider
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            'Mikael Janson has indicated that zhe is planning to ride the '
            '100 km distance.',
            mail.outbox[0].body)

    def test_email_single_distance_populaire(self):
        """email to organizer lacks distance msg for single distance populaire
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='NewYearsPop')
        rider = Rider.objects.get(
            first_name='Mike', last_name='Croy', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertNotIn(
            'Mike Croy has indicated that zhe is planning to ride the '
            '100 km distance.',
            mail.outbox[0].body)

    def test_email_admin_contact_msg(self):
        """email to organizer has correct admin contact email address msg
        """
        from ..models import Populaire
        from ..models import Rider
        populaire = Populaire.objects.get(short_name='VicPop')
        rider = Rider.objects.get(
            first_name='Mikael', last_name='Janson', populaire=populaire)
        self._send_one(populaire.pk, rider.pk, 'testserver')
        self.assertIn(
            'This is an auto-generated email. If you are having problems with '
            'the RandoPony system please send email to '
            '<{0}>.'.format(settings.ADMINS[0][1]),
            mail.outbox[0].body)
