# -*- coding: utf-8 -*-
from plone.scim.common import ScimView
from plone.scim.exceptions import FilterParserException
from plone.scim.filter_parser import from_filter
from plone.scim.interfaces import BASE_PATH
from plone.scim.utils import get_source_groups
from plone.scim.utils import validate_scim_request
from Products.CMFCore.utils import getToolByName
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


def groups_post_group_id_not_unique(name):
    """Return response 400 for POST /Groups."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "scimType": "uniqueness",
        "detail": "id '{name:s}' is reserved".format(name=name),
        "status": "400",
    }


def groups_get_not_found(name):
    """Return response 404 for GET /Groups."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": "Resource '{name:s}' not found".format(name=name),
        "status": "404",
    }


def groups_get_bad_request():
    """Return response 400 for GET /Groups."""
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "scimType": "invalidFilter",
        "detail": (
            "Only requests with "
            '"?filter=id Sw needle" or '
            '"?filter=id Eq needle" or'
            '"?filter=externalId Sw needle" or '
            '"?filter=externalId Eq needle" are supported'
        ),
        "status": "400",
    }


def groups_get_ok(context, request, group, members, external_id):
    """Return response 200 for GET /Groups/id."""
    site_url = context.absolute_url()
    base_url = "{site_url:s}/{BASE_PATH:s}".format(
        site_url=site_url, BASE_PATH=BASE_PATH
    )
    response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "id": group["id"],
        "displayName": group["title"],
        "members": [
            isinstance(member, dict)
            and {
                "value": member["id"],
                "$ref": "{base_url:s}/v2/Groups/{group_id:s}".format(
                    base_url=base_url, group_id=member["id"]
                ),
                "displayName": member["title"],
            }
            or {
                "value": member.getId(),
                "$ref": "{base_url:s}/v2/Users/{user_id:s}".format(
                    base_url=base_url, user_id=member.getId()
                ),
                "displayName": member.getProperty("fullname"),
            }
            for member in members
        ],
        "meta": {
            "resourceType": "Group",
            "location": "{base_url:s}/v2/Groups/{group_id:s}".format(
                base_url=base_url, group_id=group["id"]
            ),
        },
    }
    if external_id:
        response.update({"externalId": external_id})

    request.response.setHeader("Location", response["meta"]["location"])
    return response


def groups_get_multiple_ok(groups):
    """Return response 200 for GET /Groups."""
    groups = list(groups)

    def with_external_id(group, external_id):
        if external_id:
            group.update({"externalId": external_id})
        return group

    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(groups),
        "Resources": [
            with_external_id(
                {"id": group["id"], "displayName": group["title"]}, external_id
            )
            for group, members, external_id in groups
        ],
    }


# noinspection PyProtectedMember
def get_group_tuples(source_groups, group_id=None, external_id=None):
    """Return (group, external_id) tuples by given group_id or external id."""
    if group_id and isinstance(group_id, dict):
        for group_id, group in source_groups._groups.items(**group_id):
            external_id = source_groups._groupid_to_externalid.get(group_id)
            yield group, external_id
    elif group_id and group_id in source_groups._groups:
        yield source_groups._groups[group_id], source_groups._groupid_to_externalid.get(
            group_id
        )

    if external_id and isinstance(external_id, dict):
        for external_id, group_id in source_groups._externalid_to_groupid.items(
            **external_id
        ):
            if group_id in source_groups._groups:
                yield source_groups._groups[group_id], external_id
    elif external_id and external_id in source_groups._externalid_to_groupid:
        group_id = source_groups._externalid_to_groupid[external_id]
        if group_id in source_groups._groups:
            yield source_groups._groups[group_id], external_id


def filter_groups(context, query, start_index, count, include_members=True):
    """Return list of member objects from source_groups matching query."""

    groups = get_source_groups(context)

    # get groups by filter
    if query:
        query = {
            "group_id": query.get("group_id"),
            "external_id": query.get("external_id"),
        }
        results = list(get_group_tuples(groups, **query))
    else:
        results = []
        for group_id, group in groups._groups.items():
            external_id = groups._groupid_to_externalid.get(group_id)
            results.append((group, external_id))

    # paginate!
    if count:
        results = results[start_index : start_index + count]

    portal_membership = getToolByName(context, "portal_membership")
    for group, external_id in results:
        if include_members:
            members = get_members(context, group["id"])
        else:
            members = ()
        yield group, members, external_id


