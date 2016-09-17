# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from time import mktime

import feedparser
from django.utils import timezone
from django.utils.encoding import force_text

from feeds.models import Feed, Entry


def timestruct_to_utctime(timestruct):
	if timestruct is None:
		return None
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


def register_feed(url):
	feed, _ = Feed.objects.update_or_create(xml_url=url)
	try:
		parser_data = feedparser.parse(feed.xml_url)
		fill_feed_info(feed, parser_data)
		feed.save()
		return {'status': 'success', 'feed': feed}
	except Exception as e: #pylint: disable=broad-except
		feed.save()
		return {'status': 'error', 'error': force_text(e), 'feed': feed}


def import_entries(feed, entries):
	for entry in entries:
		entry_data = {
			'link': entry.link,
			'title': entry.title,
			'summary': entry.get('summary', ''),
			'content': entry.get('content', ''),
			'published': timestruct_to_utctime(entry.get('published_parsed', None)),
			'author_name': entry.get('author', ''),
		}
		Entry.objects.update_or_create(
			guid=entry.guid,
			feed=feed,
			defaults=entry_data,
		)


def import_feed(feed):
	try:
		parser_data = feedparser.parse(feed.xml_url)
		fill_feed_info(feed, parser_data)
		feed.update_status = Feed.UPDATE_STATUS_UPDATED
		feed.update_error = ''
		feed.save()
	except Exception as e: #pylint: disable=broad-except
		feed.update_status = Feed.UPDATE_STATUS_ERROR
		feed.update_error = force_text(e)
		feed.save()
	import_entries(feed, parser_data.entries)
