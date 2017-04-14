# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog

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
	url(r'^jsi18n/$', JavaScriptCatalog.as_view(**js_info_dict), name='javascript-catalog'),
	url(r'^template-change/$', template_dynamicloader.views.change, name='template-change'),
	url(r'^task-status/$', web.celery_views.task_status_view, name='celery_task_status'),
	url(r'^settings/$', web.views.settings_view, name='settings_view'),
	url(r'^', include('feeds.urls')),
]

if settings.DEBUG:
	import debug_toolbar
	urlpatterns += [
		url(r'^__debug__/', include(debug_toolbar.urls)),
	]
