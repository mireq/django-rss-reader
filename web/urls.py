# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.contrib import admin

import feeds.views


urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^accounts/', include('accounts.urls', namespace='accounts')),
	url(r'^$', feeds.views.new_entries, name='new_entries'),
]
