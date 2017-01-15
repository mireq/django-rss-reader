# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from time import mktime

import feedparser
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.encoding import force_text

from feeds.models import Feed, Entry
from web.celery import app


User = get_user_model()


def timestruct_to_utctime(timestruct):
	if timestruct is None:
		return None
	elif isinstance(timestruct, datetime):
		return timestruct
	else:
		utc_date = datetime.utcfromtimestamp(mktime(timestruct))
		return utc_date.replace(tzinfo=timezone.utc)


def fill_feed_info(feed, parser_data):
	feed_data = parser_data.feed
	feed.title = feed_data.title
	feed.description = feed_data.get('description', '')
	feed.html_url = feed_data.get('link', '')
	feed.language = feed_data.get('language', '')
	feed.last_build_date = timestruct_to_utctime(feed_data.get('updated_parsed', None))


@app.task
def register_feed(url, user_id=None):
	feed, _ = Feed.objects.get_or_create(xml_url=url)
	user = None
	if user_id is not None:
		user = User.objects.get(pk=user_id)
	try:
		parser_data = feedparser.parse(feed.xml_url)
		fill_feed_info(feed, parser_data)
		feed.update_status = Feed.UPDATE_STATUS_UPDATED
		feed.last_build_date = None
		feed.save()
		if user:
			feed.subscribe(user)
		return {'status': 'success', 'feed': feed.pk}
	except Exception as e: #pylint: disable=broad-except
		feed.save()
		if user:
			feed.subscribe(user)
		return {'status': 'error', 'error': force_text(e), 'feed': feed.pk}


def import_entries(feed, entries):
	for entry in entries:
		entry_data = {
			'link': entry.link,
			'title': entry.title,
			'summary': entry.get('summary', ''),
			'content': entry.get('content', ''),
			'created': timestruct_to_utctime(entry.get('published_parsed', entry.get('updated_parsed', timezone.now()))),
			'updated': timestruct_to_utctime(entry.get('updated_parsed')),
			'author_name': entry.get('author', ''),
		}
		try:
			entry = Entry.objects.get(
				guid=entry.get('guid', entry.get('link')),
				feed=feed
			)
			changed = False
			for key, value in entry_data.items():
				if key == 'updated':
					continue
				if getattr(entry, key) != value:
					setattr(entry, key, value)
					changed = True
			if changed:
				entry.save()
		except Entry.DoesNotExist:
			entry = Entry(
				guid=entry.get('guid', entry.get('link')),
				feed=feed,
				**entry_data
			)
			entry.save()


@app.task
def update_feed(feed_id, force=False):
	try:
		feed = Feed.objects.get(pk=feed_id)
	except Feed.DoesNotExist:
		return
	try:
		parser_data = feedparser.parse(feed.xml_url)
		old_build_date = feed.last_build_date
		fill_feed_info(feed, parser_data)
		if not force and (old_build_date == feed.last_build_date and not old_build_date is None):
			return
		feed.update_status = Feed.UPDATE_STATUS_UPDATED
		feed.update_error = ''
		feed.save()
	except Exception as e: #pylint: disable=broad-except
		feed.update_status = Feed.UPDATE_STATUS_ERROR
		feed.update_error = force_text(e)
		feed.save()
	import_entries(feed, parser_data.entries)


@app.task
def synchronize():
	for feed in Feed.objects.for_update().values_list('pk', flat=True):
		update_feed.delay(feed)