# noinspection PyProtectedMember
def get_members(context, group_id):
    """Return existing members, whether users or other groups."""
    acl_users = getToolByName(context, "acl_users")
    source_users = acl_users["source_users"]
    source_groups = acl_users["source_groups"]
    portal_membership = getToolByName(context, "portal_membership")
    members = source_groups.listAssignedPrincipals(group_id)
    for principal_id, title in members:
        assert title  # pylint
        if principal_id in source_users._login_to_userid:
            yield portal_membership.getMemberById(principal_id)
        elif principal_id in source_groups._groups:
            yield source_groups._groups[principal_id]


# noinspection PyProtectedMember
def get_group(context, group_id, resolve_members=True):
    """Return (group, members, external_id) from source_groups matching group_id."""
    acl_users = getToolByName(context, "acl_users")
    source_groups = acl_users["source_groups"]
    if group_id in source_groups._groups:
        group = source_groups._groups[group_id]
        external_id = source_groups._groupid_to_externalid.get(group_id)
        if resolve_members:
            members = get_members(context, group_id)
        else:
            members = source_groups.listAssignedPrincipals(group_id)
        return group, members, external_id
    return None, (), None


# noinspection PyProtectedMember
def delete_group(context, group_id):
    """Delete group from source_groups matching group_id."""
    acl_users = getToolByName(context, "acl_users")
    source_groups = acl_users["source_groups"]
    if group_id in source_groups._groups:
        source_groups.removeGroup(group_id)
        external_id = source_groups._groupid_to_externalid.get(group_id)
        if external_id:
            delete_external_id(source_groups, group_id, external_id)
        mutable_properties = acl_users["mutable_properties"]
        mutable_properties.deleteUser(group_id)


@implementer(IPublishTraverse)
class GroupsGet(ScimView):
    """Define SCIM endpoint /Groups."""

    group_id = None

    def publishTraverse(self, request, name):
        assert request  # pylint

        if self.group_id is None:
            self.group_id = name
        else:
            raise NotFound()
        return self

    def render(self):
        # Named group
        if self.group_id is not None:
            group, members, external_id = get_group(self.context, self.group_id)
            if group is None:
                self.status_code = 404
                return groups_get_not_found(self.group_id)
            return groups_get_ok(
                self.context, self.request, group, members, external_id
            )

        # Possibly parse the filter query string
        query = self.request.form.get("filter") or ""
        if query:
            try:
                parsed_query = from_filter(query)
            except FilterParserException:
                self.status_code = 400
                return groups_get_bad_request()
        else:
            parsed_query = {}

        # Possibly parse start_index (1-based)
        try:
            start_index = int(self.request.form.get("startIndex"))
            if start_index > 0:
                start_index = start_index - 1
        except (ValueError, TypeError):
            start_index = 0

        # Possibly parse count
        try:
            count = int(self.request.form.get("count")) or None
        except (ValueError, TypeError):
            count = None

        return groups_get_multiple_ok(
            filter_groups(
                self.context, parsed_query, start_index, count, include_members=False
            )
        )


def get_group_id(data):
    """Return group_id name from SCIM Group."""
    return data.get("id") or data.get("externalId") or data.get("displayName")


def get_external_id(data):
    """Return external_id name from SCIM Group."""
    return data.get("externalId") or data.get("displayName")


def get_display_name(data):
    """Return display name from SCIM Group."""
    return data.get("displayName")


def get_added_members(data):
    """Return members for SCIM Group."""
    return data.get("members") or []


