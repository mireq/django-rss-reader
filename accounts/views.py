# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.generic import FormView, View

from .forms import AuthenticationForm


class Login(FormView):
	template_name = 'accounts/login.html'
	form_class = AuthenticationForm

	def form_valid(self, form):
		auth_login(self.request, form.get_user())
		next_url = self.request.POST.get('next') or reverse('home')
		return HttpResponseRedirect(next_url)

	def get_context_data(self, **kwargs):
		next_url = self.request.POST.get('next', self.request.GET.get('next', ''))
		return super(Login, self).get_context_data(next=next_url, **kwargs)


class Logout(View):
	def get(self, request, *args, **kwargs):
		auth_logout(request)
		return HttpResponseRedirect(reverse('home'))


login = Login.as_view()
logout = Logout.as_view()
