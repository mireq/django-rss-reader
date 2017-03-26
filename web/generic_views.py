# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_ajax_utils.views import JsonResponseMixin


class ApiEndpointMixin(JsonResponseMixin):
	api_actions = {
		'get': {},
		'post': {}
	}

	def render_result(self, result):
		return self.render_json_response({'result': result})

	def render_error(self, error_code, errors=None):
		response = {'error': {'code': error_code}}
		if errors is not None:
			response['error']['errors'] = errors
		return self.render_json_response(response)

	def render_api_actions(self, data, method='get'):
		action = self.api_actions.get(method, {}).get(data.get('action'))
		return None if action is None else getattr(self, action)()
