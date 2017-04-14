# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog

import feeds.api
import feeds.views
import template_dynamicloader.views
import web.celery_views
import web.views


js_info_dict = {
	'packages': None,
	'domain': 'djangojs',
}


urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^accounts/', include('accounts.urls')),
	url(r'^entry/(?P<pk>\d+)/$', feeds.views.entry_detail_view, name='entry_detail'),
	url(r'^$', feeds.views.entry_list_view, name='entry_list'),
	url(r'^feeds/$', feeds.views.user_feed_list_view, name='user_feed_list'),
	url(r'^feeds/create/$', feeds.views.user_feed_create_view, name='user_feed_create'),
	url(r'^feeds/(?P<pk>\d+)/detail/$', feeds.views.user_feed_detail_view, name='user_feed_detail'),
	url(r'^feeds/(?P<pk>\d+)/delete/$', feeds.views.user_feed_delete_view, name='user_feed_delete'),
	url(r'^settings/$', web.views.settings_view, name='settings_view'),
	url(r'^template-change/$', template_dynamicloader.views.change, name='template-change'),
	url(r'^task-status/$', web.celery_views.task_status_view, name='celery_task_status'),
	url(r'^jsi18n/$', JavaScriptCatalog.as_view(**js_info_dict), name='javascript-catalog'),
	url(r'^api/entry/list/$', feeds.api.entry_list_api, name='api_entry_list'),
	url(r'^api/entry/(?P<pk>\d+)/$', feeds.api.entry_detail_api, name='api_entry_detail'),
]

if settings.DEBUG:
	import debug_toolbar
	urlpatterns += [
		url(r'^__debug__/', include(debug_toolbar.urls)),
	]
