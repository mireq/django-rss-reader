# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import operator
from functools import reduce

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.utils.functional import cached_property

from .models import Entry


class UserEntriesMixin(LoginRequiredMixin):
	ORDERINGS = {
		'default': ('-created', '-pk'),
		'old': ('created', 'pk'),
	}

	paginate_by = 10

	def get_queryset(self):
		return self.get_filtered_queryset().order_by(*self.get_ordering())

	def get_filtered_queryset(self):
		qs = Entry.objects.for_user(self.request.user)
		if self.saved_filters.get('all'):
			return qs
		else:
			return qs.filter(is_read=False)

	def get_reverse_queryset(self):
		return self.get_filtered_queryset().order_by(*self.get_reverse_ordering())

	def get_ordering(self):
		return self.ORDERINGS.get(self.saved_filters.get('list_type', 'new'), self.ORDERINGS['default'])

	def get_reverse_ordering(self):
		def invert_field(field):
			if field[0] == '-':
				return field[1:]
			else:
				return '-' + field
		return [invert_field(field) for field in self.get_ordering()]

	def get_next_by_ordering(self, queryset, ordering):
		prev_fields = []
		conditions = []
		for field in ordering:
			negative = field[0] == '-'
			if negative:
				field = field[1:]
			cond = {f: getattr(self.object, f) for f in prev_fields}
			op = 'lt' if negative else 'gt'
			cond[field + '__' + op] = getattr(self.object, field)
			conditions.append(Q(**cond))
			prev_fields.append(field)
		return queryset.filter(reduce(operator.or_, conditions, Q()))

	def get_next(self):
		ordering = self.get_ordering()
		qs = self.get_filtered_queryset().order_by(*ordering)
		return self.get_next_by_ordering(qs, ordering).first()

	def get_prev(self):
		ordering = self.get_reverse_ordering()
		qs =  self.get_filtered_queryset().order_by(*ordering)
		return self.get_next_by_ordering(qs, ordering).first()

	@cached_property
	def saved_filters(self):
		filters = self.request.session.get('saved_filters', {})
		if 'list_type' in self.request.GET:
			filters['list_type'] = self.request.GET['list_type']
		if 'all' in self.request.GET:
			filters['all'] = self.request.GET.get('all')
		return filters


class EntryList(UserEntriesMixin, ListView):
	def get(self, request, *args, **kwargs):
		if self.request.session.get('saved_filters') != self.saved_filters:
			self.request.session['saved_filters'] = self.saved_filters
		return super(EntryList, self).get(request, *args, **kwargs)


class EntryDetail(UserEntriesMixin, DetailView):
	def get_queryset(self):
		return Entry.objects.for_user(self.request.user)

	def get_context_data(self, **kwargs):
		ctx = super(EntryDetail, self).get_context_data(**kwargs)
		ctx['next'] = self.get_next()
		ctx['prev'] = self.get_prev()
		return ctx

	def get_object(self, **kwargs):
		obj = super(EntryDetail, self).get_object(**kwargs)
		obj.mark_favorite(self.request.user)
		return obj


entry_list = EntryList.as_view()
entry_detail = EntryDetail.as_view()
