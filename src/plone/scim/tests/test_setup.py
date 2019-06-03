# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_ROLES
from plone.scim.testing import PLONE_SCIM_INTEGRATION_TESTING  # noqa: E501
from Products.CMFCore.utils import getToolByName
import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that plone.scim is properly installed."""

    layer = PLONE_SCIM_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = getToolByName(  # noqa: P001
                self.portal, "portal_quickinstaller"
            )

    def test_product_installed(self):
        """Test if plone.scim is installed."""
        self.assertTrue(self.installer.isProductInstalled("plone.scim"))

    def test_browserlayer(self):
        """Test that IPloneScimLayer is registered."""
        from plone.scim.interfaces import IPloneScimLayer
        from plone.browserlayer import utils

        self.assertIn(IPloneScimLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = PLONE_SCIM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = getToolByName(  # noqa: P001
                self.portal, "portal_quickinstaller"
            )
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["plone.scim"])
        setRoles(self.portal, TEST_USER_ID, TEST_USER_ROLES)

    def test_product_uninstalled(self):
        """Test if plone.scim is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled("plone.scim"))

    def test_browserlayer_removed(self):
        """Test that IPloneScimLayer is removed."""
        from plone.scim.interfaces import IPloneScimLayer
        from plone.browserlayer import utils

        self.assertNotIn(IPloneScimLayer, utils.registered_layers())
