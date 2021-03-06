# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models import Prefetch
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from web.models import TimestampModelMixin
from web.ordering import get_next_order


@python_2_unicode_compatible
class Category(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name=_("user"),
		on_delete=models.CASCADE
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
		verbose_name=_("user"),
		on_delete=models.CASCADE
	)
	feed = models.ForeignKey(
		Feed,
		verbose_name=_("feed"),
		on_delete=models.CASCADE
	)
	category = models.ForeignKey(
		Category,
		verbose_name=_("category"),
		blank=True,
		null=True,
		on_delete=models.CASCADE
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

	def get_absolute_url(self):
		return reverse('feeds:user_feed_detail', args=(self.pk,))


@python_2_unicode_compatible
class Entry(models.Model):
	feed = models.ForeignKey(
		Feed,
		verbose_name=_("feed"),
		on_delete=models.CASCADE
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
	in_feed = models.BooleanField(
		verbose_name=("this entry is included in feed"),
		blank=True,
		default=True
	)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = _("News entry")
		verbose_name_plural = _("News entries")
		unique_together = (('feed', 'guid'),)

	def get_absolute_url(self):
		return reverse('feeds:entry_detail', args=(self.pk,))


class UserEntryStatusQuerySet(models.QuerySet):
	def prefetch_user_feed(self, user):
		qs = UserFeed.objects.filter(user=user).only('name')
		prefetch = Prefetch('entry__feed__userfeed_set', queryset=qs, to_attr='user_feed')
		return self.prefetch_related(prefetch)

	def for_user(self, user):
		return self.filter(user=user).prefetch_user_feed(user)


@python_2_unicode_compatible
class UserEntryStatus(models.Model):
	objects = UserEntryStatusQuerySet.as_manager()

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name=_("user"),
		on_delete=models.CASCADE
	)
	entry = models.ForeignKey(
		Entry,
		verbose_name=_("news item"),
		related_name='status',
		on_delete=models.CASCADE
	)
	is_read = models.BooleanField(
		verbose_name=_("news is readed"),
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
	read_time = models.DateTimeField(
		verbose_name=_("last read time"),
		blank=True,
		null=True,
		db_index=True
	)
	created = models.DateTimeField(
		verbose_name = _("created date"),
		db_index=True,
	)

	def serialize(self):
		return {
			'id': self.entry.id,
			'url': self.entry.get_absolute_url(),
			'is_read': self.is_read,
			'is_favorite': self.is_favorite,
			'read_time': self.read_time,
			'feed_name': self.entry.feed.title if len(self.entry.feed.user_feed) == 0 else self.entry.feed.user_feed[0].name,
			'guid': self.entry.guid,
			'link': self.entry.link,
			'title': self.entry.title,
			'summary': self.entry.summary,
			'content': self.entry.content,
			'created': self.entry.created,
			'updated': self.entry.updated,
			'author_name': self.entry.author_name,
		}

	def __str__(self):
		return self.entry.title

	class Meta:
		verbose_name = _("News entry status for user")
		verbose_name_plural = _("News entry statuses for user")
		unique_together = (('user', 'entry'),)
		index_together = (('user', 'is_read', 'created',),)

	def get_absolute_url(self):
		return self.entry.get_absolute_url()

	def mark_read(self, status=True):
		self.is_read = status
		self.read_time = timezone.now() if status else None
		self.save()
	mark_read.alters_data = True

	def mark_favorite(self, favorite=True):
		self.is_favorite = favorite
		self.save()
	mark_favorite.alters_data = True
