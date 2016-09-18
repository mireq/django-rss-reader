# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^accounts/', include('accounts.urls', namespace='accounts')),
	url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
]
