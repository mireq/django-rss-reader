# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http.response import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from . import forms


REDIRECT_PARAMETER_NAME = 'next'


class SuccessRedirectMixin(object):
	redirect_url = ''

	def __get_default_redirect_url(self):
		return resolve_url(self.redirect_url)

	def __get_redirect_parameter_value(self):
		post_redirect = self.request.POST.get(REDIRECT_PARAMETER_NAME)
		get_redirect = self.request.GET.get(REDIRECT_PARAMETER_NAME)
		return post_redirect or get_redirect or ''

	def get_redirect_url(self):
		next_url = self.__get_redirect_parameter_value()
		if next_url and not is_safe_url(next_url, allowed_hosts={self.request.get_host()}):
			next_url = ''
		if next_url:
			return next_url
		else:
			return self.__get_default_redirect_url()

	def get_success_url(self):
		return self.get_redirect_url()

	def get_context_data(self, **kwargs):
		ctx = super(SuccessRedirectMixin, self).get_context_data(**kwargs)
		ctx['next'] = self.__get_redirect_parameter_value()
		ctx['REDIRECT_PARAMETER_NAME'] = REDIRECT_PARAMETER_NAME
		return ctx


class Login(SuccessRedirectMixin, generic.FormView):
	form_class = forms.AuthenticationForm
	redirect_url = settings.LOGIN_REDIRECT_URL
	template_name = 'accounts/login.html'

	def form_valid(self, form):
		user = form.get_user()
		auth_login(self.request, form.get_user())
		messages.success(self.request, _("Logged in as %(user)s") % {'user': user.get_full_name()})
		return HttpResponseRedirect(self.get_redirect_url())


class Logout(SuccessRedirectMixin, generic.View):
	redirect_url = settings.LOGOUT_REDIRECT_URL

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated():
			messages.success(self.request, _("Logged out"))
		auth_logout(request)
		return HttpResponseRedirect(self.get_redirect_url())


login = Login.as_view()
logout = Logout.as_view()
