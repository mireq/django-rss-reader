# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


REMEMBER_COOKIE_AGE = getattr(settings, 'ACCOUNTS_REMEMBER_COOKIE_AGE', 31536000)
REMEMBER_COOKIE_NAME = getattr(settings, 'ACCOUNTS_REMEMBER_COOKIE_NAME', 'remember_token')
