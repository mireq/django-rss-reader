# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

import feeds.views


urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^accounts/', include('accounts.urls', namespace='accounts')),
	url(r'^entry/(?P<pk>\d+)/$', feeds.views.entry_detail, name='entry_detail'),
	url(r'^$', feeds.views.entry_list, name='entry_list'),
]

if settings.DEBUG:
	import debug_toolbar
	urlpatterns += [
		url(r'^__debug__/', include(debug_toolbar.urls)),
	]
