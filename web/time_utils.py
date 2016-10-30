# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime as python_datetime
from time import mktime

from django.utils import timezone


def timestamp_to_datetime(timestamp):
	return python_datetime.fromtimestamp(timestamp, timezone.utc)


def datetime_to_timestamp(datetime=None):
	if datetime is None:
		datetime = timezone.now()
	timestamp = mktime(datetime.timetuple()) + (datetime.microsecond / 1000000.)
	return timestamp
