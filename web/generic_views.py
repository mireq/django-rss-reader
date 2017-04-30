# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import HttpResponseBadRequest
from django_ajax_utils.views import JsonResponseMixin


class ApiEndpointMixin(JsonResponseMixin):
	api_actions = {
		'get': [],
		'post': []
	}

	def render_result(self, result, **kwargs):
		result_data = {'result': result}
		result_data.update(kwargs)
		return self.render_json_response(result_data)

	def render_error(self, error_code, errors=None):
		response = {'error': {'code': error_code}}
		if errors is not None:
			response['error']['errors'] = errors
		return self.render_json_response(response)

	def render_api_actions(self, data, method):
		action = data.get('action')
		if action not in self.api_actions.get(method, []):
			action = None
		return None if action is None else getattr(self, action)()

	def get(self, request, *args, **kwargs):
		return self.render_api_actions(request.GET, 'get') or HttpResponseBadRequest("Unknown action")

	def post(self, request, *args, **kwargs):
		return self.render_api_actions(request.POST, 'post') or HttpResponseBadRequest("Unknown action")
