# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import RememberToken
from web.celery import app


@app.task
def clean_remember_tokens():
	RememberToken.objects.clean_remember_tokens()
