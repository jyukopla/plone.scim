# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import plone.scim


class PloneScimLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=plone.scim)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.scim:default')


PLONE_SCIM_FIXTURE = PloneScimLayer()


PLONE_SCIM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_SCIM_FIXTURE,),
    name='PloneScimLayer:IntegrationTesting',
)


PLONE_SCIM_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_SCIM_FIXTURE,),
    name='PloneScimLayer:FunctionalTesting',
)


PLONE_SCIM_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLONE_SCIM_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='PloneScimLayer:AcceptanceTesting',
)
