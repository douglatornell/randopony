"""Django settings for RandoPony project.
"""
# Standard library:
import os
import sys
# Django-Celery:
import djcelery


project_path = os.path.dirname(__file__)
if project_path not in sys.path:
    sys.path.append(project_path)

djcelery.setup_loader()
BROKER_URL = 'django://'

ADMINS = (
    ('Doug Latornell', 'djl@douglatornell.ca'),
)

MANAGERS = ADMINS

TIME_ZONE = 'America/Vancouver'

LANGUAGE_CODE = 'en-ca'

SITE_ID = 1

USE_I18N = False

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
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'randopony.urls'

STATICFILES_DIRS = (
    # Always use absolute paths.
    os.path.join(project_path, 'site_static'),
)

TEMPLATE_DIRS = (
    # Always use absolute paths.
    os.path.join(project_path, 'site_templates'),
    os.path.join(project_path, 'admin_templates'),
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
    'djkombu',
    'djcelery',
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

# Settings that differ between development and production environments
try:
    from dev_settings import DEBUG
    from dev_settings import TEMPLATE_DEBUG
    from dev_settings import DATABASES
    from dev_settings import STATIC_URL
    # Use the Python standard library SMTP DebuggingServer to handle email
    # by printing it to stdout. Run the server with:
    #    python -m smtpd -n -c DebuggingServer <EMAIL_HOST>:<EMAIL_PORT>
    from dev_settings import EMAIL_HOST
    from dev_settings import EMAIL_PORT
except ImportError:
    from production_settings import DEBUG
    from production_settings import DATABASES
    from production_settings import STATIC_ROOT
    from production_settings import STATIC_URL
    from production_settings import ADMIN_MEDIA_PREFIX
    from production_settings import EMAIL_HOST
    from production_settings import EMAIL_HOST_USER

# Settings that should be kept secret:
from private_settings import SECRET_KEY
from private_settings import GOOGLE_DOCS_PASSWORD
from private_settings import EMAIL_HOST_PASSWORD
