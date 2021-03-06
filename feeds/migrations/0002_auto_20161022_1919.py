# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-22 19:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('feeds', '0001_initial'),
	]

	operations = [
		migrations.AddField(
			model_name='userentrystatus',
			name='is_read',
			field=models.BooleanField(db_index=True, default=False, verbose_name='news is readed'),
		),
		migrations.AddField(
			model_name='userentrystatus',
			name='read_time',
			field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='last read time'),
		),
	]
