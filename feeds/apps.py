# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import apps
from django.utils.translation import ugettext_lazy as _


class AppConfig(apps.AppConfig):
	name = 'feeds'
	verbose_name = _("Feeds")
