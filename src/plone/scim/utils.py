# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Products.Five import BrowserView
from zope.component import queryUtility
from zope.security.interfaces import IPermission


def check_permission(permission, obj):
    utility = queryUtility(IPermission, name=permission)
    if utility is not None:
        permission = utility.title
    return bool(
        getSecurityManager().checkPermission(permission, obj),  # noqa: P001
    )


def static_view(func):
    class StaticView(BrowserView):
        def __call__(self):
            return func(self.context, self.request)

    return StaticView
