from zope import schema
from zope.interface import Interface
from plone.supermodel import model
from z3c.form import form, button, field
from plone import api

class ITokenForm(Interface):
    username = schema.TextLine(title=u"Username", description=u"Should match the user already created having the SCIM-role.")
    timeout = schema.Int(title=u"Timeout", description=u"Specified in seconds.")

class TokenForm(form.Form):
    fields = field.Fields(ITokenForm)
    ignoreContext = True

    @button.buttonAndHandler(u"Get a token")
    def handleGetToken(self, action):
        data, errors = self.extractData()
        if errors:
            return

        user = api.user.get(username=data['username'])
        if user is None:
            self.status = u"User not found."
            return

        # Create the token
        plugin = self.context.acl_users['jwt_auth']

        payload = {}
        payload["fullname"] = user.getProperty("fullname")
        token = plugin.create_token(
            user.getId(),
            timeout=data.get('timeout'),
            data=payload
        )

        self.status = u"Token for user {}: {}".format(data['username'], token)
