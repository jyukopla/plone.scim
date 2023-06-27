FROM plone/plone-backend:6.0.1

# Install package to initialize & configure the database
COPY . /addons/plone.scim
RUN /app/bin/pip install /addons/plone.scim
RUN echo "<include package=\"plone.scim\" file=\"configure.zcml\" />" > /app/etc/package-includes/plone.scim-configure.zcml

