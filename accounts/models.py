# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
	objects = UserManager()
	settings = models.TextField(_("settingss"), blank=True)

	def clean_fields(self, exclude=None):
		if self.email:
			qs = User._default_manager.filter(email=self.email).exclude(pk=self.pk)
			if qs.exists():
				raise ValidationError({'email': [_("User with this e-mail address already exists")]})
		super(User, self).clean_fields(exclude)

	@property
	def user_settings(self):
		try:
			return json.loads(self.settings)
		except ValueError:
			return {}

	@user_settings.setter
	def user_settings(self, val):
		self.settings = json.dumps(val, cls=DjangoJSONEncoder)
