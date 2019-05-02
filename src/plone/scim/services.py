# -*- coding: utf-8 -*-
from plone.rest import Service


class Patch(Service):
    def render(self):
        return '{"message": "PATCH: Hello World!"}'
