"""Admin configuration for RandoPony pasture app.
"""
from __future__ import absolute_import
# Django:
from django.contrib import admin
# RandoPony:
from .models import EmailAddress
from .models import Link


admin.site.register(EmailAddress)
admin.site.register(Link)
