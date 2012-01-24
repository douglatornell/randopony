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
    email = models.CharField(max_length=100)


    def __unicode__(self):
        return '{0.key} <{0.email}>'.format(self)
