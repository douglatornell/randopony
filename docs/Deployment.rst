=====================================
Deployment of RandoPony on WebFaction
=====================================

:Author: Doug Latornell
:Created: 2009-12-27
:Revised: 2012-02-07


These notes describe the process of deploying RandoPony on the
WebFaction_ shared hosting service. Specifically, what is described is
a deployment under the :kbd:`randonneurs.bc.ca` domain, but it
shouldn't be hard to extrapolate from these notes to deploy under
another domain.

.. _WebFaction: http://webfaction.com

The canonical reference at the time of writing is the `Django section`_
of the `WebFaction Software Documentation`_.

.. _Django section: http://docs.webfaction.com/software/django/index.html
.. _WebFaction Software Documentation: http://docs.webfaction.com/software/index.html


Create the Django and Static Media Applications
===============================================

#. Log into the WebFaction control panel.
#. Use the :guilabel:`Domains / websites > Applications` menu to
    create a :kbd:`Django 1.3.1 (mod_wsgi 3.3/Python 2.7)` application
    called :kbd:`randopony`.

To reduce memory consumption (the primary resource limitation and
package cost differentiator on WebFaction), and improve performance of
the app, create static applications to serve media files (CSS, images,
JavaScript, etc.) for RandoPony and the Django admin:

#. Use the :guilabel:`Domains / websites > Applications` menu to
   create a :kbd:`Symbolic link to static/cgi/php53 app` application
   called :kbd:`randopony_static` that links to
   :kbd:`/home/bcrandonneur/webapps/randopony/randopony/media` (this is
   the value to enter in the :guilabel:`Extra Info:` field.
#. Also, create a :kbd:`Symbolic link to static/cgi/php53 app`
   application called :kbd:`randopony_docs` that links to
   :kbd:`/home/bcrandonneur/webapps/randopony/randopony/docs/_build/html`


Create the :kbd:`randopony` Subdomain
=====================================

Create a subdomain from which the randopony app will be served:

#. Use the :guilabel:`Domains / websites > Domains` menu to add a
   :kbd:`randopony` subdomain prefix to the :kbd:`randonneurs.bc.ca`
   domain.


Create the Website Entry
========================

Configure WebFaction to proxy requests to the Django app, static, and
docs apps:

#. Use the :guilabel:`Domains / websites > Websites` menu to create a
   site called :kbd: `randopony` connected to the
   :kbd:`randopony.randonneurs.bc.ca` subdomain, with the following
   site apps added to it:

   * :kbd:`randopony` mounted at :kbd:`/`
   * :kbd:`randopony_static` mounted at :kbd:`/static`
   * :kbd:`randopony_docs` mounted at :kbd:`/docs`


Install the Packages that RandoPony Depends On
==============================================

#. :command:`ssh` into :kbd:`webfaction.com`.

#. Put the :kbd:`randopony` Python library directory on the
   :envvar:`PYTHONPATH`:

   .. code-block:: sh

      $ export PYTHONPATH=$HOME/webapps/randopony/lib/python2.7

#. Install the Python client library for Google data APIs:

   .. code-block:: sh

       $ easy_install-2.7 \
         --install-dir=$HOME/webapps/randopony/lib/python2.7/ \
         gdata

#. Install the South database migration tool for Django:

   .. code-block:: sh

      $ easy_install-2.7 \
        --install-dir=$HOME/webapps/randopony/lib/python2.7/ \
        south

#. Install the Django-Celery asynchronous task queue framework:

   .. code-block:: sh

      $ easy_install-2.7 \
        --install-dir=$HOME/webapps/randopony/lib/python2.7/ \
        --script-dir=$HOME/webapps/randopony/bin \
        django-celery

#. Install the Django-Kombu task message transport library:

   .. code-block:: sh

      $ easy_install-2.7 \
        --install-dir=$HOME/webapps/randopony/lib/python2.7/ \
        --script-dir=$HOME/webapps/randopony/bin \
        django-kombu


Configure Production and Private Settings
=========================================

#. Edit :file:`randopony/production_settings.py` to make the
   settings appropriate for your deployment:

#. Create :file:`randopony/private_settings.py` and put values in it
   for:

   * SECRET_KEY
   * GOOGLE_DOCS_PASSWORD
   * EMAIL_HOST_PASSWORD

   :file:`randopony/private_settings.py` should have tight
   permissions; e.g. 600, and should be excluded from version control
   tracking.

#. Review the :file:`randopony/settings.py` module and change any
   values that you think you need to, :kbd:`TIME_ZONE`, for example.
   Note that you can change the
   :kbd:`REGISTRATION_FORM_CAPTCHA_QUESTION` and its answer, but the
   view code assumes that the answer is an integer.


Copy RandoPony to WebFaction
============================

There are lots of ways to do this, but the
:file:`randopony/fabfile.py` module includes a :kbd:`deploy_code`
Fabric_ task that can be used to create the initial deployment on
WebFaction.

.. code-block:: sh

   $ fab deploy_code

excludes a bunch of files that don't need to, or shouldn't be copied
to WebFaction; e.g. the local version of the database, development
settings file, etc.

:file:`randopony/fabfile.py` also includes a :kbd:`deploy` task that
provides a means of updating the deployed files when changes are made
in your local development copy, collecting the static files, and
restarting Apache. The :kbd:`deploy` task is the default task in
:file:`randopony/fabfile.py`.

.. _Fabric: http://fabfile.org


Configure the RandoPony Installation on WebFaction
==================================================

#. Open a :command:`ssh` session to WebFaction.

#. Change to the :file:`randopony` directory:

   .. code-block:: sh

      $ cd $HOME/webapps/randopony

#. Delete the :file:`myproject` directory created when Django was installed:

   .. code-block:: sh

      $ rm -rf myproject

#. Rename the :file:`myproject.wsgi` file to :file:`randopony.wsgi`:

   .. code-block:: sh

      $ mv myproject.wsgi randopony.wsgi

#. Edit the :file:`randopony.wsgi` file to set the settings module name:

   .. code-block:: python

      os.environ['DJANGO_SETTINGS_MODULE'] = randopony.settings

#. Edit the :file:`apache2/conf/httpd.conf` file to set the WSGI script alias:

   .. code-block:: conf

      WSGIScriptAlias / /home/bcrandonneur/webapps/randopony/randopony.wsgi


Create a Mailbox and Email Address for RandoPony
================================================

WebFaction's SMTP server will only allow applications to send email
from mailboxes and addresses that have been created in the control
panel.

#. Use the :guilabel:`E-mails > Mailboxes` menu to create a mailbox
   called :kbd: `randopony`, and set its password to the value you put
   in the :file:`private_settings.py` module.

#. Use the :guilabel:`E-mails > E-mail addresses` menu to create an
   address like :kbd: `randopony@randonneurs.bc.ca` that matches what
   you put in the :file:`settings.py` module, and target it at the
   :kbd:`randopony` mailbox. You can create a fun auto-responder
   message too, if you want.


Initialize the Database and Start the App
=========================================

#. Initialize the database, and create a superuser:

   .. code-block:: sh

      $ cd $HOME/webapps/randopony
      $ bin/django-admin.py syncdb --pythonpath="$HOME/webapps/randopony" --settings=randopony.settings
      ...

#. Use South to apply all of the database migrations necessary to
   bring the database into sync with the current version of
   :kbd:`randopony`:

   .. code-block:: sh

      $ cd $HOME/webapps/randopony/randopony
      $ bin/django-admin.py migrate --pythonpath="$HOME/webapps/randopony" --settings=randopony.settings
      ...

#. Tighten up security by making the database, and settings files
   read-write by owner only, and invisible to everyone else:

   .. code-block:: sh

      $ cd $HOME/webapps/randopony/randopony/
      $ chmod go-rw randopony-production.db
      $ chmod go-rw settings.py production_settings.py private_settings.py

#. Restart Apache:

   .. code-block:: sh

      $ $HOME/webapps/randopony/apache2/bin/restart

The application should now be accessible at
:kbd:`http://randopony.randonneurs.bc.ca/` and the Django admin
interface should be operational at
:kbd:`http://randopony.randonneurs.bc.ca/admin/`


Add Deployment-Specific Settings to Database
============================================

#. Log in to the admin interface.

#. In the :kbd:`Email address` table of the :kbd:`Pasture` app, add
   email addresses with the following keys:

   * :kbd:`webmaster`
       The email address of the club site webmaster that will receive
       notifications when events are added to the pony

   * :kbd:`from_randopony`
       The email address to use as the :kbd:`From` address for emails
       that the pony sents

   * :kbd:`google_docs` The email address used to log into the Google
       Docs account associated with the pony, where the rider list
       spreadsheets are stored

#. In the :kbd:`Links` table of the :kbd:`Pasture` app, add URLs with
   the following keys:

   * :kbd:`event_waiver_url`
       The URL of the event waiver on the club web site

   * :kbd:`membership_form_url`
       The URL of the membership and waiver form on the club web site

..
   Local Variables:
   mode: rst
   mode: auto-fill
   End:
