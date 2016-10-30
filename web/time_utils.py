# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime as python_datetime
from time import mktime

from django.utils.timezone import utc


def timestamp_to_datetime(timestamp):
	return python_datetime.fromtimestamp(timestamp, utc)


def datetime_to_timestamp(datetime=None):
	if datetime is None:
		datetime = python_datetime.now(utc)
	timestamp = mktime(datetime.timetuple()) + (datetime.microsecond / 1000000.)
	return timestamp