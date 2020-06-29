{ plone ? "plone52"
, python ? "python37"
}:

(import ./setup.nix { inherit plone python; }).buildout
