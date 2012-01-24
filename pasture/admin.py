"""Admin configuration for RandoPony pasture app.
"""
from __future__ import absolute_import
# Django:
from django.contrib import admin
# RandoPony:
from .models import EmailAddress


admin.site.register(EmailAddress)
