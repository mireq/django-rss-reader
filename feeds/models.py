# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models import F, Case, When
from django.db.models.functions import Coalesce
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from web.models import TimestampModelMixin
from web.ordering import get_next_order


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


class FeedManager(models.Manager):
	def for_update(self):
		return self.get_queryset().exclude(update_status='')


@python_2_unicode_compatible
class Feed(TimestampModelMixin, models.Model):
	UPDATE_STATUS_UPDATED = 'u'
	UPDATE_STATUS_ERROR = 'e'

	UPDATE_STATUS_CHOICES = (
		('', _("Not updated")),
		('u', _("Updated")),
		('e', _("Update error")),
	)

	objects = FeedManager()

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
		next_order = get_next_order(UserFeed.objects.filter(user=user, category=category))
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
	def for_user(self, user):
		feed_name = Coalesce(
			Case(
				When(
					feed__userfeed__user=user,
					then=F('feed__userfeed__name')
				),
				output_field=models.CharField(null=True)
			),
			F('feed'),
			output_field=models.CharField()
		)
		return (self.get_queryset()
			.filter(status__user=user, feed__userfeed__user=user)
			.annotate(feed_name=feed_name)
			.select_related('feed'))


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
	created = models.DateTimeField(
		verbose_name = _("created date"),
		blank=True,
		null=True,
		db_index=True
	)
	updated = models.DateTimeField(
		verbose_name = _("updated date"),
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

	@property
	def short_summary(self):
		return Truncator(strip_tags(self.summary).replace('&shy;', '')).words(100, truncate="...")

	class Meta:
		verbose_name = _("News entry")
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
		verbose_name=_("news item"),
		related_name='status'
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
