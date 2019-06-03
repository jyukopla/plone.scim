# -*- coding: utf-8 -*-
from plone.scim.interfaces import BASE_PATH
from plone.scim.utils import view
import datetime


@view
def service_provider_config(context, request):  # noqa: E507
    site_url = context.absolute_url()
    base_url = "{site_url:s}/{BASE_PATH:s}".format(
        site_url=site_url, BASE_PATH=BASE_PATH
    )
    timestamp = datetime.datetime.now().isoformat().rsplit(".", 1)[0] + "Z"
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "documentationUri": "http://www.simplecloud.info/",
        "patch": {"supported": False},
        "bulk": {"supported": 1000, "maxOperations": 1000, "maxPayloadSize": 1048576},
        "filter": {"supported": True, "maxResults": 200},
        "changePassword": {"supported": False},
        "sort": {"supported": False},
        "etag": {"supported": False},
        "authenticationSchemes": [
            {
                "name": "OAuth Bearer Token",
                "description": "Authentication scheme using the OAuth Bearer Token Standard",
                "specUri": "http://www.rfc-editor.org/info/rfc6750",
                "documentationUri": "https://plonerestapi.readthedocs.io/en/latest/authentication.html#json-web-tokens-jwt",
                "type": "oauthbearertoken",
            },
            {
                "name": "HTTP Basic",
                "description": "Authentication scheme using the HTTP Basic Standard",
                "specUri": "http://www.rfc-editor.org/info/rfc2617",
                "documentationUri": "https://en.wikipedia.org/wiki/Basic_access_authentication",
                "type": "httpbasic",
                "primary": True,
            },
        ],
        "meta": {
            "location": "{base_url:s}/v2/ServiceProviderConfig".format(
                base_url=base_url
            ),
            "resourceType": "ServiceProviderConfig",
            "created": "{timestamp}".format(timestamp=timestamp),
            "lastModified": "{timestamp}".format(timestamp=timestamp),
        },
    }
