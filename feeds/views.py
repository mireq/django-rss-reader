# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Entry


class UserEntriesMixin(LoginRequiredMixin):
	paginate_by = 10

	def get_queryset(self):
		return Entry.objects.for_user(self.request.user)


class NewEntries(UserEntriesMixin, ListView):
	def get_queryset(self):
		return (super(NewEntries, self).get_queryset()
			.filter(status__is_unread=True)
			.order_by('-created', '-pk'))


new_entries = NewEntries.as_view()