class CreateGroup(ScimView):
    """Implement SCIM endpoint POST /Groups."""

    # noinspection PyProtectedMember,PyArgumentList
    def render(self):
        """Implement SCIM endpoint POST /Groups."""
        data = validate_scim_request(self.request, resource_type="Groups")
        if HAS_CSRF_PROTECTION:
            alsoProvides(self.request, IDisableCSRFProtection)

        # Extract supported data
        group_id = get_group_id(data)
        external_id = get_external_id(data)
        display_name = get_display_name(data)
        members = get_added_members(data)

        assert group_id, "'id' or 'externalId' is required"

        # Create group
        groups = get_source_groups(self.context)
        try:
            group = groups.getGroupInfo(group_id)
            if group is not None:
                self.status_code = 400
                return groups_post_group_id_not_unique(group_id)
        except KeyError:
            pass
        groups.addGroup(str(group_id), title=display_name)
        portal_groups = getToolByName(self.context, "portal_groups")
        group = portal_groups.getGroupById(group_id)
        portal_groups.editGroup(group_id, title=display_name)

        for member in members:
            groups.addPrincipalToGroup(str(member["value"]), group_id)

        if external_id:
            set_external_id(groups, group_id, external_id)

        self.status_code = 201
        group, members, external_id = get_group(self.context, group_id)
        return groups_get_ok(self.context, self.request, group, members, external_id)


# noinspection PyProtectedMember
def set_external_id(source_groups, group_id, external_id):
    """Set source_groups external id for given group_id."""
    source_groups._externalid_to_groupid[str(external_id)] = str(group_id)
    source_groups._groupid_to_externalid[str(group_id)] = str(external_id)


# noinspection PyProtectedMember
def delete_external_id(source_groups, group_id, external_id):
    """Delete source_groups external id from given group_id."""
    if external_id in source_groups._externalid_to_groupid:
        del source_groups._externalid_to_groupid[external_id]
    if group_id in source_groups._groupid_to_externalid:
        del source_groups._groupid_to_externalid[group_id]


@implementer(IPublishTraverse)
class GroupsPut(ScimView):
    """Define SCIM endpoint /Groups."""

    group_id = None

    def publishTraverse(self, request, name):
        assert request  # pyflakes

        if self.group_id is None:
            self.group_id = name
        else:
            raise NotFound()
        return self

    def render(self):
        data = validate_scim_request(self.request, resource_type="Groups")
        if HAS_CSRF_PROTECTION:
            alsoProvides(self.request, IDisableCSRFProtection)

        # Named group
        if self.group_id is not None:
            group, members, external_id = get_group(
                self.context, self.group_id, resolve_members=False
            )
        else:
            group, members, external_id = (None, (), None)
        if group is None:
            self.status_code = 404
            return groups_get_not_found(self.group_id or "")

        # Extract supported data
        group_id = get_group_id(data)
        external_id = get_external_id(data)
        display_name = get_display_name(data)
        added_members = get_added_members(data)

        # Update group
        groups = get_source_groups(self.context)
        groups.updateGroup(group_id, title=display_name)
        portal_groups = getToolByName(self.context, "portal_groups")
        group = portal_groups.getGroupById(group_id)
        portal_groups.editGroup(group_id, title=display_name)

        added_members = [member["value"] for member in added_members]
        for principal, title in members:
            assert title  # pyflakes

            if principal not in added_members:
                groups.removePrincipalFromGroup(principal, group_id)
        for principal in added_members:
            groups.addPrincipalToGroup(str(principal), group_id)

        if external_id:
            set_external_id(groups, str(group_id), str(external_id))

        group, members, external_id = get_group(self.context, group_id)
        return groups_get_ok(self.context, self.request, group, members, external_id)


@implementer(IPublishTraverse)
class GroupsDelete(ScimView):
    """Implement SCIM endpoint DELETE /Groups/[id]."""

    group_id = None

    def publishTraverse(self, request, name):
        assert request  # pyflakes

        if self.group_id is None:
            self.group_id = name
        else:
            raise NotFound()
        return self

    def render(self):
        if HAS_CSRF_PROTECTION:
            alsoProvides(self.request, IDisableCSRFProtection)

        # Named group
        if self.group_id is not None:
            groups = get_source_groups(self.context)
            try:
                group = groups.getGroupInfo(self.group_id)
            except KeyError:
                group = None
        else:
            group = None
        if group is None:
            self.status_code = 404
            return groups_get_not_found(self.group_id)

        # Delete
        delete_group(self.context, self.group_id)
        self.status_code = 204
        return ""
