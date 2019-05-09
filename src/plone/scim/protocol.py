# -*- coding: utf-8 -*-
from plone.rest import Service
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
from plone.scim.utils import check_permission
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.security.interfaces import Forbidden

import json


GET_ENDPOINTS = {
    'ServiceProviderConfig': {
        'view': service_provider_config,
        'permission': 'zope2.View',
    },
    'ResourceTypes': {
        'view': resource_types,
        'permission': 'zope2.View',
        'mapping': {
            'User': {
                'view': user_resource_type,
                'permission': 'zope2.View',
            },
            'Group': {
                'view': group_resource_type,
                'permission': 'zope2.View',
            },
        },
    },
    'Schemas': {
        'view': schemas,
        'permission': 'zope2.View',
        'mapping': {
            'urn:ietf:params:scim:schemas:core:2.0:User': {
                'view': user_schema,
                'permission': 'zope2.View',
            },
            'urn:ietf:params:scim:schemas:core:2.0:Group': {
                'view': group_schema,
                'permission': 'zope2.View',
            },
            'urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig': {
                'view': service_provider_config_schema,
                'permission': 'zope2.View',
            },
            'urn:ietf:params:scim:schemas:core:2.0:ResourceType': {
                'view': resource_type_schema,
                'permission': 'zope2.View',
            },
            'urn:ietf:params:scim:schemas:core:2.0:Schema': {
                'view': schema_schema,
                'permission': 'zope2.View',
            },
        },
    },
}

GET_ENDPOINTS['v2'] = {
    'permission': 'zope2.View',
    'mapping': GET_ENDPOINTS.copy(),
}


@implementer(IPublishTraverse)
class Get(Service):
    def __init__(self, context, request):
        super(Service, self).__init__(context, request)
        self.mapping = GET_ENDPOINTS
        self.view = None

    def publishTraverse(self, request, name):
        route = self.mapping.get(name) or {}
        if route:
            if check_permission(route.get('permission'), self.context):
                self.view = route.get('view')
                self.mapping = route.get('mapping') or {}
                if IPublishTraverse.providedBy(self.view):
                    return self.view
                else:
                    return self
            else:
                raise Forbidden()
        else:
            raise NotFound(self.context, name, request)

    def render(self):
        if self.view is not None:
            if 'application/scim+json' in self.request.getHeader('Accept'):
                content_type = 'application/scim+json'
            else:
                content_type = 'application/json'
            self.request.response.setHeader('Content-Type', content_type)
            return json.dumps(
                self.view(self.context, self.request)(),
                indent=2,
            )
        else:
            self.request.response.redirect(
                '/'.join([
                    self.context.absolute_url(),
                    BASE_PATH,
                    'ServiceProviderConfig',
                ]),
            )
            return ''
