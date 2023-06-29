# -*- coding: utf-8 -*-
from copy import deepcopy
from plone.scim.common import ScimView
from plone.scim.interfaces import BASE_PATH
import json
import os


# pylama:ignore=E501,C0301
# E501,C0301    Line too long


with open(
    os.path.join(os.path.dirname(__file__), "rfc7643", "enterpriseUser.json")
) as fp:
    ENTERPRISE_USER = json.loads(fp.read())

with open(os.path.join(os.path.dirname(__file__), "rfc7643", "group.json")) as fp:
    GROUP_SCHEMA = json.loads(fp.read())

with open(
    os.path.join(os.path.dirname(__file__), "rfc7643", "resourceType.json")
) as fp:
    RESOURCE_TYPE_SCHEMA = json.loads(fp.read())

with open(os.path.join(os.path.dirname(__file__), "rfc7643", "schema.json")) as fp:
    SCHEMA_SCHEMA = json.loads(fp.read())

with open(
    os.path.join(os.path.dirname(__file__), "rfc7643", "serviceProviderConfig.json")
) as fp:
    SERVICE_PROVIDER_CONFIG_SCHEMA = json.loads(fp.read())

with open(os.path.join(os.path.dirname(__file__), "rfc7643", "user.json")) as fp:
    USER_SCHEMA = json.loads(fp.read())


class UserSchema(ScimView):
    """Render User schema."""

    permission = "zope2.View"

    def render(self):
        """Implement /Schemas/User endpoint."""
        site_url = self.context.absolute_url()
        base_url = (
            "{site_url:s}/{BASE_PATH:s}".format(site_url=site_url, BASE_PATH=BASE_PATH)
            + "/v2/Schemas/urn:ietf:params:scim:schemas:core:2.0"
        )
        schema = deepcopy(USER_SCHEMA)
        schema.update(
            {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Schema"],
                "meta": {
                    "resourceType": "Schema",
                    "location": "{base_url:s}:User".format(base_url=base_url),
                },
            }
        )
        return schema


class GroupSchema(ScimView):
    """Render Group schema."""

    permission = "zope2.View"

    def render(self):
        """Implement /Schemas/Group endpoint."""
        site_url = self.context.absolute_url()
        base_url = (
            "{site_url:s}/{BASE_PATH:s}".format(site_url=site_url, BASE_PATH=BASE_PATH)
            + "/v2/Schemas/urn:ietf:params:scim:schemas:core:2.0"
        )
        schema = deepcopy(GROUP_SCHEMA)
        schema.update(
            {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Schema"],
                "meta": {
                    "resourceType": "Schema",
                    "location": "{base_url:s}:Group".format(base_url=base_url),
                },
            }
        )
        return schema


class ServiceProviderConfigSchema(ScimView):
    """Render ServiceProviderConfig schema."""

    permission = "zope2.View"

    def render(self):
        """Implement /Schemas/ServiceProviderConfig endpoint."""
        site_url = self.context.absolute_url()
        base_url = (
            "{site_url:s}/{BASE_PATH:s}".format(site_url=site_url, BASE_PATH=BASE_PATH)
            + "/v2/Schemas/urn:ietf:params:scim:schemas:core:2.0"
        )
        schema = deepcopy(SERVICE_PROVIDER_CONFIG_SCHEMA)
        schema.update(
            {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Schema"],
                "meta": {
                    "resourceType": "Schema",
                    "location": "{base_url:s}:ServiceProviderConfig".format(
                        base_url=base_url
                    ),
                },
            }
        )
        return schema


class ResourceTypeSchema(ScimView):
    """Render ResourceType schema."""

    permission = "zope2.View"

    def render(self):
        """Implement /Schemas/ResourceType endpoint."""
        site_url = self.context.absolute_url()
        base_url = (
            "{site_url:s}/{BASE_PATH:s}".format(site_url=site_url, BASE_PATH=BASE_PATH)
            + "/v2/Schemas/urn:ietf:params:scim:schemas:core:2.0"
        )
        schema = deepcopy(RESOURCE_TYPE_SCHEMA)
        schema.update(
            {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Schema"],
                "meta": {
                    "resourceType": "Schema",
                    "location": "{base_url:s}:ResourceType".format(base_url=base_url),
                },
            }
        )
        return schema


class SchemaSchema(ScimView):
    """Render Schema schema."""

    permission = "zope2.View"

    def render(self):
        """Implement /Schemas/Schema endpoint."""
        site_url = self.context.absolute_url()
        base_url = (
            "{site_url:s}/{BASE_PATH:s}".format(site_url=site_url, BASE_PATH=BASE_PATH)
            + "/v2/Schemas/urn:ietf:params:scim:schemas:core:2.0"
        )
        schema = deepcopy(SCHEMA_SCHEMA)
        schema.update(
            {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Schema"],
                "meta": {
                    "resourceType": "Schema",
                    "location": "{base_url:s}:Schema".format(base_url=base_url),
                },
            }
        )
        return schema


class Schemas(ScimView):
    """Render all schemas."""

    permission = "zope2.View"

    def render(self, schema_view_classes=()):  # noqa: Parameters differ from overridden
        """Implement /Schemas endpoint."""

        # remove non-User and non-Group schemas
        # because at least the compliance utility breaks down
        # if there are no matching resource types.
        schema_view_classes = [
            kls
            for kls in schema_view_classes
            if kls.__name__ in ["UserSchema", "GroupSchema"]
        ]

        return {
            "totalResults": 5,
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "Resources": [
                klass(self.context, self.request).render()
                for klass in schema_view_classes
            ],
        }
