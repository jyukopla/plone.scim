from Testing.makerequest import makerequest
from zope.site.hooks import setSite

app = makerequest(app)
site = app['Plone']

setSite(site)
jwt_auth = site.acl_users["jwt_auth"]
jwt_auth.create_token("admin", timeout=1231231312)
