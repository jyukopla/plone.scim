# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone.scim.interfaces import BASE_PATH
from plone.scim.testing import PLONE_SCIM_FUNCTIONAL_TESTING  # noqa: E501
import requests
import unittest


class TestResourceTypes(unittest.TestCase):
    layer = PLONE_SCIM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_resource_types_endpoint(self):
        url = "/".join([self.portal.absolute_url(), BASE_PATH, "ResourceTypes"])

        response = requests.get(url, headers=dict(Accept="application/scim+json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/scim+json")

        data = response.json()
        self.assertIn("Resources", data)
        self.assertEqual(data["totalResults"], len(data["Resources"]))

        for resource in data["Resources"]:
            self.assertIn("meta", resource)
            self.assertIn("location", resource["meta"])

            url = resource["meta"]["location"]
            response = requests.get(url, headers=dict(Accept="application/scim+json"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.headers.get("Content-Type"), "application/scim+json"
            )
