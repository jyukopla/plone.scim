# -*- coding: utf-8 -*-
from plone.scim.common import ScimView
from plone.scim.exceptions import FilterParserException
from plone.scim.filter_parser import from_filter
from plone.scim.interfaces import BASE_PATH
from plone.scim.utils import generate_password
from plone.scim.utils import get_source_users
from plone.scim.utils import validate_scim_request
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IUserAdderPlugin
from zExceptions import NotFound
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


# pylama:ignore=W0212,R1704
# W0212 Access to a protected member
# R1704 Redefining argument with the local name


try:
    from plone.protect.interfaces import IDisableCSRFProtection

    HAS_CSRF_PROTECTION = True
except ImportError:
    HAS_CSRF_PROTECTION = False


def users_post_user_name_not_unique(name):
    """Return response 400 for POST /Users."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "scimType": "uniqueness",
        "detail": "userName '{name:s}' is reserved".format(name=name),
        "status": "400",
    }


def users_get_not_found(name):
    """Return response 404 for GET /Users."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": "Resource '{name:s}' not found".format(name=name),
        "status": "404",
    }


def users_get_bad_request_no_filter():
    """Return response 400 for GET /Users."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "scimType": "invalidFilter",
        "detail": (
            "Only requests with "
            '"?filter=userName Sw needle" or '
            '"?filter=userName Eq needle" or'
            '"?filter=externalId Sw needle" or '
            '"?filter=externalId Eq needle" are supported'
        ),
        "status": "400",
    }


def users_get_ok(context, request, user, external_id):
    """Return response 200 for GET /Users/id."""
    site_url = context.absolute_url()
    base_url = "{site_url:s}/{BASE_PATH:s}".format(
        site_url=site_url, BASE_PATH=BASE_PATH
    )
    response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user.getId(),
        "userName": user.getUserName(),
        "meta": {
            "resourceType": "User",
            "location": "{base_url:s}/v2/Users/{user_id:s}".format(
                base_url=base_url, user_id=user.getId()
            ),
        },
    }
    if user.getProperty("fullname"):
        response.update(
            {
                "displayName": user.getProperty("fullname"),
                "nickName": user.getProperty("fullname"),
                "name": {"formatted": user.getProperty("fullname")},
            }
        )
    if user.getProperty("email"):
        response.update(
            {
                "emails": [
                    {
                        "value": user.getProperty("email"),
                        "type": "work",
                        "primary": True,
                    }
                ]
            }
        )
    if external_id:
        response.update({"externalId": external_id})

    request.response.setHeader("Location", response["meta"]["location"])
    return response


def users_get_multiple_ok(user_tuples):
    """Return response 200 for GET /Users."""
    user_tuples = list(user_tuples)

    def with_external_id(user_, external_id_):
        if external_id_:
            user_.update({"externalId": external_id_})
        return user_

    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(user_tuples),
        "Resources": [
            with_external_id(
                {"id": user.getId(), "userName": user.getUserName()}, external_id
            )
            for user, external_id in user_tuples
        ],
    }


# noinspection PyProtectedMember
def get_user_id_tuples(source_users, login=None, external_id=None, **kwargs):
    """Return user ids by given login or external id."""
    assert isinstance(kwargs, dict)  # pyling
    if login and isinstance(login, dict):
        for login, user_id in source_users._login_to_userid.items(**login):
            yield user_id, source_users._login_to_externalid.get(login)
    elif login and login in source_users._login_to_userid:
        user_id = source_users._login_to_userid[login]
        yield user_id, source_users._externalid_to_login.get(login)

    if external_id and isinstance(external_id, dict):
        for external_id, login in source_users._externalid_to_login.items(
            **external_id
        ):
            if login in source_users._login_to_userid:
                yield source_users._login_to_userid[login], external_id
    elif external_id and external_id in source_users._externalid_to_login:
        login = source_users._externalid_to_login[external_id]
        if login in source_users._login_to_userid:
            yield source_users._login_to_userid[login], external_id


def filter_users(context, query):
    """Return list of member objects from source_users matching query."""
    users = get_source_users(context)
    results = get_user_id_tuples(users, **query)
    portal_membership = getToolByName(context, "portal_membership")
    for user_id, external_id in results:
        yield portal_membership.getMemberById(user_id), external_id


def get_user(context, login):
    """Return (member, external_id) from source_users matching login."""
    acl_users = getToolByName(context, "acl_users")
    source_users = acl_users["source_users"]
    if login in source_users._login_to_userid:
        user_id = source_users._login_to_userid[login]
        external_id = source_users._login_to_externalid.get(login)
        portal_membership = getToolByName(context, "portal_membership")
        return portal_membership.getMemberById(user_id), external_id
    return None, None


# noinspection PyProtectedMember
def delete_user(context, login):
    """Delete user from source_users matching login."""
    acl_users = getToolByName(context, "acl_users")
    source_users = acl_users["source_users"]
    if login in source_users._login_to_userid:
        user_id = source_users._login_to_userid[login]
        source_users.removeUser(user_id)
        external_id = source_users._login_to_externalid.get(login)
        if external_id:
            del source_users._login_to_externalid[login]
            del source_users._externalid_to_login[external_id]
        mutable_properties = acl_users["mutable_properties"]
        mutable_properties.deleteUser(user_id)


@implementer(IPublishTraverse)
class UsersGet(ScimView):
    """Define SCIM endpoint /Users."""

    login = None

    def publishTraverse(self, request, name):
        assert request  # pylint

        if self.login is None:
            self.login = name
        else:
            raise NotFound()
        return self

    def render(self):
        # Named user
        if self.login is not None:
            user, external_id = get_user(self.context, self.login)
            if user is None:
                self.status_code = 404
                return users_get_not_found(self.login)
            return users_get_ok(self.context, self.request, user, external_id)

        # Filtered list of users
        query = self.request.form.get("filter") or ""
        if not query:
            self.status_code = 400
            return users_get_bad_request_no_filter()
        try:
            parsed_query = from_filter(query)
        except FilterParserException:
            self.status_code = 400
            return users_get_bad_request_no_filter()

        return users_get_multiple_ok(filter_users(self.context, parsed_query))


def get_login(data):
    """Return login name from SCIM User."""
    return data["userName"] or data.get("externalId")


def get_external_id(data):
    """Return external_id name from SCIM User."""
    return data.get("externalId")


def get_fullname(data):
    """Return fullname name from SCIM User."""
    return data.get("displayName", (data.get("name") or {}).get("formatted"))


def get_email(data):
    """Return external_id name from SCIM User."""
    try:
        return (
            [row for row in (data.get("emails") or []) if (row or {}).get("primary")]
            or [
                row
                for row in (data.get("emails") or [])
                if (row or {}).get("type") == "work"
            ]
        )[0].get("value")
    except IndexError:
        return None


class CreateUser(ScimView):
    """Implement SCIM endpoint /Users for HTTP POST."""

    # noinspection PyProtectedMember,PyArgumentList
    def render(self):
        data = validate_scim_request(self.request)
        if HAS_CSRF_PROTECTION:
            alsoProvides(self.request, IDisableCSRFProtection)

        # Extract supported data
        login = get_login(data)
        external_id = get_external_id(data)
        fullname = get_fullname(data)
        email = get_email(data)

        # Create user
        portal_membership = getToolByName(self.context, "portal_membership")
        users = get_source_users(self.context)
        if login in users._login_to_userid:
            self.status_code = 400
            return users_post_user_name_not_unique(login)

        # TODO: We may want to support global uniqueness checking later,
        # but now we want to allow overlapping accounts with LDAP

        # if portal_membership.getMemberById(login):
        #     self.status_code = 400
        #     return users_post_user_name_not_unique(login)

        users = IUserAdderPlugin(get_source_users(self.context))
        users.doAddUser(str(login), generate_password(256))
        if external_id:
            users._externalid_to_login[str(external_id)] = str(login)
            users._login_to_externalid[str(login)] = str(external_id)

        # Update user
        user = portal_membership.getMemberById(login)
        user.setMemberProperties({"fullname": fullname, "email": email})

        self.status_code = 201
        return users_get_ok(self.context, self.request, user, external_id)


# noinspection PyProtectedMember
def set_external_id(source_users, login, external_id):
    """Set source_users external id for given login."""
    source_users._externalid_to_login[external_id] = login
    source_users._login_to_externalid[login] = external_id


# noinspection PyProtectedMember
def delete_external_id(source_users, login, external_id):
    """Delete source_users external id from given login."""
    del source_users._externalid_to_login[external_id]
    del source_users._login_to_externalid[login]


@implementer(IPublishTraverse)
class UsersPut(ScimView):
    """Define SCIM endpoint /Users."""

    login = None

    def publishTraverse(self, request, name):
        assert request  # pylint

        if self.login is None:
            self.login = name
        else:
            raise NotFound()
        return self

    def render(self):
        data = validate_scim_request(self.request)
        if HAS_CSRF_PROTECTION:
            alsoProvides(self.request, IDisableCSRFProtection)

        # Named user
        if self.login is not None:
            user, external_id = get_user(self.context, self.login)
        else:
            user, external_id = (None, None)
        if user is None:
            self.status_code = 404
            return users_get_not_found(self.login)

        # Extract supported data
        users = get_source_users(self.context)
        if not external_id:
            external_id = data.get("externalId")
            if external_id:
                users._externalid_to_login[str(external_id)] = str(self.login)  # noqa
                users._login_to_externalid[str(self.login)] = str(external_id)  # noqa
        external_id = get_external_id(data)
        fullname = get_fullname(data)
        email = get_email(data)

        # Update user
        portal_membership = getToolByName(self.context, "portal_membership")
        user = portal_membership.getMemberById(self.login)
        user.setProperties({"fullname": fullname, "email": email})

        return users_get_ok(self.context, self.request, user, external_id)


@implementer(IPublishTraverse)
class UsersDelete(ScimView):
    """Define SCIM endpoint DELETE /Users/name."""

    login = None

    def publishTraverse(self, request, name):
        assert request  # pylint

        if self.login is None:
            self.login = name
        else:
            raise NotFound()
        return self

    def render(self):
        if HAS_CSRF_PROTECTION:
            alsoProvides(self.request, IDisableCSRFProtection)

        # Named user
        if self.login is not None:
            user, external_id = get_user(self.context, self.login)  # noqa: external_id
        else:
            user, external_id = (None, None)  # noqa: external_id unused
        if user is None:
            self.status_code = 404
            return users_get_not_found(self.login)

        delete_user(self.context, self.login)
        self.status_code = 204
        return ""
