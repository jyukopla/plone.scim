# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from copy import deepcopy
from plone.scim.interfaces import CORE_SCHEMAS
from plone.scim.interfaces import EXTENSION_SCHEMAS
from Products.CMFCore.utils import getToolByName
from scimschema import ScimResponse
from zExceptions import BadRequest
from zope.component import queryUtility
from zope.security.interfaces import IPermission
import json
import logging
import os
import string
import struct

logger = logging.getLogger('plone.scim')


try:
    import secrets

    HAS_SECRETS = True
except ImportError:
    HAS_SECRETS = False


try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def get_source_users(context):
    """Return mutable ZODB User Manager."""
    acl_users = getToolByName(context, "acl_users")
    source_users = acl_users["source_users"]
    return source_users


def get_source_groups(context):
    """Return mutable ZODB Group Manager."""
    acl_groups = getToolByName(context, "acl_users")
    source_groups = acl_groups["source_groups"]
    return source_groups


def check_permission(permission, obj):
    """Check if request has the given permission for the given object."""
    utility = queryUtility(IPermission, name=permission)
    if utility is not None:
        permission = utility.title
    return utility is not None and bool(
        getSecurityManager().checkPermission(permission, obj)  # noqa: P001
    )


def validate_scim_request(request):
    """Validate given request against known SCIM schemas."""
    try:
        assert (
            request.getHeader("content-type") == "application/scim+json"
        ), "Invalid Content-Type. Expecting 'application/scim+json'."
    except AssertionError as e:
        raise BadRequest(str(e))

    try:
        data = json.loads(request.BODY)
        validate_scim_data(data)
        return data
    except (AssertionError, JSONDecodeError) as e:
        detail = str(e)
        if detail.startswith("Response"):
            offset = len("Request")
            detail = "Request" + detail[offset:]
        raise BadRequest(detail)
    except TypeError as e:
        logger.exception("Unexpected exception for:\n{json:s}".format(
            json=json.dumps(data, indent=2),
        ))
        raise BadRequest(str(e))


def validate_scim_data(data):
    """Validate given SCIM request data against known schemas."""
    ScimResponse(
        data=deepcopy(data),
        core_schema_definitions=CORE_SCHEMAS,
        extension_schema_definitions=EXTENSION_SCHEMAS,
    ).validate()


def generate_password(length=32):
    """Generate random password."""
    if HAS_SECRETS:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(length))

    symbols = string.printable.strip()
    return "".join(
        [
            symbols[x * len(symbols) / 256]
            for x in struct.unpack("%dB" % (length,), os.urandom(length))
        ]
    )
