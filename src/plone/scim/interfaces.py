# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


BASE_PATH = '@scim'  # registered in protocol.zcml


class IPloneScimLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
