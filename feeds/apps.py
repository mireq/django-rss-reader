# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import apps
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _


class AppConfig(apps.AppConfig):
	name = 'feeds'
	verbose_name = _("Feeds")

	def ready(self):
		UserFeed = self.get_model('UserFeed')
		pre_delete.connect(self.on_delete_user_feed, sender=UserFeed)

	def on_delete_user_feed(self, instance, **kwargs):
		UserNewsStatus = self.get_model('UserNewsStatus')
		UserNewsStatus.objects.filter(user=instance.user, news__feed=instance.feed.delete())
