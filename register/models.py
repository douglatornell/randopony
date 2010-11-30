"""Model classes for RandoPony site register app

"""
# Standard library:
import uuid
# Django:
from django import forms
from django.conf import settings
from django.db import models
from django.forms.util import ErrorList


REGIONS = dict(
    Club='Club Events',
    LM='Lower Mainland',
    PR='Peace Region',
    SI='Southern Interior',
    SW='Super Week',
    VI='Vancouver Island'
)


class BaseEvent(models.Model):
    """Abstract base class for Brevet and ClubEvent models.
    """
    REGION_CHOICES = [
        (key, REGIONS[key]) for key in sorted(REGIONS.keys())
    ]
    
    class Meta():
        abstract = True
        ordering = ['date']

    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    date = models.DateField()
    location = models.CharField(max_length=100)
    time = models.TimeField()
    organizer_email = models.CharField(
        max_length=100,
        help_text='Use commas to separate multiple email addresses')
    info_question = models.TextField(
        "event info question", blank=True,
        help_text='Optional question that will appear on the '
                  'pre-registration form')


    def __unicode__(self):
        event_id = '{region}{event} {date}'.format(
            region='' if self.region == 'Club' else self.region,
            event=self.event,
            date=self.date.strftime('%d-%b-%Y'))
        return event_id


    def _get_uuid(self):
        """Return the URL namespace uuid for the event.
        """
        return uuid.uuid5(uuid.NAMESPACE_URL, self.get_absolute_url())
    uuid = property(_get_uuid)


    def get_absolute_url(self):
        url_id = '{region}{event}{date}'.format(
            region='' if self.region == 'Club' else self.region,
            event=self.event,
            date=self.date.strftime('%d%b%Y'))
        return '/register/{0}'.format(url_id)


class Brevet(BaseEvent):
    """Brevet event model.
    """
    EVENT_CHOICES = (
        ( '200',  '200 km'),
        ( '300',  '300 km'),
        ( '400',  '400 km'),
        ( '600',  '600 km'),
        ('1000', '1000 km'),
    )

    event = models.CharField(max_length=30, choices=EVENT_CHOICES)
    route_name = models.CharField(max_length=100)
    alt_start_time = models.TimeField(
        'alternate start time', blank=True, null=True)


class ClubEvent(BaseEvent):
    """Non-brevet club event model.
    """
    EVENT_CHOICES = (
        ( 'AGM',  'AGM'),
        ( 'brunch',  'Brunch'),
        ( 'dinner',  'Dinner'),
        ( 'social',  'Spring Social'),
    )

    event = models.CharField(max_length=30, choices=EVENT_CHOICES)


class Person(models.Model):
    """Abstract base class for BrevetRider and EventParticipant models.
    """
    class Meta():
        abstract = True
        ordering = ['last_name']

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    info_answer = models.CharField(
        'info answer', max_length=100, blank=True)

    def __unicode__(self):
        return self.full_name


    def _get_full_name(self):
        """Return the person's full name.
        """
        return '{0} {1}'.format(self.first_name, self.last_name)
    full_name = property(_get_full_name)
        

class BrevetRider(Person):
    """Brevet rider model for people who have pre-registered to ride
    in a brevet.
    """
    club_member = models.BooleanField('club member?', default=False)
    brevet = models.ForeignKey(Brevet)
        

class EventParticipant(Person):
    """Event participant model for people who have pre-registered for
    a non-brevet club event.
    """
    event = models.ForeignKey(ClubEvent)


class BaseRiderForm(forms.ModelForm):
    """Base class for rider pre-registration ModelForms.

    Adds CAPTCHA answer field and its validator to the form.
    """
    captcha = forms.IntegerField()

    def clean_captcha(self):
        """Validate the CAPTCHA answer.
        """
        answer = self.cleaned_data['captcha']
        if answer != settings.REGISTRATION_FORM_CAPTCHA_ANSWER:
            self._errors['captcha'] = ErrorList(['Wrong! See hint.'])
        return answer


class RiderForm(BaseRiderForm):
    """Rider pre-registration from for a brevet that requires qualifying info.
    """
    def __init__(self, *args, **kwargs):
        """Make qualifying info a required field.
        """
        super(RiderForm, self).__init__(*args, **kwargs)
        self.fields['info_answer'].required = True


    class Meta:
        model = BrevetRider
        exclude = ('brevet', )


class RiderFormWithoutQualification(BaseRiderForm):
    class Meta:
        model = BrevetRider
        exclude = ('brevet', 'info_answer')
