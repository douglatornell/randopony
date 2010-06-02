"""Model classes for RandoPony site register app

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-05
"""
from django import forms
from django.conf import settings
from django.db import models
from django.forms.util import ErrorList


class Brevet(models.Model):
    REGION_CHOICES = (
        ('LM', 'Lower Mainland'),
        ('PR', 'Peace Region'),
        ('SI', 'Southern Interior'),
        ('VI', 'Vancouver Island'),
    )
    DISTANCE_CHOICES = (
        (200, '200 km'),
        (300, '300 km'),
        (400, '400 km'),
        (600, '600 km'),
        (1000, '1000 km'),
        (1200, '1200 km'),
        (2000, '2000 km'),
    )

    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    distance = models.IntegerField(choices=DISTANCE_CHOICES)
    date = models.DateField()
    route_name = models.CharField(max_length=100)
    start_location = models.CharField(max_length=100)
    start_time = models.TimeField()
    alt_start_time = models.TimeField('alternate start time', blank=True, null=True)
    organizer_email = models.EmailField()
    info_question = models.TextField(
        "brevet info question", blank=True,
        help_text='Optional question that will appear on the '
                  'pre-registration form')

    def __unicode__(self):
        return ('%(region)s%(distance)d %(date)s'
                % dict(region=self.region,
                       distance=self.distance,
                       date=self.date.strftime('%d-%b-%Y')))

    class Meta():
        ordering = ['date']


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
