"""Django settings for WebFaction deployment of RandoPony site.

"""
from os import path


project_path = path.dirname(__file__)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Doug Latornell', 'djl@douglatornell.ca'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
# Use a different database file name from what's in the development
# settings module to avoid nasty surprises if the --delete-excluded
# option is used in rsync2wf.sh
DATABASE_NAME = path.join(project_path, 'randopony-production.db')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Vancouver'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-ca'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
MEDIA_ROOT = path.join(project_path, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://randopony.sadahome.ca/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://randopony.sadahome.ca/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = open(path.join(project_path, '.secret_key'), 'r').read()

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'randopony.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(project_path, 'media/templates'),
    path.join(project_path, 'media/register/templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'south',
    'randopony.register',
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
EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'randopony'
EMAIL_HOST_PASSWORD = open(
    path.join(project_path, '.email_host_password'), 'r').read()

# Google Docs settings
GOOGLE_DOCS_EMAIL = 'randopony@sadahome.ca'
GOOGLE_DOCS_PASSWORD = open(
    path.join(project_path, '.google_docs_password'), 'r').read()
