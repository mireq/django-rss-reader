# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from .forms import ChangeTemplateHiddenForm
from .utils import switch_template


@require_POST
def change(request):
	form = ChangeTemplateHiddenForm(request.POST)
	response = HttpResponseRedirect(request.POST.get('next', reverse('entry_list')))
	if form.is_valid() and 'change_style' in request.POST:
		switch_template(response, **form.cleaned_data)
	return response
