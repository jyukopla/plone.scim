# -*- coding: utf-8 -*-
from plone.scim.common import ScimView
from plone.scim.interfaces import BASE_PATH


# pylama:ignore=W0613
# W0613         Unused argument 'request'


class UserResourceType(ScimView):
    """Render User resource type."""

    permission = "zope2.View"

    def render(self):
        """Return /ResourceTypes/User."""
        site_url = self.context.absolute_url()
        base_url = "{site_url:s}/{BASE_PATH:s}".format(
            site_url=site_url, BASE_PATH=BASE_PATH
        )
        return {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
            "id": "User",
            "name": "User",
            "endpoint": "{BASE_PATH:s}/Users".format(BASE_PATH=BASE_PATH),
            "description": "User Account",
            "schema": "urn:ietf:params:scim:schemas:core:2.0:User",
            "schemaExtensions": [{}],
            "meta": {
                "location": "{base_url:s}/v2/ResourceTypes/User".format(
                    base_url=base_url
                ),
                "resourceType": "ResourceType",
            },
        }


class GroupResourceType(ScimView):
    """Render Group resource type."""

    permission = "zope2.View"

    def render(self):
        """Implement /ResourceTypes/Group endpoint."""
        site_url = self.context.absolute_url()
        base_url = "{site_url:s}/{BASE_PATH:s}".format(
            site_url=site_url, BASE_PATH=BASE_PATH
        )
        return {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
            "id": "Group",
            "name": "Group",
            "endpoint": "{BASE_PATH:s}/Groups".format(BASE_PATH=BASE_PATH),
            "description": "Group",
            "schema": "urn:ietf:params:scim:schemas:core:2.0:Group",
            "meta": {
                "location": "{base_url:s}/v2/ResourceTypes/Group".format(
                    base_url=base_url
                ),
                "resourceType": "ResourceType",
            },
        }


class ResourceTypes(ScimView):
    """Render all resource types."""

    permission = "zope2.View"

    def render(self, resource_type_view_classes=()):  # noqa: Parameters differ
        """Implement /ResourceTypes endpoint."""
        return {
            "totalResults": 2,
            "itemsPerPage": 10,
            "startIndex": 1,
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "Resources": [
                klass(self.context, self.request).render()
                for klass in resource_type_view_classes
            ],
        }
