# -*- coding: utf-8 -*-
from plone.scim.exceptions import FilterParserException
import re


try:
    from urllib.parse import urlparse
    from urllib.parse import parse_qs
except ImportError:  # python2
    from urlparse import urlparse
    from urlparse import parse_qs


EQ = re.compile(r'([a-z]+)\sEq\s"([^"]+)"|([a-z]+)\sEq\s([^\s]+)', re.I)
SW = re.compile(r'([a-z]+)\sSw\s"([^"]+)"|([a-z]+)\sSw\s([^\s]+)', re.I)

MAPPING = {"externalid": "external_id", "username": "login", "id": "group_id"}


def parse_eq(value):
    """Return parsed query for filter string with 'Eq' condition."""
    result = {}
    match = EQ.match(value)
    if match:
        groups = [g for g in match.groups() if g]
        groups[0] = MAPPING.get(groups[0].lower(), groups[0].lower())
        result[groups[0]] = {"min": groups[1], "max": groups[1]}
    return result


def parse_sw(value):
    """Return parsed query for filter string with 'Sw' condition."""
    result = {}
    match = SW.match(value)
    if match:
        groups = [g for g in match.groups() if g]
        groups[0] = MAPPING.get(groups[0].lower(), groups[0].lower())
        result[groups[0]] = {"min": groups[1], "max": groups[1] + "~"}
    return result


def from_filter(value):
    """Return parsed query from filter string."""
    parsed_query = parse_eq(value) or parse_sw(value)
    if parsed_query:
        return parsed_query
    raise FilterParserException("Unsupported filter: '{query:s}'".format(query=value))


def from_url(url):
    """Return parsed query form url with filter query param."""
    query = parse_qs(urlparse(url).query)
    if "filter" in query:
        for value in query["filter"]:
            return from_filter(value)
    return {}
