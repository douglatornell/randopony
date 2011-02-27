""" Model classes for RandoPony populaires app.

"""
# Standard library:
from datetime import datetime
from datetime import timedelta
import uuid
# Django:
from django.db import models


# The webfaction server hosting randopony is 2 hours ahead of Pacific
# time.
SERVER_TZ_OFFSET = 2


class Populaire(models.Model):
    """Populaire event model.
    """
    class Meta:
        ordering = ['date']

        
    event_name = models.CharField(max_length=100)
    short_name = models.CharField(
        max_length=20,
        help_text='For use in URLs and sidebar; e.g. VicPop')
    distance = models.CharField(
        max_length=100,
        help_text='Separate multiple distance with commas; e.g. 50 km, 100 km')
    date = models.DateField()
    location = models.CharField('start location', max_length=100)
    time = models.TimeField('start time')
    organizer_email = models.CharField(
        max_length=100,
        help_text='Use commas to separate multiple email addresses')
    registration_closes = models.DateTimeField()
    entry_form_url = models.CharField(
        max_length=200,
        help_text='Full URL of entry form PDF;<br/> e.g. '
                  'http://www.randonneurs.bc.ca/VicPop/VicPop11_registration.pdf')
    entry_form_url_label = models.CharField(
        max_length=30,
        default='Entry Form (PDF)')
    google_doc_id = models.CharField(max_length=200)


    def __unicode__(self):
        return '{short_name} {date}'.format(
            short_name=self.short_name,
            date=self.date.strftime('%d-%b-%Y'))

    
    def _get_uuid(self):
        """Return the URL namespace uuid for the event.
        """
        return uuid.uuid5(uuid.NAMESPACE_URL, self.get_absolute_url())
    uuid = property(_get_uuid)


    def get_absolute_url(self):
        url_id = '{short_name}{date}'.format(
            short_name=self.short_name,
            date=self.date.strftime('%d%b%Y'))
        return '/populaires/{0}'.format(url_id)



    def _registration_closed(self):
        """Has registration for the populaire closed?
        """
        closure_datetime = (
            self.registration_closes + timedelta(hours=SERVER_TZ_OFFSET))
        return datetime.now() > closure_datetime
    registration_closed = property(_registration_closed)


    def _started(self):
        """Has populaire started?
        """
        start_datetime = (datetime.combine(self.date, self.time)
                          + timedelta(hours=SERVER_TZ_OFFSET))
        return datetime.now() > start_datetime
    started = property(_started)


    def _in_past(self):
        """Return a link to the year's results on the club site for
        populaires more than 7 days in the past, otherwise False.
        """
        results_url = False
        today = datetime.today().date()
        seven_days = timedelta(days=7)
        if self.date < today - seven_days:
            results_url = (
                'http://randonneurs.bc.ca/results/{0}_times/{0}_times.html'
                .format(str(self.date.year)[-2:]))
        return results_url
    in_past = property(_in_past)
