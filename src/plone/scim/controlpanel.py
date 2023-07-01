from plone import api
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope import schema
from zope.interface import Interface


class ITokenForm(Interface):
    username = schema.TextLine(
        title="Username",
        description="Should match the user already created having the SCIM-role.",
    )
    timeout = schema.Int(title="Timeout", description="Specified in seconds.")


class TokenForm(form.Form):
    fields = field.Fields(ITokenForm)
    ignoreContext = True

    @button.buttonAndHandler("Get a token")
    def handleGetToken(self, action):
        data, errors = self.extractData()
        if errors:
            return

        user = api.user.get(username=data["username"])
        if user is None:
            self.status = "User not found."
            return

        # Create the token
        plugin = self.context.acl_users["jwt_auth"]

        payload = {}
        payload["fullname"] = user.getProperty("fullname")
        token = plugin.create_token(
            user.getId(), timeout=data.get("timeout"), data=payload
        )

        self.status = "Token for user {}: {}".format(data["username"], token)
