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

SPRITES = (
	{
		'name': 'sprites',
		'output': 'img/sprites.png',
		'scss_output': 'css/_sprites.scss',
		'extra_sizes': ((2, '@2x'),),
		'width': 80,
		'height': 80,
		'images': (
			{ 'name': 'white_delete', 'src': 'img/white/delete.png', },
			{ 'name': 'white_favorite', 'src': 'img/white/favorite.png', },
			{ 'name': 'white_folder', 'src': 'img/white/folder.png', },
			{ 'name': 'white_home', 'src': 'img/white/home.png', },
			{ 'name': 'white_left', 'src': 'img/white/left.png', },
			{ 'name': 'white_menu', 'src': 'img/white/menu.png', },
			{ 'name': 'white_right', 'src': 'img/white/right.png', },
			{ 'name': 'white_search', 'src': 'img/white/search.png', },
			{ 'name': 'white_settings', 'src': 'img/white/settings.png', },
			{ 'name': 'white_share', 'src': 'img/white/share.png', },
			{ 'name': 'white_tag', 'src': 'img/white/tag.png', },
			{ 'name': 'white_user', 'src': 'img/white/user.png', },
		),
	},
)
