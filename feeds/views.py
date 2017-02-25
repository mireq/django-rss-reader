# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import operator
from functools import reduce

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.utils.functional import cached_property
from django.views.generic import ListView, DetailView, FormView, DeleteView
from django_ajax_utils.views import AjaxFormMixin, AjaxRedirectMixin

from .forms import FeedCreateForm
from .models import Entry, UserFeed
from feeds.tasks import register_feed
from web.celery_views import TaskRunMixin
from web.time_utils import datetime_to_timestamp, timestamp_to_datetime


class UserEntriesMixin(LoginRequiredMixin):
	ORDERINGS = {
		'default': ('-created', '-pk'),
		'old': ('created', 'pk'),
	}

	paginate_by = 10
	is_detail = False

	def get_context_data(self, **kwargs):
		ctx = super(UserEntriesMixin, self).get_context_data(**kwargs)
		ctx['filters'] = self.saved_filters
		return ctx

	def get_queryset(self):
		return self.get_filtered_queryset().order_by(*self.get_ordering())

	def get_filtered_queryset(self):
		qs = Entry.objects.for_user(self.request.user)
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
			if not self.is_detail:
				filters['ts'] = datetime_to_timestamp(datetime=None)
		return filters


class EntryListView(UserEntriesMixin, ListView):
	def get(self, request, *args, **kwargs):
		self.request.session['saved_filters'] = self.saved_filters
		return super(EntryListView, self).get(request, *args, **kwargs)


class EntryDetailView(UserEntriesMixin, DetailView):
	is_detail = True

	def get_queryset(self):
		return Entry.objects.for_user(self.request.user)

	def get_context_data(self, **kwargs):
		ctx = super(EntryDetailView, self).get_context_data(**kwargs)
		ctx['next'] = self.get_next()
		ctx['prev'] = self.get_prev()
		return ctx

	def post(self, request, *args, **kwargs):
		action = request.POST.get('action', '')
		if action == 'favorite':
			self.get_object().mark_favorite(request.user, True)
		elif action == 'unfavorite':
			self.get_object().mark_favorite(request.user, False)
		return HttpResponseRedirect(self.request.get_full_path())

	def get(self, request, *args, **kwargs):
		if 'mark' in self.request.GET:
			self.get_object().mark_read(self.request.user)
			return HttpResponse('')
		response = super(EntryDetailView, self).get(request, *args, **kwargs)
		if not 'cache' in self.request.GET:
			self.object.mark_read(self.request.user)
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
