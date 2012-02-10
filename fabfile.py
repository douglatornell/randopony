"""Fabric tasks for deployment of RandoPony web app.
"""
# Standard library:
import os
# Fabric:
from fabric.api import cd
from fabric.api import env
from fabric.api import get
from fabric.api import local
from fabric.api import lcd
from fabric.api import run
from fabric.api import task
from fabric.contrib.project import rsync_project


env.user = 'bcrandonneur'
env.hosts = ['bcrandonneur.webfactional.com']
app_name = 'randopony'
app_dir = '/home/{0}/webapps/{1}2012'.format(env.user, app_name)
app_database = 'randopony-production.db'


@task(default=True)
def deploy():
    """Deploy app to webfaction
    """
    deploy_code()
    collect_static()
    restart_apache()


@task
def deploy_code():
    """rsync project code to webfaction
    """
    exclusions = (
        'dev_settings.py '
        'fabfile.py '
        'htmlcov '
        'manage.py '
        'requirements* '
        '.DS_Store '
        '.hg* '
        '*.db '
        '*.pyc '
        '*~ '
        .split())
    rsync_project(remote_dir=app_dir, exclude=exclusions, delete=True)


@task
def collect_static():
    """Collect static files on webfaction
    """
    with cd(app_dir):
        run('bin/django-admin.py collectstatic -v0 --noinput '
            '--pythonpath="{0}" --settings={1}.settings'
            .format(app_dir, app_name))


@task
def restart_apache():
    """Restart Apache2 on webfaction
    """
    with cd(os.path.join(app_dir, 'apache2/bin')):
        run('./restart')


@task
def start_supervisord():
    """Start supervisord on webfaction
    """
    with cd(os.path.join(app_dir, app_name)):
        run('../bin/supervisord')


@task
def restart_supervisord():
    """Restart supervisord on webfaction
    """
    with cd(os.path.join(app_dir, app_name)):
        run('kill -HUP `cat supervisord.pid`')


@task
def tail_supervisord_log():
    """Tail supervisord log on webfaction
    """
    with cd('logs/user'):
        run('tail randopony_supervisord.log')


@task
def tail_celeryd_log():
    """Tail celeryd log on webfaction
    """
    with cd('logs/user'):
        run('tail randopony_celeryd.log')


@task
def backup_db():
    """Make backup copy of database on webfaction
    """
    with cd(os.path.join(app_dir, app_name)):
        run('cp {0} ~/{0}-backup'.format(app_database))


@task
def pull_db():
    """Pull copy of database from webfaction
    """
    with cd(os.path.join(app_dir, app_name)):
        get(app_database, './')


@task
def build_docs():
    """Build docs locally
    """
    with lcd('docs'):
        local('make html')


@task
def clean_docs():
    """Delete local docs HTML files
    """
    local('rm -rf docs/_build')


@task
def deploy_docs():
    """rsync rendered docs to webfaction
    """
    rsync_project(
        local_dir='docs/_build/html',
        remote_dir=os.path.join(app_dir, app_name, 'docs/_build/'),
        delete=True)


@task
def coverage_report():
    """Run test suite & report on coverage
    """
    omit_files = (
        'dev_settings.py,fabfile.py,manage.py,private_settings.py,'
        'production_settings.py,settings.py'
        )
    env.warn_only = True
    local('coverage run --source . manage.py test')
    local('coverage report --omit "{0}"'.format(omit_files))
    local('coverage html --omit "{0}"'.format(omit_files))
