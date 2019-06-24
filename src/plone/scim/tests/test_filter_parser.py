# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone.scim.filter_parser import from_filter
from plone.scim.filter_parser import from_url
import unittest


class TestFilter(unittest.TestCase):
    def test_filter_username_eq(self):
        query = 'userName Eq "test-user"'
        expected = {"login": {"min": "test-user", "max": "test-user"}}
        self.assertDictEqual(from_filter(query), expected)

    def test_filter_username_eq_icase(self):
        query = 'userName eq "test-user"'
        expected = {"login": {"min": "test-user", "max": "test-user"}}
        self.assertDictEqual(from_filter(query), expected)

    def test_filter_username_sw(self):
        query = 'userName Sw "test-use"'
        expected = {"login": {"min": "test-use", "max": "test-use~"}}
        self.assertDictEqual(from_filter(query), expected)

    def test_filter_external_id_eq(self):
        query = 'externalId Eq "test-use"'
        expected = {"external_id": {"min": "test-use", "max": "test-use"}}
        self.assertDictEqual(from_filter(query), expected)

    def test_filter_external_id_eq_icase(self):
        query = 'externalId eq "test-use"'
        expected = {"external_id": {"min": "test-use", "max": "test-use"}}
        self.assertDictEqual(from_filter(query), expected)

    def test_filter_external_id_sw(self):
        query = 'externalId Sw "test-use"'
        expected = {"external_id": {"min": "test-use", "max": "test-use~"}}
        self.assertDictEqual(from_filter(query), expected)

    def test_filter_from_url(self):
        url = '?filter=userName%20Eq%20"test-user"'
        expected = {"login": {"min": "test-user", "max": "test-user"}}
        self.assertDictEqual(from_url(url), expected)

        url = '?filter=userName+Eq+"test-user"'
        expected = {"login": {"min": "test-user", "max": "test-user"}}
        self.assertDictEqual(from_url(url), expected)

    def test_unsupported_filter(self):
        query = "(meta.resourceType eq User) or (meta.resourceType eq Group)"
        self.assertRaises(Exception, from_filter, query)
