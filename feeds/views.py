# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from .models import Entry


class UserEntriesMixin(LoginRequiredMixin):
	paginate_by = 10
	list_type = ''

	def get_queryset(self):
		return Entry.objects.for_user(self.request.user)

	def get_context_data(self, **kwargs):
		ctx = super(UserEntriesMixin, self).get_context_data(**kwargs)
		ctx['list_type'] = self.request.GET.get('list_type', self.list_type)
		return ctx


class NewEntries(UserEntriesMixin, ListView):
	list_type = 'new'

	def get_queryset(self):
		return (super(NewEntries, self).get_queryset()
			.filter(status__is_unread=True)
			.order_by('-created', '-pk'))


class EntryDetail(UserEntriesMixin, DetailView):
	pass


new_entries = NewEntries.as_view()
entry_detail = EntryDetail.as_view()
