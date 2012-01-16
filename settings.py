"""Django settings for RandoPony project.
"""
from os import path

project_path = path.dirname(__file__)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Doug Latornell', 'djl@douglatornell.ca'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(project_path, 'randopony.db')

    }
}

TIME_ZONE = 'America/Vancouver'

LANGUAGE_CODE = 'en-ca'

SITE_ID = 1

USE_I18N = False

STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

SECRET_KEY = open(path.join(project_path, '.secret_key'), 'r').read()

ROOT_URLCONF = 'randopony.urls'

STATICFILES_DIRS = (
    # Always use absolute paths.
    path.join(project_path, 'site_static'),
)

TEMPLATE_DIRS = (
    # Always use absolute paths.
    path.join(project_path, 'site_templates'),
    path.join(project_path, 'admin_templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'south',
    'randopony.pasture',
    'randopony.register',
    'randopony.populaires',
)

# Application-specific settings:

# CAPTCHA question and answer for brevet pre-registration
REGISTRATION_FORM_CAPTCHA_QUESTION = (
    'Are you a human? Are you a randonneur? Please prove it. '
    'A Super Randonneur series consists of brevets of '
    '200 km, 300 km, ___ km, and 600 km. Fill in the blank:'
)
REGISTRATION_FORM_CAPTCHA_ANSWER = 400

# Email from address for messages from registration form handler to
# brevet organizer
REGISTRATION_EMAIL_FROM = 'randopony@sadahome.ca'

# Email address of club webmaster for pre-registration page setup
# messages from admin
WEBMASTER_EMAIL = 'eric_fergusson@telus.net'

# SMTP server settings
#
# Use the Python standard library SMTP DebuggingServer to handle email
# by printing it to stdout. Run the server with:
#    python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 1025

# Google Docs settings
GOOGLE_DOCS_EMAIL = 'randopony@sadahome.ca'
GOOGLE_DOCS_PASSWORD = open(
    path.join(project_path, '.google_docs_password'), 'r').read()
