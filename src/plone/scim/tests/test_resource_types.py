# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone.scim.interfaces import BASE_PATH
from plone.scim.testing import PLONE_SCIM_FUNCTIONAL_TESTING  # noqa: E501

import requests
import unittest


class TestResourceTypes(unittest.TestCase):
    layer = PLONE_SCIM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_service_provider_config(self):
        response = requests.get(
            '/'.join([
                self.portal.absolute_url(),
                BASE_PATH,
                'ServiceProviderConfig',
            ]),
            headers=dict(Accept='application/json'),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('Content-Type'),
            'application/json',
        )
        # schema_path = os.path.join(
        #     os.path.dirname(__file__), '..', 'rfc7643',
        #     'serviceProviderConfig.json'
        # )
        # with open(schema_path) as fp:
        #     schema = json.loads(fp.read())
        # data = response.json()
        # validate(instance=data, schema=schema)
