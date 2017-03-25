# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_ajax_utils.views import JsonResponseMixin


class ApiEndpointMixin(JsonResponseMixin):
	def render_result(self, result):
		return self.render_json_response({'result': result})

	def render_error(self, error_code, message=None):
		response = {'error': {'code': error_code}}
		if message is not None:
			response['error']['message'] = message
		return self.render_json_response(response)
