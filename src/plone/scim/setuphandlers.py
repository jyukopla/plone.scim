# -*- coding: utf-8 -*-
from BTrees import OOBTree
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    """Define hidden generic setup profiles of plone.scim."""

    def getNonInstallableProfiles(self):  # noqa: R0201
        """Hide uninstall profile from site-creation and quickinstaller."""
        return ["plone.scim:uninstall"]


def post_install(context):
    """Implement post install script."""
    acl_users = getToolByName(context, name="acl_users")

    source_users = acl_users["source_users"]
    source_users._externalid_to_login = OOBTree.OOBTree()  # noqa
    source_users._login_to_externalid = OOBTree.OOBTree()  # noqa

    source_groups = acl_users["source_groups"]
    source_groups._externalid_to_groupid = OOBTree.OOBTree()  # noqa
    source_groups._groupid_to_externalid = OOBTree.OOBTree()  # noqa


def uninstall(context):
    """Implement uninstall script."""
    acl_users = getToolByName(context, name="acl_users")

    source_users = acl_users["source_users"]
    delattr(source_users, "_externalid_to_login")
    delattr(source_users, "_login_to_externalid")

    source_groups = acl_users["source_groups"]
    delattr(source_groups, "_externalid_to_groupid")
    delattr(source_groups, "_groupid_to_externalid")
