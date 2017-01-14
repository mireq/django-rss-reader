# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import HttpResponseRedirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django_ajax_utils.views import JsonResponseMixin, AjaxRedirectMixin

from .celery import app
from .url_utils import build_url


def format_task(task):
	if task is None:
		return {
			'task': None,
			'status': 'INVALID',
		}
	task_data = {
		'task': task.id,
		'status': task.status
	}
	if task.status == 'SUCCESS':
		data = task.get()
		task_data['data'] = data
	elif task.status == 'PROGRESS':
		if task.result:
			task_data.update(task.result)
	return task_data


class TaskStatusMixin(JsonResponseMixin):
	task_parameter = 'task_id'
	redirect_parameter = 'next'
	redirect_statuses = set(['SUCCESS', 'FAILURE'])

	@cached_property
	def celery_task(self):
		if self.task_parameter in self.request.GET:
			return app.AsyncResult(self.request.GET[self.task_parameter])
		else:
			return None

	@cached_property
	def celery_task_parsed(self):
		return self.format_task_result(self.celery_task)

	def format_task_result(self, task):
		return format_task(task)

	def get_context_data(self, **kwargs):
		ctx = super(TaskStatusMixin, self).get_context_data(**kwargs)
		ctx['task'] = self.celery_task_parsed
		return ctx

	def render_task_status(self):
		return self.render_json_response({
			'celery_task': self.celery_task_parsed,
		})


class TaskRunMixin(TaskStatusMixin):
	task = None

	def get_task_args(self):
		return ()

	def get_task_kwargs(self):
		return self.kwargs

	def task_run(self):
		return self.task.delay(*self.get_task_args(), **self.get_task_kwargs())

	def get_task_success_url(self):
		return None

	def get_task_status_response(self):
		result = self.format_task_result(self.task_run())
		success_url = self.get_task_success_url()
		url_parameters = {'task_id': result['task']}
		if success_url:
			url_parameters['next'] = success_url
		result_url = build_url('celery_task_status', query=url_parameters)
		if self.request.is_ajax():
			return self.render_json_response({'celery_result_url': result_url})
		return HttpResponseRedirect(result_url)


class TaskStatusView(AjaxRedirectMixin, TaskStatusMixin, TemplateView):
	template_name = 'task_status.html'

	def get_redirect_url(self):
		next_url = self.request.GET.get(self.redirect_parameter)
		if not next_url or not self.celery_task:
			return None
		if not self.celery_task_parsed['status'] in self.redirect_statuses:
			return None
		query = {'task_id': self.celery_task_parsed['task']}
		return build_url(next_url, query=query)

	def get(self, request, **kwargs):
		redirect_url = self.get_redirect_url()
		if redirect_url:
			return HttpResponseRedirect(redirect_url)
		if request.is_ajax():
			return self.render_task_status()
		else:
			return super(TaskStatusView, self).get(request, **kwargs)


task_status_view = TaskStatusView.as_view()
