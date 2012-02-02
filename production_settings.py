"""Django settings for deployment of RandoPony project.
"""
from os import path

project_path = path.dirname(__file__)


DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(project_path, 'randopony-production.db')
    }
}

STATIC_ROOT = path.join(project_path, 'static')
STATIC_URL = 'http://randopony.randonneurs.bc.ca/static/'
ADMIN_MEDIA_PREFIX = 'http://randopony.randonneurs.bc.ca/static/admin/'

EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'randopony'
SERVER_EMAIL = 'randopony@randonneurs.bc.ca'
