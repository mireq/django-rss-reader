# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import forms as auth_forms


class UserChangeForm(auth_forms.UserChangeForm):
	pass


class UserCreationForm(auth_forms.UserCreationForm):
	pass
