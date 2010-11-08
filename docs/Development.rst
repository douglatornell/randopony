.. _Development-doc:

===================================
 RandoPony Development Environment
===================================

:Author: Doug Latornell
:Created: 2010-11-07

These notes describe the development environment I use for
RandoPony. I do most of the development on Mac OS/X, but these notes
should translate quite easily for Linux and BSD platforms. I do almost
zero Python development on Windows, so I can only say that you can, in
principle, set up an environment like this, but you're on your own for
the details of exactly how to do it.

The following assumes that you are using:

* pip_ for Python package installation
* virtualenv_ for development environment isolation
* virtualenvwrapper_ for managing your virtualenvs
* Mercurial_ for version control

.. _pip: http://pip.openplans.org/
.. _virtualenv: http://virtualenv.openplans.org/
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/
.. _Mercurial: http://mercurial.selenic.com/


Virtualenv Setup
================

* Create a virtualenv for development work. I name it for the Django_
  version that I'm developing against:

  .. code-block:: sh

    $ mkvirtualenv --no-site-packages --distribute django-1.2

  :command:`mkvirtualenv` will automatically activate the
  :kbd:`django-1.2` virtualenv for you. To do that manually use:

  .. code-block:: sh

    $ workon django-1.2

* Install the packages for development work:

  .. code-block:: sh
     
      (django-1.2)$ pip install django 
      (django-1.2)$ pip install south
      (django-1.2)$ pip install sphinx
      (django-1.2)$ pip install pyyaml
      (django-1.2)$ pip install ipython
      (django-1.2)$ pip install coverage

  * Django_ is the web framework that RandoPony is built on.
  * South_ is a database schema migration tool for DJango
  * Sphinx_ is the documentation tool used to generate HTML docs
  * PyYAML_ is a YAML parser/emitter for Python. The RandoPony test
    suite fixtures are in YAML
  * iPython_ is an enhanced interactive python shell
  * coverage_ is a tool for measuring test suite code coverage

  .. _Django: http://www.djangoproject.com/
  .. _South: http://south.aeracode.org/
  .. _Sphinx: http://sphinx.pocoo.org/
  .. _PyYAML: http://pyyaml.org/wiki/PyYAML
  .. _iPython: http://ipython.scipy.org/moin/
  .. _coverage: http://nedbatchelder.com/code/coverage/


Get the Code!
=============

* Clone the source code repository:

  .. code-block:: sh
     
      (django-1.2)$ cd ~/python
      (django-1.2)$ hg clone http://bitbucket.org/douglatornell/randopony

  I keep my Python development projects in a directory called
  :file:`python`. You can do what you want.

  I've shown the code being cloned from a read-only repository on
  `bitbucket.org`_. You probably want to create your own fork there
  and clone from it so that you have somewhere that you can push
  changes back to.

  .. _bitbucket.org: http://bitbucket.org/


Set Up a Media Server
=====================

This is the least OS-agnostic bit of the whole dev environment
setup. The goal is to have a web server serving the static content
from the :file:`randopony/media/` directories.

You can try the approach described in the `Django docs`_ but I haven't
had much luck with that. And anyway, you eventually have to figure out
how to get a real server to serve the static files for production
deployment, so you might as well get started...

.. _Django docs: http://docs.djangoproject.com/en/1.2/howto/static-files/

On OS/X I have my :kbd:`localhost` web server enabled, and have
a :file:`~/Sites/django_media` directory. Inside that I have a
symbolic link from :file:`randopony` to
:file:`~/python/randopony/media/`. I have permissions on the files in
:file:`~/python/randopony/media/` set so that they are globally
readable.

.. note::

   It would be a very *very* bad idea to use this technique to set up
   a media server on a production deployment because it may opening up
   the server's filesystem to attacks from the web.

In :file:`randopony/settings.py` I have:

.. code-block:: python

     project_path = path.dirname(__file__)
     MEDIA_ROOT = path.join(project_path, 'media')
     MEDIA_URL = 'http://localhost/~doug/django_media/randopony/'
     ADMIN_MEDIA_PREFIX = '/media/'


Run the Test Suite
==================

* Run the full test suite with:

  .. code-block:: sh

     (django-1.2)$ ./manage.py test

  That runs all of the tests; i.e. the Django admin and auth tests for
  the project, and the tests for all of the RandoPony apps, like :kbd:`register`.

* Run the test suite for a single RandoPony app:

  .. code-block:: sh

     (django-1.2)$ ./manage.py test register

* Get a code coverage report for the RandoPony apps:

  .. code-block:: sh

     (django-1.2)$ make coverage-report

  and point your browser at :file:`~/python/randopony/htmlcov/` to
  view the report.


Build the Docs
==============

* Build the HTML version of the docs with:

  .. code-block:: sh

     (django-1.2)$ cd ~/python/randopony/docs
     (django-1.2)$ make html

  and point your browser at
  :file:`~/python/randopony/docs/_build/html/` to view them.

