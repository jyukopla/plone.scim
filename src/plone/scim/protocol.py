# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.scim.common import forbidden
from plone.scim.common import not_found
from plone.scim.common import scim_response
from plone.scim.common import ScimView
from plone.scim.common import server_error
from plone.scim.common import unauthorized
from plone.scim.groups import CreateGroup
from plone.scim.groups import GroupsDelete
from plone.scim.groups import GroupsGet
from plone.scim.groups import GroupsPut
from plone.scim.interfaces import BASE_PATH
from plone.scim.resource_types import GroupResourceType
from plone.scim.resource_types import ResourceTypes
from plone.scim.resource_types import UserResourceType
from plone.scim.schemas import GroupSchema
from plone.scim.schemas import ResourceTypeSchema
from plone.scim.schemas import Schemas
from plone.scim.schemas import SchemaSchema
from plone.scim.schemas import ServiceProviderConfigSchema
from plone.scim.schemas import UserSchema
from plone.scim.service_provider_config import ServiceProviderConfig
from plone.scim.users import CreateUser
from plone.scim.users import UsersDelete
from plone.scim.users import UsersGet
from plone.scim.users import UsersPut
from plone.scim.utils import check_permission
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import logging
import transaction


logger = logging.getLogger("plone.scim")


class SchemasWrapper(ScimView):
    """Render schemas from routing configuration."""

    permission = "zope2.View"

    def render(self):
        view = Schemas(self.context, self.request)
        schema_view_classes = [
            schema["view"] for schema in GET_ENDPOINTS["Schemas"]["mapping"].values()
        ]
        return view.render(schema_view_classes)


class ResourceTypesWrapper(ScimView):
    """Render resource types from routing configuration."""

    permission = "zope2.View"

    def render(self):
        view = ResourceTypes(self.context, self.request)
        resource_type_view_classes = [
            resource_type["view"]
            for resource_type in GET_ENDPOINTS["ResourceTypes"]["mapping"].values()
        ]
        return view.render(resource_type_view_classes)


GET_ENDPOINTS = {
    "ServiceProviderConfig": {
        "view": ServiceProviderConfig,
        "permission": "zope2.View",
    },
    "ResourceTypes": {
        "view": ResourceTypesWrapper,
        "permission": "zope2.View",
        "mapping": {
            "User": {"view": UserResourceType, "permission": "zope2.View"},
            "Group": {"view": GroupResourceType, "permission": "zope2.View"},
        },
    },
    "Schemas": {
        "view": SchemasWrapper,
        "permission": "zope2.View",
        "mapping": {
            "urn:ietf:params:scim:schemas:core:2.0:User": {
                "view": UserSchema,
                "permission": "zope2.View",
            },
            "urn:ietf:params:scim:schemas:core:2.0:Group": {
                "view": GroupSchema,
                "permission": "zope2.View",
            },
            "urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig": {
                "view": ServiceProviderConfigSchema,
                "permission": "zope2.View",
            },
            "urn:ietf:params:scim:schemas:core:2.0:ResourceType": {
                "view": ResourceTypeSchema,
                "permission": "zope2.View",
            },
            "urn:ietf:params:scim:schemas:core:2.0:Schema": {
                "view": SchemaSchema,
                "permission": "zope2.View",
            },
        },
    },
    "Users": {"permission": "plone.scim:ManageUsersAndGroups", "view": UsersGet},
    "Groups": {"permission": "plone.scim:ManageUsersAndGroups", "view": GroupsGet},
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

    # noinspection PyPep8Naming
    def publishTraverse(self, request, name):
        assert request is not None
        route = self.mapping.get(name) or {}
        if isinstance(route, dict):
            self.mapping = route.get("mapping") or {}
            self.permission = route.get("permission")
            self.view = route.get("view")
            if self.view is not None:
                self.view = self.view(self.context, self.request)
            if IPublishTraverse.providedBy(self.view):
                return self.view
            return self
        return ScimView(
            self.context,
            self.request,
            response=not_found("Endpoint '{name:s}' not found".format(name=name)),
            status_code=404,
        )

    def render(self):

        if self.permission and not check_permission(self.permission, self.context):
            portal_membership = getToolByName(self.context, "portal_membership")
            if portal_membership.isAnonymousUser():
                return scim_response(self.request, unauthorized(), 401)
            return scim_response(self.request, forbidden(), 403)
        if self.view is not None:
            try:
                return self.view()
            except Exception as e:  # noqa: Catching too general exception
                transaction.abort()
                logger.exception("{exception:s}:".format(exception=str(e)))
                response = server_error(str(e))
                return scim_response(self.request, response, 500)
        self.request.response.redirect(
            "/".join([self.context.absolute_url(), BASE_PATH, "ServiceProviderConfig"])
        )
        return ""


POST_ENDPOINTS = {
    "Users": {"permission": "plone.scim:ManageUsersAndGroups", "view": CreateUser},
    "Groups": {"permission": "plone.scim:ManageUsersAndGroups", "view": CreateGroup},
}
POST_ENDPOINTS["v2"] = {
    "permission": "plone.scim:ManageUsersAndGroups",
    "mapping": POST_ENDPOINTS.copy(),
}


@implementer(IPublishTraverse)
class Post(Get):
    """Define available SCIM endpoints for HTTP POST."""

    def __init__(self, context, request):
        super(Post, self).__init__(context, request)
        self.mapping = POST_ENDPOINTS


PUT_ENDPOINTS = {
    "Users": {"permission": "plone.scim:ManageUsersAndGroups", "view": UsersPut},
    "Groups": {"permission": "plone.scim:ManageUsersAndGroups", "view": GroupsPut},
}
PUT_ENDPOINTS["v2"] = {
    "permission": "plone.scim:ManageUsersAndGroups",
    "mapping": PUT_ENDPOINTS.copy(),
}


@implementer(IPublishTraverse)
class Put(Get):
    """Define available SCIM endpoints for HTTP PUT."""

    def __init__(self, context, request):
        super(Put, self).__init__(context, request)
        self.mapping = PUT_ENDPOINTS


DELETE_ENDPOINTS = {
    "Users": {"permission": "plone.scim:ManageUsersAndGroups", "view": UsersDelete},
    "Groups": {"permission": "plone.scim:ManageUsersAndGroups", "view": GroupsDelete},
}
DELETE_ENDPOINTS["v2"] = {
    "permission": "plone.scim:ManageUsersAndGroups",
    "mapping": DELETE_ENDPOINTS.copy(),
}


@implementer(IPublishTraverse)
class Delete(Get):
    """Define available SCIM endpoints for HTTP DELETE."""

    def __init__(self, context, request):
        super(Delete, self).__init__(context, request)
        self.mapping = DELETE_ENDPOINTS
