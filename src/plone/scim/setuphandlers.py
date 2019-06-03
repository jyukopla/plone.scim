# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


# pylama:ignore=W0613
# W0613         Unused argument 'request'


@implementer(INonInstallable)
class HiddenProfiles(object):
    """Define hidden generic setup profiles of plone.scim."""

    def getNonInstallableProfiles(self):  # noqa: R0201
        """Hide uninstall profile from site-creation and quickinstaller."""
        return ["plone.scim:uninstall"]


def post_install(context):
    """Implement post install script."""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Implement uninstall script."""
    # Do something at the end of the uninstallation of this package.
