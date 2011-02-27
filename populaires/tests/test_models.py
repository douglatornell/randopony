"""Unit tests for RandoPony populaires app models.

"""
# Standard library:
from datetime import date
from datetime import datetime
from datetime import time
import unittest2 as unittest
import uuid
# Mock:
from mock import patch


class TestPopulaire(unittest.TestCase):
    """Unit tests for Populaire model object.
    """
    def _get_target_class(self):
        from ..models import Populaire
        return Populaire


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_unicode(self):
        """__unicode__ returns {short_name} {date} for brevet
        """
        today = date.today()
        pop = self._make_one(short_name='VicPop', date=today)
        self.assertEqual(
            unicode(pop), u'VicPop {0}'.format(today.strftime('%d-%b-%Y')))

        
    def test_uuid_value(self):
        """uuid property returns URL namespace uuid for populaire
        """
        today = date.today()
        pop = self._make_one(short_name='VicPop', date=today)
        pop_uuid = uuid.uuid5(
            uuid.NAMESPACE_URL,
            '/populaires/VicPop{0}'.format(today.strftime('%d%b%Y')))
        self.assertEqual(pop.uuid, pop_uuid)


    def test_registration_closed_false_before_close_datetime(self):
        """registration_closed property False before closure datetime
        """
        pop = self._make_one(
            short_name='VicPop',
            date=date(2011, 3, 27),
            registration_closes=datetime(2011, 3, 24, 12, 0))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2011, 3, 21, 11, 0)
            self.assertFalse(pop.registration_closed)


    def test_registration_closed_false_after_close_datetime(self):
        """registration_closed property is False after closure datetime
        """
        pop = self._make_one(
            short_name='VicPop',
            date=date(2011, 3, 27),
            registration_closes=datetime(2011, 3, 24, 12, 0))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2011, 3, 25, 13, 0)
            self.assertTrue(pop.registration_closed)


    def test_started_false_before_populaire_start_datetime(self):
        """started property is False before start datetime
        """
        pop = self._make_one(
            short_name='VicPop',
            date=date(2011, 3, 27),
            time=time(10, 0))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2011, 3, 21, 13, 0)
            mock_datetime.combine = datetime.combine
            self.assertFalse(pop.started)


    def test_started_false_after_populaire_start_datetime(self):
        """started property is True after start datetime
        """
        pop = self._make_one(
            short_name='VicPop',
            date=date(2011, 3, 27),
            time=time(10, 0))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2011, 3, 27, 12, 30)
            mock_datetime.combine = datetime.combine
            self.assertTrue(pop.started)


    def test_in_past_false_before_populaire(self):
        """in_past property is False before populaire start date
        """
        pop = self._make_one(
            short_name='VicPop', date=date(2011, 3, 27))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 3, 1)
            self.assertFalse(pop.in_past)


    def test_in_past_results_url_week_after_populaire(self):
        """in_past property is results URL on club site 8 days after populaire
        """
        pop = self._make_one(
            short_name='VicPop', date=date(2011, 3, 27))
        with patch('randopony.populaires.models.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 4, 25)
            self.assertEqual(
                pop.in_past,
                'http://randonneurs.bc.ca/results/11_times/11_times.html')


class TestRider(unittest.TestCase):
    """Unit tests for Rider model object.
    """
    def _get_target_class(self):
        from ..models import Rider
        return Rider


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    
    def test_unicode(self):
        """__unicode__ returns {first_name} {last_name} for rider
        """
        rider = self._make_one(
            first_name='Doug', last_name='Latornell')
        self.assertEqual(unicode(rider), u'Doug Latornell')


    def test_full_name(self):
        """full_name property returns {first_name} {last_name} for rider
        """
        rider = self._make_one(
            first_name='Doug', last_name='Latornell')
        self.assertEqual(rider.full_name, u'Doug Latornell')



