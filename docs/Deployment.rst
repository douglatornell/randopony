=====================================
Deployment of RandoPony on WebFaction
=====================================

:Author: Doug Latornell
:Created: 2009-12-27
:Revised: 2011-02-13


These notes describe the process of deploying RandoPony on the
WebFaction_ shared hosting service. Specifically, what is described is
a deployment under my :kbd:`sadahome.ca` domain, but it shouldn't be
hard to extrapolate from these notes to deploy under another domain.

.. _WebFaction: http://webfaction.com

The canonical reference at the time of writing is the `Django section`_
of the `WebFaction Software Documentation`_.

.. _Django section: http://docs.webfaction.com/software/django/index.html
.. _WebFaction Software Documentation: http://docs.webfaction.com/software/index.html


Create the Django and Static Media Applications
===============================================

#. Log into the WebFaction control panel.
#. Use the :guilabel:`Domains / websites > Applications` menu to
    create a :kbd:`Django 1.2.5/mod_wsgi 3.2/Python 2.6` application
    called :kbd:`randopony`.

To reduce memory consumption (the primary resource limitation and
package cost differentiator on WebFaction), and improve performance of
the app, create static applications to serve media files (CSS, images,
JavaScript, etc.) for RandoPony and the Django admin:

#. Use the :guilabel:`Domains / websites > Applications` menu to
   create a :kbd:`Symbolic link to static-only app` application called
   :kbd:`randopony_media` that links to
   :kbd:`/home/dlatornell/webapps/randopony/randopony/media` (this is
   the value to enter in the :guilabel:`Extra Info:` field.
#. Also create a :kbd:`Symbolic link to static-only app` application
   called :kbd:`randopony_admin_media` that links to
   :kbd:`/home/dlatornell/webapps/randopony/lib/python2.6/django/contrib/admin/media`.
#. Finally, create a :kbd:`Symbolic link to static-only app`
   application called :kbd:`randopony_docs` that links to
   :kbd:`/home/dlatornell/webapps/randopony/randopony/docs/_build/html`


Create the :kbd:`randopony` Subdomain
=====================================

Create a subdomain from which the randopony app will be served:

#. Use the :guilabel:`Domains / websites > Domains` menu to add a
   :kbd:`randopony` subdomain prefix to the :kbd:`sadahome.ca` domain.


Create the Website Entry
========================

Configure WebFaction to proxy requests to the Django app, and static media apps:

#. Use the :guilabel:`Domains / websites > Websites` menu to create a
   site called :kbd: `randopony` connected to the
   :kbd:`randopony.sadahome.ca` subdomain, with the following site
   apps added to it:

   * :kbd:`randopony` mounted at :kbd:`/`
   * :kbd:`randopony_media` mounted at :kbd:`/media`
   * :kbd:`randopony_admin_media` mounted at :kbd:`/media/admin`
   * :kbd:`randopony_docs` mounted at :kbd:`/docs`


Install the Packages that RandoPony Depends On
==============================================

#. :command:`ssh` into :kbd:`webfaction.com`.

#. Put the :kbd:`randopony` Python library directory on the
   :envvar:`PYTHONPATH`:

    .. code-block:: sh
    
       export PYTHONPATH=$HOME/webapps/randopony/lib/python2.6

#. Install the Python client library for Google data APIs:

    .. code-block:: sh
    
        easy_install-2.6 --install-dir=$HOME/webapps/randopony/lib/python2.6/ --script-dir $HOME/webapps/bin gdata

#. Install the South database migration tool for Django:

    .. code-block:: sh
    
        easy_install-2.6 --install-dir=$HOME/webapps/randopony/lib/python2.6/ --script-dir $HOME/webapps/bin south


Create a Django Settings Module
===============================

#. Copy :file:`randopony/settings.py` to
   :file:`randopony/webfaction-settings.py` and edit it make the
   settings appropriate for the deployment:

   .. code-block:: python

      DEBUG = False

      ADMINS = (
          ('Your Name', 'you@example.com'),
      )

      SECRET_KEY = 'a string of random characters, the longer the better'

      EMAIL_USER_PASSWORD = 'password for the randopony email sender account''

Review the other settings and change any that you think you need to,
:kbd:`TIME_ZONE`, for example.  Note that you can change the
:kbd:`REGISTRATION_FORM_CAPTCHA_QUESTION` and its answer, but the view
code assumes that the answer is an integer.


Copy RandoPony to WebFaction
============================

There are lots of ways to do this, but the :file:`randopony/Makefile`
target :kbd:`rsync-proj` uses :command:`rsync` to create the initial
deployment on WebFaction as well as providing a means of updating the
deployed files when changes are made in your local development
copy.

   .. code-block:: sh

      make rsync-proj

excludes a bunch of files that don't need to, or shouldn't be copied
to WebFaction; e.g. the local version of the database, development
settings file, etc.


Configure the RandoPony Installation on WebFaction
==================================================

#. Open a :command:`ssh` session to WebFaction.

#. Change to the :file:`randopony` directory:

   .. code-block:: sh

      cd ~/webapps/randopony

#. Delete the :file:`myproject` directory created when Django was installed:

   .. code-block:: sh

      rm -rf myproject

#. Rename the :file:`myproject.wsgi` file to :file:`randopony.wsgi`:

   .. code-block:: sh

      mv myproject.wsgi randopony.wsgi

#. Edit the :file:`randopony.wsgi` file to set the settings module name:

   .. code-block:: python

      os.environ['DJANGO_SETTINGS_MODULE'] = randopony.webfaction-settings

#. Edit the :file:`apache2/conf/httpd.conf` file to set the WSGI script alias:

   .. code-block:: none

      WSGIScriptAlias / /home/dlatornell/webapps/randopony/randopony.wsgi


Create a Mailbox and Email Address for RandoPony
================================================

WebFaction's SMTP server will only allow applications to send email
from mailboxes and addresses that have been created in the control
panel.

#. Use the :guilabel:`E-mails > Mailboxes` menu to create a mailbox
   called :kbd: `randopony`, and set its password to the value you put
   in the :file:`webfaction-settings.py` file. 

#. Use the :guilabel:`E-mails > E-mail addresses` menu to create an
   address like :kbd: `randopony@sadahome.ca` that matches what you
   put in the :file:`webfaction-settings.py` file, and target it at
   the :kbd:`randopony` mailbox. You can create a fun auto-responder
   message too, if you want.


Initialize the Database and Start the App
=========================================

#. Rename the :file:`.webfaction_secret_key` file to
   :file:`.secret_key`.

#. Initialize the database, and create a superuser. We need to
   temporarily copy :file:`webfaction-settings.py` to
   :file:`settings.py` for this step because that's the name that
   :command:`manage.py` expects:

   .. code-block:: sh

      cd ~/webapps/randopony/randopony
      cp webfaction-settings.py settings.py
      python2.6 manage.py syncdb
      ...

#. Tighten up security by making the database, settings, and password
   files read-write by owner only, and invisible to everyone else, and
   removing world execute permission from the :file:`manage.py` file:

   .. code-block:: sh

      cd ~/webapps/randopony/randopony/
      chmod go-rw randopony-production.db
      chmod go-rw webfaction-settings.py settings.py
      chmod go-rw .email_host_password .google_docs_password
      chmod o-x manage.py

#. Use South to apply all of the database migrations necessary to
    bring the database into sync with the current version of
    :kbd:`randopony`:

   .. code-block:: sh
      
      python2.6 manage.py migrate register

#. Delete the  temporary copy of :file:`webfaction-settings.py`:

   .. code-block:: sh
      
      rm settings.py*

#. Restart Apache:

   .. code-block:: sh

      ~/webapps/randopony/apache2/bin/restart


The application should now be accessible at
:kbd:`http://randopony.sadahome.ca/register/` and the Django admin
interface should be operational at
:kbd:`http://randopony.sadahome.ca/admin/`

.. 
   Local Variables:
   mode: rst
   mode: auto-fill
   End:
