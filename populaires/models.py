""" Model classes for RandoPony populaires app.

"""
# Standard library:
from datetime import datetime
from datetime import timedelta
import uuid
# Django:
from django import forms
from django.db import models
from django.forms.util import ErrorList


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


class Rider(models.Model):
    """Rider model for people who have pre-registered to ride a
    populaire.
    """
    class Meta:
        ordering = ['last_name']
        
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    distance = models.IntegerField()
    populaire = models.ForeignKey(Populaire)

    def __unicode__(self):
        return self.full_name


    def _get_full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)
    full_name = property(_get_full_name)


class RiderForm(forms.ModelForm):
    """Rider pre-registration form.
    """
    def __init__(self, *args, **kwargs):
        distance_choices = kwargs.pop('distance_choices')
        super(RiderForm, self).__init__(*args, **kwargs)
        self.fields['distance'].widget = forms.RadioSelect(
            choices=distance_choices)
        self.fields['distance'].error_messages={
            'required': 'Please choose a distance'}

    class Meta:
        model = Rider
        exclude = ('populaire', )

    captcha = forms.IntegerField()


    def clean_captcha(self):
        """Validate the CAPTCHA answer.
        """
        answer = self.cleaned_data['captcha']
        if answer != 2:
            self._errors['captcha'] = ErrorList(['Wrong!'])
        return answer
