# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.apps import AppConfig as CoreAppConfig
from django.utils.encoding import force_text


class AppConfig(CoreAppConfig):
	name = 'web'
	verbose_name = 'web'

	def ready(self):
		self.patch_migrations()

	def patch_migrations(self):
		def unexpand_tabs(text):
			for length in range(16, 0, -4):
				rx = re.compile('^' + '[ ]' * length, re.MULTILINE)
				text = rx.sub('\t' * (length // 4), force_text(text))
			return text

		from django.db.migrations.writer import MigrationWriter

		old_as_string = MigrationWriter.as_string

		def as_string(self):
			return unexpand_tabs(old_as_string(self))

		MigrationWriter.as_string = as_string
