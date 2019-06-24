# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from scimschema.core_schemas import load_dict
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import os


BASE_PATH = "@scim"
CORE_SCHEMAS = load_dict(path=os.path.join(os.path.dirname(__file__), "rfc7643"))
EXTENSION_SCHEMAS = {}


class IPloneScimLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
