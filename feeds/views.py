# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Q

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

	def get_new_entries(self):
		return (Entry.objects.for_user(self.request.user)
			.filter(status__is_unread=True)
			.order_by('-created', '-pk'))

	def get_new_next(self):
		obj = self.get_object()
		return (self.get_new_entries()
			.filter(Q(created__lt=obj.created) | Q(created=obj.created, pk__lt=obj.pk))
			.first())

	def get_new_prev(self):
		obj = self.get_object()
		return (self.get_new_entries()
			.filter(Q(created__gt=obj.created) | Q(created=obj.created, pk__gt=obj.pk))
			.order_by('created', 'pk')
			.first())


class NewEntries(UserEntriesMixin, ListView):
	list_type = 'new'

	def get_queryset(self):
		return self.get_new_entries()


class EntryDetail(UserEntriesMixin, DetailView):
	def get_context_data(self, **kwargs):
		ctx = super(EntryDetail, self).get_context_data(**kwargs)
		ctx['next'] = self.get_new_next()
		ctx['prev'] = self.get_new_prev()
		return ctx


new_entries = NewEntries.as_view()
entry_detail = EntryDetail.as_view()
