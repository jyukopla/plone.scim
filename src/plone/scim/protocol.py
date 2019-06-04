# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.scim.groups import create_group
from plone.scim.groups import Groups
from plone.scim.interfaces import BASE_PATH
from plone.scim.resource_types import group_resource_type
from plone.scim.resource_types import resource_types
from plone.scim.resource_types import user_resource_type
from plone.scim.schemas import group_schema
from plone.scim.schemas import resource_type_schema
from plone.scim.schemas import schema_schema
from plone.scim.schemas import schemas
from plone.scim.schemas import service_provider_config_schema
from plone.scim.schemas import user_schema
from plone.scim.service_provider_config import service_provider_config
from plone.scim.users import create_user
from plone.scim.users import Users
from plone.scim.utils import check_permission
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.security.interfaces import Forbidden
import json


GET_ENDPOINTS = {
    "ServiceProviderConfig": {
        "view": service_provider_config,
        "permission": "zope2.View",
    },
    "ResourceTypes": {
        "view": resource_types,
        "permission": "zope2.View",
        "mapping": {
            "User": {"view": user_resource_type, "permission": "zope2.View"},
            "Group": {"view": group_resource_type, "permission": "zope2.View"},
        },
    },
    "Schemas": {
        "view": schemas,
        "permission": "zope2.View",
        "mapping": {
            "urn:ietf:params:scim:schemas:core:2.0:User": {
                "view": user_schema,
                "permission": "zope2.View",
            },
            "urn:ietf:params:scim:schemas:core:2.0:Group": {
                "view": group_schema,
                "permission": "zope2.View",
            },
            "urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig": {
                "view": service_provider_config_schema,
                "permission": "zope2.View",
            },
            "urn:ietf:params:scim:schemas:core:2.0:ResourceType": {
                "view": resource_type_schema,
                "permission": "zope2.View",
            },
            "urn:ietf:params:scim:schemas:core:2.0:Schema": {
                "view": schema_schema,
                "permission": "zope2.View",
            },
        },
    },
    "Users": {"permission": "zope2.ManageUsers", "view": Users},
    "Groups": {"permission": "zope2.ManageUsers", "view": Groups},
}

GET_ENDPOINTS["v2"] = {"permission": "zope2.View", "mapping": GET_ENDPOINTS.copy()}


@implementer(IPublishTraverse)
class Get(Service):
    """Define available SCIM endpoints for HTTP GET."""

    def __init__(self, context, request):
        super(Get, self).__init__(context, request)
        self.mapping = GET_ENDPOINTS
        self.permission = None
        self.view = None

    def publishTraverse(self, request, name):
        route = self.mapping.get(name) or {}
        if route:
            self.mapping = route.get("mapping") or {}
            self.permission = route.get("permission")
            self.view = route.get("view")
            if IPublishTraverse.providedBy(self.view):
                return self.view
            return self
        raise NotFound(self.context, name, request)

    def render(self):
        if self.view is not None:
            if not check_permission(self.permission, self.context):
                raise Forbidden()
            if "application/scim+json" in self.request.getHeader("Accept"):
                content_type = "application/scim+json"
            else:
                content_type = "application/json"
            self.request.response.setHeader("Content-Type", content_type)
            return json.dumps(self.view(self.context, self.request)(), indent=2)
        self.request.response.redirect(
            "/".join([self.context.absolute_url(), BASE_PATH, "ServiceProviderConfig"])
        )
        return ""


POST_ENDPOINTS = {
    "Users": {"permission": "zope2.ManageUsers", "view": create_user},
    "Groups": {"permission": "zope2.ManageUsers", "view": create_group},
}


@implementer(IPublishTraverse)
class Post(Get):
    """Define available SCIM endpoints for HTTP POST."""

    def __init__(self, context, request):
        super(Post, self).__init__(context, request)
        self.mapping = POST_ENDPOINTS


PUT_ENDPOINTS = {}


@implementer(IPublishTraverse)
class Put(Get):
    """Define available SCIM endpoints for HTTP PUT."""

    def __init__(self, context, request):
        super(Put, self).__init__(context, request)
        self.mapping = PUT_ENDPOINTS
