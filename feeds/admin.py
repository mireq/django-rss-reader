# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

from .models import Category, Feed, Entry


class CategoryAdmin(admin.ModelAdmin):
	raw_id_fields = ('user',)


class FeedAdmin(admin.ModelAdmin):
	list_display = ('title', 'xml_url',)
	search_fields = ('title', 'xml_url',)


class EntryAdmin(admin.ModelAdmin):
	list_display = ('title', 'guid', 'get_link')

	def get_link(self, obj):
		return format_html('<a href="{}" class="button" target="_blank">{}</a>', obj.link, _("Open"))
	get_link.allow_tags = True
	get_link.short_description = _("Link")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(Entry, EntryAdmin)
