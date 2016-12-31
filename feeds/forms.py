# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Feed


class FeedCreateForm(forms.ModelForm):
	class Meta:
		model = Feed
		fields = ['xml_url']
