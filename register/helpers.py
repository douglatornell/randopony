"""Helper functions for the randopony register app.

:Author: Doug Latornell <djl@douglatornell.ca>
:Created: 2009-12-25
"""
# Python 2.6 with future features:
from __future__ import absolute_import


def email2words(email):
    """Return a slightly obfuscated version of the email address.

    Replaces @ with ' at ', and . with ' dot '.
    """
    return email.replace('@', ' at ').replace('.', ' dot ')
