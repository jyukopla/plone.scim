# -*- coding: utf-8 -*-
from plone.scim.utils import validate_request
from plone.scim.utils import view
from Products.Five import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class Users(BrowserView):
    """Define SCIM endpoint /Users."""

    def __call__(self):
        validate_request(self.request)
        return {}


@view
def create_user(context, request):  # noqa
    """Define SCIM endpoint /Users for HTTP POST."""
    validate_request(request)
    return {}
