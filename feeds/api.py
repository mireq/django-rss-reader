# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import HttpResponseBadRequest
from django.views.generic import View, DetailView

from .models import UserEntryStatus
from .views import UserEntriesMixin
from web.generic_views import ApiEndpointMixin


class EntryListApi(UserEntriesMixin, ApiEndpointMixin, View):
	ENTRIES_COUNT = 20

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
		entries = list(entries.select_related('entry', 'entry__feed')[:self.ENTRIES_COUNT])
		result = [entry.serialize() for entry in entries]
		if 'self' in request.GET and hasattr(self, 'object'):
			result.insert(0, self.object.serialize())
		return self.render_result(result)


class EntryDetailApi(UserEntriesMixin, ApiEndpointMixin, DetailView):
	api_actions = {
		'get': {
			'serialize': 'serialize'
		}
	}

	def get_queryset(self):
		return UserEntryStatus.objects.for_user(self.request.user)

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		return self.render_api_actions(request.GET) or HttpResponseBadRequest("Unknown action")

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return self.render_api_actions(request.POST, 'post') or HttpResponseBadRequest("Unknown action")

	def serialize(self):
		return self.render_result(self.object.serialize())


entry_list_api = EntryListApi.as_view()
entry_detail_api = EntryDetailApi.as_view()
