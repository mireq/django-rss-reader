# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _


class FeedCreateForm(forms.Form):
	xml_url = forms.URLField(label=_("URL"))
