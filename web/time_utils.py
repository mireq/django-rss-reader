# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import time
from datetime import datetime as python_datetime

from django.utils import timezone


def timestamp_to_datetime(timestamp):
	return python_datetime(*time.gmtime(timestamp)[:6], tzinfo=timezone.utc)


def datetime_to_timestamp(datetime=None):
	if datetime is None:
		datetime = timezone.now()
	timestamp = calendar.timegm(datetime.utctimetuple()) + (datetime.microsecond / 1000000.)
	return timestamp
