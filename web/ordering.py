# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.db.models import F, Max


def fix_ordering(queryset, order_field='order'):
	index = 0
	with transaction.atomic():
		for instance in queryset:
			index += 1
			if getattr(instance, order_field) != index:
				setattr(instance, order_field, index)
			instance.save()


def move_item(item, position, queryset, order_field='order'):
	with transaction.atomic():
		position_up_filter = {order_field + '__gte': position}
		position_add_one = {order_field: F(order_field) + 1}
		queryset.filter(**position_up_filter).update(**position_add_one)
		setattr(item, order_field, position)
		item.save()


def get_next_order(queryset, order_field='order'):
	return (queryset.aggregate(next_order=Max(order_field))['next_order'] or 0) + 1
