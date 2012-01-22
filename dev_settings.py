"""Django settings for development of RandoPony project.
"""
from os import path

project_path = path.dirname(__file__)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(project_path, 'randopony.db')
    }
}

STATIC_URL = '/static/'

# SMTP server settings
#
# Use the Python standard library SMTP DebuggingServer to handle email
# by printing it to stdout. Run the server with:
#    python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 1025
