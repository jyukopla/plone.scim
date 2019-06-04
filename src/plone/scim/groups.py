# -*- coding: utf-8 -*-
from plone.scim.utils import validate_request
from plone.scim.utils import view
from Products.Five import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class Groups(BrowserView):
    """Defines SCIM endpoint for /Groups."""

    def __call__(self):
        validate_request(self.request)
        return {}


@view
def create_group(context, request):  # noqa
    """Define SCIM endpoint /Groups for HTTP POST."""
    validate_request(request)
    return {}
