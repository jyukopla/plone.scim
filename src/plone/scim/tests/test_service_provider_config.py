# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone.scim.interfaces import BASE_PATH
from plone.scim.testing import PLONE_SCIM_FUNCTIONAL_TESTING  # noqa: E501
import requests
import unittest


class TestServiceProviderConfig(unittest.TestCase):
    layer = PLONE_SCIM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_service_provider_config_endpoint(self):
        url = "/".join([self.portal.absolute_url(), BASE_PATH, "ServiceProviderConfig"])

        response = requests.get(url, headers=dict(Accept="application/scim+json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/scim+json")
