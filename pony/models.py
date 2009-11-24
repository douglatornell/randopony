from datetime import date

from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.full_name


    @property
    def full_name(self):
        return ' '.join((self.first_name, self.last_name))


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
        (600, '500 km'),
        (1000, '1000 km'),
        (1200, '1200 km'),
        (2000, '2000 km'),
    )

    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    distance = models.IntegerField(choices=DISTANCE_CHOICES)
    date = models.DateField()


    def __unicode__(self):
        return ('%(year)d %(region)s%(distance)d %(monthday)s'
                % dict(year=self.date.year, region=self.region,
                       distance=self.distance,
                       monthday=self.date.strftime('%b%d')))


class Result(models.Model):
    brevet = models.ForeignKey(Brevet)
    rider = models.ForeignKey(Member)
    time = models.CharField(max_length=6)
