# -*- coding: utf-8 -*-
from plone.scim.utils import check_permission
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zExceptions import BadRequest
import json
import logging
import transaction


logger = logging.getLogger("plone.scim")


def bad_request(detail="Bad Request."):
    """Return response 400."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "scimType": "invalidSyntax",
        "detail": detail,
        "status": "400",
    }


def unauthorized(
    detail="Authorization failure. The authorization header is invalid or missing.",
):
    """Return response 401."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": detail,
        "status": "401",
    }


def forbidden(detail="Operation is not permitted based on the supplied authorization"):
    """Return response 403."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": detail,
        "status": "403",
    }


def not_found(detail="Resource not found"):
    """Return response 404."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": detail,
        "status": "404",
    }


def server_error(detail):
    """Return response 500 for any endpoint."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": detail,
        "status": "500",
    }


def scim_response(request, response, status_code=200):
    """Configure SCIM response."""
    request.response.setHeader("Content-Type", "application/scim+json")
    request.response.setStatus(status_code)
    return json.dumps(response, indent=2)


class ScimView(BrowserView):
    """SCIM endpoint base view."""

    permission = "plone.scim:ManageUsersAndGroups"

    def __init__(self, context, request, response=None, status_code=200):
        super(ScimView, self).__init__(context, request)
        self.status_code = status_code
        self.response = response

    def render(self):
        """Return response JSON."""
        return self.response

    def __call__(self):
        """Call render and return response or error message."""
        # noinspection PyBroadException
        if self.permission and not check_permission(self.permission, self.context):
            portal_membership = getToolByName(self.context, "portal_membership")
            if portal_membership.isAnonymousUser():
                return scim_response(self.request, unauthorized(), 401)
            return scim_response(self.request, forbidden(), 403)
        try:
            response = self.render()
        except BadRequest as e:  # noqa
            transaction.abort()
            self.status_code = 400
            response = bad_request(str(e))
        except Exception as e:  # noqa
            transaction.abort()
            logger.exception("{exception:s}:".format(exception=str(e)))
            self.status_code = 500
            response = server_error(str(e))

        if self.status_code == 204:
            self.request.response.setStatus(204)
            return ""
        return scim_response(self.request, response, self.status_code)
