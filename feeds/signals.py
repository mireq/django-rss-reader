# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Entry, UserEntryStatus, UserFeed


@receiver(post_save, sender=Entry)
def on_entry_updated(sender, instance, **kwargs): # pylint: disable=unused-argument
	users = (UserFeed.objects
		.filter(feed=instance.feed)
		.values_list('user_id', flat=True))
	user_statuses = (UserEntryStatus.objects
		.filter(user_id__in=users, entry=instance)
		.values_list('user_id', flat=True))
	to_create = set(users).difference(set(user_statuses))
	new_status_instances = [
		UserEntryStatus(user_id=user_id, entry=instance, is_unread=True)
		for user_id in to_create
	]
	UserEntryStatus.objects.bulk_create(new_status_instances)


def on_delete_user_feed(sender, instance, **kwargs): # pylint: disable=unused-argument
	UserEntryStatus.objects.filter(user=instance.user, news__feed=instance.feed.delete())
