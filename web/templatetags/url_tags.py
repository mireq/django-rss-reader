# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def link_add(context, url, **values):
	if not values:
		return url
	get_data = context['request'].GET.copy()
	get_data.pop('page', None)
	get_data.update(values)
	separator = '&' if '?' in url else '?'
	return url + separator + get_data.urlencode()


@register.simple_tag(takes_context=True)
def link_remove(context, url, *keys):
	if not keys:
		return url
	get_data = context['request'].GET.copy()
	get_data.pop('page', None)
	for key in keys:
		if key in get_data:
			del get_data[key]
	encoded = get_data.urlencode()
	if encoded:
		separator = '&' if '?' in url else '?'
		return url + separator + encoded
	else:
		return url


@register.simple_tag(takes_context=True)
def current_link_add(context, **values):
	return link_add(context['request'].path, **values)


@register.simple_tag(takes_context=True)
def current_link_remove(context, *keys):
	return link_remove(context['request'].path, *keys)
