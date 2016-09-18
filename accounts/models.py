# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .settings import REMEMBER_COOKIE_AGE


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


class RememberTokenManager(models.Manager):
	def get_by_string(self, token):
		try:
			user_id, token_hash = token.split(':')
		except ValueError:
			return None

		max_age = timezone.now() - timedelta(seconds=REMEMBER_COOKIE_AGE)
		for token in self.all().filter(created__gte=max_age, user=user_id):
			if check_password(token_hash, token.token_hash):
				return token

	def clean_remember_tokens(self):
		max_age = timezone.now() - timedelta(seconds=REMEMBER_COOKIE_AGE)
		return self.all().filter(created__lte=max_age).delete()


@python_2_unicode_compatible
class RememberToken(models.Model):
	objects = RememberTokenManager()

	token_hash = models.CharField(
		max_length=255,
		blank=False,
		primary_key=True
	)
	created = models.DateTimeField(
		editable=False,
		blank=True,
		auto_now_add=True
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name='remember_me_tokens'
	)

	def __str__(self):
		return self.token_hash
