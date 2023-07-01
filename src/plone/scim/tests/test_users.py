# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from base64 import b64encode
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.scim.interfaces import BASE_PATH
from plone.scim.testing import PLONE_SCIM_FUNCTIONAL_TESTING
import requests
import unittest


CREATE_USER = """
{
  "schemas":["urn:ietf:params:scim:schemas:core:2.0:User"],
  "userName":"bjensen",
  "externalId":"bjensen",
  "name":{
    "formatted":"Ms. Barbara J Jensen III",
    "familyName":"Jensen",
    "givenName":"Barbara"
  }
}
"""


HEADERS = dict(
    Accept="application/scim+json",
    Authorization="Basic {token:s}".format(
        token=b64encode(
            (SITE_OWNER_NAME + ":" + SITE_OWNER_PASSWORD).encode("utf-8")
        ).decode("utf-8")
    ),
)


class TestUsers(unittest.TestCase):
    layer = PLONE_SCIM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_get_users_without_permissions(self):
        url = "/".join([self.portal.absolute_url(), BASE_PATH, "Users"])
        response = requests.get(url, headers=dict(Accept="application/scim+json"))
        self.assertEqual(response.status_code, 401, response.json())

    def test_get_users_without_filter(self):
        url = "/".join([self.portal.absolute_url(), BASE_PATH, "Users"])
        response = requests.get(url, headers=HEADERS)
        self.assertEqual(response.status_code, 200, response.json())

    def test_get_users_with_filter(self):
        url = (
            "/".join([self.portal.absolute_url(), BASE_PATH, "Users"])
            + "?filter=userName Eq test-user"
        )
        response = requests.get(url, headers=HEADERS)
        self.assertEqual(response.status_code, 200, response.json())
