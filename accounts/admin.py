# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from .admin_forms import UserCreationForm, UserChangeForm
from .models import User


class UserAdmin(AuthUserAdmin):
	add_form = UserCreationForm
	form = UserChangeForm
	ordering = ('-id', )


admin.site.register(User, UserAdmin)
