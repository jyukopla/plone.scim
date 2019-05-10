# -*- coding: utf-8 -*-
from plone.scim.interfaces import BASE_PATH
from plone.scim.utils import static_view


@static_view
def user_resource_type(context, request):
    site_url = context.absolute_url()
    base_url = '{site_url:s}/{BASE_PATH:s}'.format(
        site_url=site_url,
        BASE_PATH=BASE_PATH,
    )
    return {
        'schemas': [
            'urn:ietf:params:scim:schemas:core:2.0:ResourceType',
        ],
        'id': 'User',
        'name': 'User',
        'endpoint': '{BASE_PATH:s}/Users'.format(BASE_PATH=BASE_PATH),
        'description': 'User Account',
        'schema': 'urn:ietf:params:scim:schemas:core:2.0:User',
        'schemaExtensions': [{}],
        'meta': {
            'location': '{base_url:s}/v2/ResourceTypes/User'.format(
                base_url=base_url,
            ),
            'resourceType': 'ResourceType',
        },
    }


@static_view
def group_resource_type(context, request):
    site_url = context.absolute_url()
    base_url = '{site_url:s}/{BASE_PATH:s}'.format(
        site_url=site_url,
        BASE_PATH=BASE_PATH,
    )
    return {
        'schemas': [
            'urn:ietf:params:scim:schemas:core:2.0:ResourceType',
        ],
        'id': 'Group',
        'name': 'Group',
        'endpoint': '{BASE_PATH:s}/Groups'.format(BASE_PATH=BASE_PATH),
        'description': 'Group',
        'schema': 'urn:ietf:params:scim:schemas:core:2.0:Group',
        'meta': {
            'location': '{base_url:s}/v2/ResourceTypes/Group'.format(
                base_url=base_url,
            ),
            'resourceType': 'ResourceType',
        },
    }


@static_view
def resource_types(context, request):
    return {
        'totalResults': 2,
        'itemsPerPage': 10,
        'startIndex': 1,
        'schemas': ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
        'Resources': [
            user_resource_type(context, request)(),
            group_resource_type(context, request)(),
        ],
    }
