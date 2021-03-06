# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import View, DetailView

from .models import UserEntryStatus
from .views import UserEntriesMixin
from web.generic_views import ApiEndpointMixin


class EntryListApi(UserEntriesMixin, ApiEndpointMixin, View):
	ENTRIES_COUNT = 50

	def get(self, request, *args, **kwargs):
		if 'from' in request.GET:
			try:
				entry_id = int(self.request.GET['from'])
				self.object = (UserEntryStatus.objects
					.prefetch_user_feed(user=self.request.user)
					.get(user=self.request.user, entry__id=entry_id))
			except (UserEntryStatus.DoesNotExist, ValueError):
				return self.render_error('Entry does not exist')

		entries = self.get_prev_entries() if 'prev' in request.GET else self.get_next_entries()
		entries = list(entries.select_related('entry', 'entry__feed')[:self.ENTRIES_COUNT + 1])
		next_entry = None
		if len(entries) > self.ENTRIES_COUNT:
			next_entry = entries.pop()
		result = [self.serialize_entry(entry) for entry in entries]
		if 'self' in request.GET and hasattr(self, 'object'):
			result.insert(0, self.serialize_entry(self.object))
		if next_entry:
			return self.render_result(result, next=next_entry.pk)
		else:
			return self.render_result(result)

	def serialize_entry(self, entry):
		data = entry.serialize()
		ctx = {
			'object': entry,
			'feed': entry.entry.feed.title if len(entry.entry.feed.user_feed) == 0 else entry.entry.feed.user_feed[0].name,
			'request': self.request,
		}
		data['rendered'] = render_to_string('feeds/userentrystatus_detail_ajax.html', ctx, request=self.request)
		return data


class EntryDetailApi(UserEntriesMixin, ApiEndpointMixin, DetailView):
	api_actions = {
		'get': ['serialize'],
		'post': ['mark_read'],
	}

	def get_queryset(self):
		return UserEntryStatus.objects.for_user(self.request.user).select_related('entry')

	def get_object(self, **kwargs):
		return get_object_or_404(self.get_queryset(), entry__pk=self.kwargs['pk'])

	def dispatch(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(EntryDetailApi, self).dispatch(request, *args, **kwargs)

	def serialize(self):
		return self.render_result(self.object.serialize())

	def mark_read(self):
		self.object.mark_read()
		return self.render_result('ok', new_entries_count=self.request.user.new_entries_count)


entry_list_api = EntryListApi.as_view()
entry_detail_api = EntryDetailApi.as_view()
