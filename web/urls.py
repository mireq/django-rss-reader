# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

import feeds.views
import template_dynamicloader.views
import web.views


urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^accounts/', include('accounts.urls', namespace='accounts')),
	url(r'^entry/(?P<pk>\d+)/$', feeds.views.entry_detail, name='entry_detail'),
	url(r'^$', feeds.views.entry_list, name='entry_list'),
	url(r'^feeds/$', feeds.views.user_feed_list, name='user_feed_list'),
	url(r'^feeds/create/$', feeds.views.user_feed_create, name='user_feed_create'),
	url(r'^feeds/detail/(?P<pk>\d+)/$', feeds.views.user_feed_detail, name='user_feed_detail'),
	url(r'^settings/$', web.views.settings_view, name='settings_view'),
	url(r'^template-change/$', template_dynamicloader.views.change, name='template-change'),
]

if settings.DEBUG:
	import debug_toolbar
	urlpatterns += [
		url(r'^__debug__/', include(debug_toolbar.urls)),
	]
