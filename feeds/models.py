# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models import Max
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from web.models import TimestampModelMixin


@python_2_unicode_compatible
class Category(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name=_("user")
	)
	name = models.CharField(
		verbose_name=_("category name"),
		max_length=100
	)
	order = models.PositiveIntegerField(
		verbose_name=_("order"),
		default=0,
		db_index=True
	)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("Category")
		verbose_name_plural = _("Categories")
		ordering = ('order',)


@python_2_unicode_compatible
class Feed(TimestampModelMixin, models.Model):
	UPDATE_STATUS_UPDATED = 'u'
	UPDATE_STATUS_ERROR = 'e'

	UPDATE_STATUS_CHOICES = (
		('', _("Not updated")),
		('u', _("Updated")),
		('e', _("Update error")),
	)

	title = models.CharField(
		verbose_name=_("feed title"),
		max_length=200
	)
	description = models.TextField(
		verbose_name=_("feed description"),
		blank=True
	)
	xml_url = models.URLField(
		verbose_name=_("URL of feed"),
		unique=True
	)
	html_url = models.URLField(
		verbose_name=_("URL of html page"),
		blank=True
	)
	language = models.CharField(
		verbose_name=_("language"),
		max_length=20,
		blank=True
	)
	last_build_date = models.DateTimeField(
		verbose_name=_("last build date"),
		blank=True,
		null=True
	)
	last_update_date = models.DateTimeField(
		verbose_name=_("last update date"),
		blank=True,
		null=True
	)
	update_status = models.CharField(
		verbose_name=_("update status"),
		max_length=1,
		choices=UPDATE_STATUS_CHOICES,
		blank=True
	)
	update_error = models.TextField(
		verbose_name=_("update error"),
		blank=True
	)

	def subscribe(self, user, category=None):
		next_order = (UserFeed.objects
			.filter(user=user, category=category)
			.aggregate(next=Max('order'))['next'] or 0) + 1
		UserFeed.objects.update_or_create(
			user=user,
			feed=self,
			defaults={
				'name': self.title,
				'category': category,
				'order': next_order
			}
		)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = _("Feed")
		verbose_name_plural = _("Feeds")


@python_2_unicode_compatible
class UserFeed(models.Model):
	name = models.CharField(
		verbose_name=_("feed name"),
		max_length=200
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name=_("user")
	)
	feed = models.ForeignKey(
		Feed,
		verbose_name=_("feed")
	)
	category = models.ForeignKey(
		Category,
		verbose_name=_("category"),
		blank=True,
		null=True
	)
	order = models.PositiveIntegerField(
		verbose_name=_("order"),
		default=0,
		db_index=True
	)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("Feed for user"),
		verbose_name_plural = _("Feeds for user")
		unique_together = (('user', 'feed'),)
		ordering = ('order',)


class EntryManager(models.Manager):
	pass


@python_2_unicode_compatible
class Entry(models.Model):
	objects = EntryManager()

	feed = models.ForeignKey(
		Feed,
		verbose_name=_("feed")
	)
	guid = models.CharField(
		verbose_name=_("unique identifier"),
		max_length=1000,
	)
	link = models.CharField(
		verbose_name=_("link to article"),
		max_length=1000,
		blank=True
	)
	title = models.CharField(
		verbose_name=_("news title"),
		max_length=1000,
		blank=True
	)
	summary = models.TextField(
		verbose_name=_("summary"),
		blank=True
	)
	content = models.TextField(
		verbose_name=_("content"),
		blank=True
	)
	published = models.DateTimeField(
		verbose_name = _("published date"),
		blank=True,
		null=True,
		db_index=True
	)
	modified = models.DateTimeField(
		verbose_name = _("modified date"),
		blank=True,
		null=True
	)
	author_name = models.CharField(
		verbose_name=("name of author"),
		max_length=200,
		blank=True
	)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = _("News entry"),
		verbose_name_plural = _("News entries")
		unique_together = (('feed', 'guid'),)


@python_2_unicode_compatible
class UserEntryStatus(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name=_("user")
	)
	entry = models.ForeignKey(
		Entry,
		verbose_name=_("news item")
	)
	is_unread = models.BooleanField(
		verbose_name=_("news is unread"),
		blank=True,
		default=False,
		db_index=True
	)
	is_favorite = models.BooleanField(
		verbose_name=_("news is favorite"),
		blank=True,
		default=False,
		db_index=True
	)

	def __str__(self):
		return self.entry.title

	class Meta:
		verbose_name = _("News entry status for user")
		verbose_name_plural = _("News entry statuses for user")
		unique_together = (('user', 'entry'),)
