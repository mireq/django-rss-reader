# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils.html import strip_tags
from django.utils.text import Truncator


try:
	from html import unescape  # python 3.4+
except ImportError:
	try:
		from html.parser import HTMLParser  # python 3.x (<3.4)
	except ImportError:
		from HTMLParser import HTMLParser  # python 2.x
	unescape = HTMLParser().unescape


register = template.Library()


@register.filter
def short_summary(text):
	return Truncator(unescape(strip_tags(text).replace('&shy;', ''))).words(100, truncate="...")
