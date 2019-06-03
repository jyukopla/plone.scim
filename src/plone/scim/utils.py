# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Products.Five import BrowserView
from zExceptions import BadRequest
from zope.component import queryUtility
from zope.security.interfaces import IPermission
import json
import scimschema


try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def validate_request(request):
    """Validate if the given request validates against SCIM schema."""
    try:
        scimschema.validate(json.loads(request.BODY))
    except (AssertionError, JSONDecodeError) as e:
        raise BadRequest(e)


def check_permission(permission, obj):
    """Check if reqest has the given permission for the given object."""
    utility = queryUtility(IPermission, name=permission)
    if utility is not None:
        permission = utility.title
    return utility is not None and bool(
        getSecurityManager().checkPermission(permission, obj)  # noqa: P001
    )


def view(func):
    """Wrap method with a simple browser view."""  # noqa

    class View(BrowserView):
        def __call__(self):
            return func(self.context, self.request)

    return View
