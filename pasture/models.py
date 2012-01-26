"""Model classes for RandoPony pasture app.
"""
# Standard library:
# Django:
from django.db import models


class EmailAddress(models.Model):
    """App level email address model.

    Storage for "static" email addresses in the database instead of in the
    settings module.
    """
    key = models.CharField(max_length=50)
    email = models.EmailField()


    def __unicode__(self):
        return '{0.key} <{0.email}>'.format(self)


class Link(models.Model):
    """Off-site link model.

    Storage for URLs content outside the RandoPony app; e.g. event
    waiver on club site.
    """
    key = models.CharField(max_length=50)
    url = models.URLField()


    def __unicode__(self):
        return self.key
