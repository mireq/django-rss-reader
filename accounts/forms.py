# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _


class AuthenticationForm(auth_forms.AuthenticationForm):
	pass
	#remember = forms.BooleanField(
	#	label=_("Remember me"),
	#	required=False,
	#	initial=True
	#)
