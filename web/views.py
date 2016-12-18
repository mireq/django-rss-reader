# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class SettingsView(LoginRequiredMixin, TemplateView):
	template_name = 'settings.html'


settings_view = SettingsView.as_view()
