# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone.scim.common import scim_response
from plone.scim.testing import PLONE_SCIM_FUNCTIONAL_TESTING
import unittest


class TestUtils(unittest.TestCase):
    layer = PLONE_SCIM_FUNCTIONAL_TESTING

    def test_set_response_headers(self):
        scim_response(self.layer["request"], {}, 200)
        self.assertDictEqual(
            self.layer["request"].response.headers,
            {"content-type": "application/scim+json"},
        )
