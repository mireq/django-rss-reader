# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template


register = template.Library()


def remove_dummy_parameters(get_data):
	get_data.pop('_dummy', None)
	get_data.pop('page', None)


@register.simple_tag(takes_context=True)
def link_add(context, url, **values):
	if not values:
		return url
	get_data = context['request'].GET.copy()
	remove_dummy_parameters(get_data)
	for k, v in values.items():
		get_data[k] = v
	separator = '&' if '?' in url else '?'
	return url + separator + get_data.urlencode('')


@register.simple_tag(takes_context=True)
def link_remove(context, url, *keys):
	if not keys:
		return url
	get_data = context['request'].GET.copy()
	remove_dummy_parameters(get_data)
	for key in keys:
		if key in get_data:
			del get_data[key]
	encoded = get_data.urlencode('')
	if encoded:
		separator = '&' if '?' in url else '?'
		return url + separator + encoded
	else:
		return url


@register.simple_tag(takes_context=True)
def current_link_add(context, **values):
	return link_add(context, context['request'].path, **values)


@register.simple_tag(takes_context=True)
def current_link_remove(context, *keys):
	return link_remove(context, context['request'].path, *keys)
