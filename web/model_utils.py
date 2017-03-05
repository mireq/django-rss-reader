# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def query_model_attribute(instance, attribute):
	attribute_chain = attribute.split('__')
	for attribute in attribute_chain:
		instance = getattr(instance, attribute)
	return instance
