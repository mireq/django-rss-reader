# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import operator
from functools import reduce

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import ListView, DetailView, FormView, DeleteView
from django_ajax_utils.views import JsonResponseMixin, AjaxFormMixin, AjaxRedirectMixin

from .forms import FeedCreateForm
from .models import UserFeed, UserEntryStatus
from feeds.tasks import register_feed
from web.celery_views import TaskRunMixin
from web.model_utils import query_model_attribute
from web.time_utils import datetime_to_timestamp, timestamp_to_datetime


class UserEntriesMixin(LoginRequiredMixin):
	ORDERINGS = {
		'default': ('-created', '-pk'),
		'old': ('created', 'pk'),
	}

	paginate_by = 10

	def get_context_data(self, **kwargs):
		ctx = super(UserEntriesMixin, self).get_context_data(**kwargs)
		ctx['filters'] = self.saved_filters
		return ctx

	def get_queryset(self):
		return self.get_filtered_queryset().order_by(*self.get_ordering())

	def get_filtered_queryset(self):
		qs = (UserEntryStatus.objects
			.for_user(self.request.user)
			.select_related('entry'))
		if self.saved_filters.get('all'):
			return qs
		elif self.saved_filters.get('favorite'):
			return qs.filter(is_favorite=True)
		else:
			display_time = self.saved_filters.get('ts')
			if display_time:
				return qs.filter(Q(is_read=False) | (Q(read_time__gt=timestamp_to_datetime(display_time))))
			else:
				return qs.filter(Q(is_read=False))

	def get_reverse_queryset(self):
		return self.get_filtered_queryset().order_by(*self.get_reverse_ordering())

	def get_ordering(self):
		return self.ORDERINGS.get(self.saved_filters.get('list_ordering', 'new'), self.ORDERINGS['default'])

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
			if hasattr(self, 'object') and self.object:
				cond = {f: query_model_attribute(self.object, f) for f in prev_fields}
				op = 'lt' if negative else 'gt'
				cond[field + '__' + op] = query_model_attribute(self.object, field)
				conditions.append(Q(**cond))
			prev_fields.append(field)
		return queryset.filter(reduce(operator.or_, conditions, Q()))

	def get_next_entries(self):
		ordering = self.get_ordering()
		qs = self.get_filtered_queryset().order_by(*ordering)
		return self.get_next_by_ordering(qs, ordering)

	def get_prev_entries(self):
		ordering = self.get_reverse_ordering()
		qs = self.get_filtered_queryset().order_by(*ordering)
		return self.get_next_by_ordering(qs, ordering)

	def get_next(self):
		return self.get_next_entries().first()

	def get_prev(self):
		return self.get_prev_entries().first()

	def get_last_view_ts(self, filters):
		try:
			return float(self.request.GET.get('ts', ''))
		except ValueError:
			return filters.get('ts', 0)

	@cached_property
	def saved_filters(self):
		filters = self.request.session.get('saved_filters', {})
		if 'list_ordering' in self.request.GET:
			filters['list_ordering'] = self.request.GET['list_ordering']
		filters['all'] = self.request.GET.get('all', filters.get('all'))
		filters['favorite'] = self.request.GET.get('favorite', filters.get('favorite'))
		try:
			filters['ts'] = float(self.request.GET.get('ts', ''))
		except ValueError:
			pass
		return filters


class EntryListView(UserEntriesMixin, ListView):
	def get(self, request, *args, **kwargs):
		filters = self.saved_filters
		if not 'ts' in self.request.GET:
			filters['ts'] = datetime_to_timestamp(datetime=None)
		self.request.session['saved_filters'] = filters
		return super(EntryListView, self).get(request, *args, **kwargs)


class EntryDetailView(UserEntriesMixin, JsonResponseMixin, DetailView):
	def get_queryset(self):
		return UserEntryStatus.objects.for_user(self.request.user).select_related('entry')

	def get_object(self, **kwargs):
		return get_object_or_404(self.get_queryset(), entry__pk=self.kwargs['pk'])

	def get_context_data(self, **kwargs):
		ctx = super(EntryDetailView, self).get_context_data(**kwargs)
		obj = ctx['object']
		ctx['next'] = self.get_next()
		ctx['prev'] = self.get_prev()
		try:
			ctx['feed'] = UserFeed.objects.get(user=self.request.user, feed=obj.entry.feed)
		except UserFeed.DoesNotExist:
			ctx['feed'] = obj.entry.feed
		return ctx

	def post(self, request, *args, **kwargs):
		action = request.POST.get('action', '')
		if action == 'favorite':
			self.get_object().mark_favorite(True)
		elif action == 'unfavorite':
			self.get_object().mark_favorite(False)
		return HttpResponseRedirect(self.request.get_full_path())

	def get(self, request, *args, **kwargs):
		if 'mark' in self.request.GET:
			self.get_object().mark_read()
			return self.render_json_response({'new_entries_count': request.user.new_entries_count})
		response = super(EntryDetailView, self).get(request, *args, **kwargs)
		self.object.mark_read()
		return response


class UserFeedMixin(object):
	def get_queryset(self):
		return (UserFeed.objects
			.filter(user=self.request.user)
			.order_by('order')
			.select_related('feed', 'category'))


class UserFeedListView(LoginRequiredMixin, UserFeedMixin, ListView):
	paginate_by = 100
	template_name = 'feeds/user_feed_list.html'


class UserFeedDetailView(LoginRequiredMixin, UserFeedMixin, DetailView):
	template_name = 'feeds/user_feed_detail.html'

	def get_context_data(self, **kwargs):
		ctx = super(UserFeedDetailView, self).get_context_data(**kwargs)
		ctx['feed'] = ctx['object'].feed
		return ctx


class UserFeedCreateView(LoginRequiredMixin, AjaxFormMixin, TaskRunMixin, FormView):
	form_class = FeedCreateForm
	template_name = 'feeds/user_feed_create.html'
	form_instance = None
	task = register_feed

	def form_valid(self, form):
		self.form_instance = form
		if self.only_validate_form:
			return self.render_to_response(self.get_context_data(form=form))
		return self.get_task_status_response()

	def get_task_kwargs(self):
		xml_url = self.form_instance.cleaned_data['xml_url']
		return {'url': xml_url, 'user_id': self.request.user.pk}

	def get(self, request, *args, **kwargs):
		if self.celery_task_parsed['status'] == 'SUCCESS':
			user_feed = UserFeed.objects.get(
				user=self.request.user,
				feed__pk=self.celery_task_parsed['data']['feed']
			)
			return HttpResponseRedirect(user_feed.get_absolute_url())
		return super(UserFeedCreateView, self).get(request, *args, **kwargs)


class UserFeedDeleteView(LoginRequiredMixin, AjaxRedirectMixin, DeleteView):
	template_name = 'feeds/user_feed_confirm_delete.html'

	def get_queryset(self):
		return UserFeed.objects.filter(user=self.request.user)

	def get_success_url(self):
		return reverse('user_feed_list')


entry_list_view = EntryListView.as_view()
entry_detail_view = EntryDetailView.as_view()
user_feed_list_view = UserFeedListView.as_view()
user_feed_detail_view = UserFeedDetailView.as_view()
user_feed_create_view = UserFeedCreateView.as_view()
user_feed_delete_view = UserFeedDeleteView.as_view()
