# -*- coding: utf-8 -*-
from __future__ import unicode_literals

ASSETS = {
	'utils': {
		'js': 'static://django_ajax_utils/js/utils.js',
	},
	'utils_ajax': {
		'js': 'static://django_ajax_utils/js/utils_ajax.js',
		'depends': ['utils'],
	},
	'pjax': {
		'js': 'static://django_ajax_utils/js/pjax.js',
		'depends': ['utils_ajax'],
	},
	'app': {
		'depends': ['utils', 'utils_ajax', 'pjax'],
		'js': [
			'static://js/app.js',
		]
	},
}
