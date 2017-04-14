# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

import feeds.api
import feeds.views


app_name = 'feeds'
urlpatterns = [
	url(r'^$', feeds.views.entry_list_view, name='entry_list'),
	url(r'^entry/(?P<pk>\d+)/$', feeds.views.entry_detail_view, name='entry_detail'),
	url(r'^feeds/$', feeds.views.user_feed_list_view, name='user_feed_list'),
	url(r'^feeds/create/$', feeds.views.user_feed_create_view, name='user_feed_create'),
	url(r'^feeds/(?P<pk>\d+)/detail/$', feeds.views.user_feed_detail_view, name='user_feed_detail'),
	url(r'^feeds/(?P<pk>\d+)/delete/$', feeds.views.user_feed_delete_view, name='user_feed_delete'),
	url(r'^api/entry/list/$', feeds.api.entry_list_api, name='api_entry_list'),
	url(r'^api/entry/(?P<pk>\d+)/$', feeds.api.entry_detail_api, name='api_entry_detail'),
]
