"""Model classes for RandoPony site register app

"""
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
    """Base class for event models.
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
    """Non-riding event model.
    """
    EVENT_CHOICES = (
        ( 'AGM',  'AGM'),
        ( 'brunch',  'Brunch'),
        ( 'dinner',  'Dinner'),
        ( 'social',  'Spring Social'),
    )

    event = models.CharField(max_length=30, choices=EVENT_CHOICES)
        

class Rider(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    club_member = models.BooleanField('club member?', default=False)
    info_answer = models.CharField(
        'info answer', max_length=100, blank=True)
    brevet = models.ForeignKey(Brevet)

    def __unicode__(self):
        return self.name

    class Meta():
        ordering = ['name']


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
        model = Rider
        exclude = ('brevet', )


class RiderFormWithoutQualification(BaseRiderForm):
    class Meta:
        model = Rider
        exclude = ('brevet', 'info_answer')
