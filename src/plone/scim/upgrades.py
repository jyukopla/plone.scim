# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def reload_gs_profile(context):
    """Implement upgrade step for reloading plone.scim GS profile."""
    loadMigrationProfile(context, "profile-plone.scim:default")
