{ pkgs ? import (fetchTarball {
    url = "https://github.com/NixOS/nixpkgs-channels/archive/aade6ded7969ff2173a9eda4cd2f11ef83ca2768.tar.gz";
    sha256 = "1svfmxzznyph9kmg0zjkjwpf9373s9b980ggw4hn1pgni8iw6q48";
  }) {}
 , setup ? import (fetchTarball {
    url = "https://github.com/datakurre/setup.nix/archive/08a51f7fc2cad7f22d50ba36d81529e7e4fec30c.tar.gz";
    sha256 = "15gzkxpwmjfhvcsr6w2nhaz0jlwnl1ary8l5lz6j6fkmg3mwb6db";
  })
#, setup ? import ../setup.nix
, python ? "python3"
, pythonPackages ? builtins.getAttr (python + "Packages") pkgs
, requirements ? ./requirements.nix
}:

let overrides = self: super: {

  "funcsigs" = super."funcsigs".overridePythonAttrs(old: {
    doCheck = false;
  });

  "mock" = super."mock".overridePythonAttrs(old: {
    doCheck = false;
  });

  "zope.testing" = super."zope.testing".overridePythonAttrs(old: {
    postInstall = ''
      rm -f $out/bin/zope-testrunner
    '';
  });

  "plone.dexterity" = super."plone.dexterity".overridePythonAttrs(old: {
    patches = if old.name != "plone.dexterity-2.2.8" then [ ./plone.dexterity.102.patch ] else [];
  });

  "plone.testing" = super."plone.testing".overridePythonAttrs(old: {
    postPatch = if old.name == "plone.testing-4.1.2" then ''
      sed -i "s|from Testing.ZopeTestCase.ZopeLite import _patched as ZOPETESTCASEALERT||g" src/plone/testing/z2.py
      sed -i "s|if ZOPETESTCASEALERT|from Testing.ZopeTestCase.ZopeLite import _patched as ZOPETESTCASEALERT\n        if ZOPETESTCASEALERT|g" src/plone/testing/z2.py
    '' else ''
      sed -i "s|from Testing.ZopeTestCase.ZopeLite import _patched as ZOPETESTCASEALERT||g" src/plone/testing/zope.py
      sed -i "s|if ZOPETESTCASEALERT|from Testing.ZopeTestCase.ZopeLite import _patched as ZOPETESTCASEALERT\n        if ZOPETESTCASEALERT|g" src/plone/testing/zope.py
    '';
  });

  # Will be fixed by updating Products.CMFActionIcons
  "Products.CMFActionIcons" = super."Products.CMFActionIcons".overridePythonAttrs(old: {
    nativeBuildInputs = [ self."eggtestinfo" ];
  });

  # Will be fixed by updating Products.CMFCore
  "Products.CMFCore" = super."Products.CMFCore".overridePythonAttrs(old: {
    nativeBuildInputs = [ self."eggtestinfo" ];
  });

  # Will be fixed by updating jsonschema
  "jsonschema" = super."jsonschema".overridePythonAttrs(old: {
    nativeBuildInputs = [ self."vcversioner" ];
  });

  # Will be fixed by updating nixpkgs
  "testfixtures" = super."testfixtures".overridePythonAttrs(old: {
    patches = [];
  });

  # https://github.com/zopefoundation/z3c.autoinclude/archive/pip.tar.gz
  "z3c.autoinclude" = super."z3c.autoinclude".overridePythonAttrs (old: {
    src = fetchTarball {
      url = "https://github.com/zopefoundation/z3c.autoinclude/archive/8f8c603024979a44b95a3fd104fff02cdb208da1.tar.gz";
      sha256 = "1mf11ivnyjdfmc2vdd01akqwqiss0q8ax624glxrzk8qx46spqqi";
    };
  });

  "zc.buildout" = pythonPackages.zc_buildout_nix.overridePythonAttrs (old: {
    name = super."zc.buildout".name;
    src = super."zc.buildout".src;
    postInstall = ''
      sed -i "s|import sys|import sys\nimport os\nsys.executable = os.path.join(sys.prefix, 'bin', os.path.basename(sys.executable))|" $out/bin/buildout
    '';
  });

  # fix zc.recipe.egg to support zip-installed setuptools
  "zc.recipe.egg" = super."zc.recipe.egg".overridePythonAttrs (old: {
    postPatch = if !pythonPackages.isPy27 then ''
      sed -i "s|return copy.deepcopy(cache_storage\[cache_key\])|import copyreg; import zipimport; copyreg.pickle(zipimport.zipimporter, lambda x: (x.__class__, (x.archive, ))); return copy.deepcopy(cache_storage[cache_key])|g" src/zc/recipe/egg/egg.py
    '' else "";
  });

};

in setup {
  inherit pkgs pythonPackages overrides;
  src = requirements;
  buildInputs = with pkgs; [
    firefox
    geckodriver
  ];
  force = true;
  shellHook = ''
    export PYTHONPATH=$(pwd)/src:$PYTHONPATH
  '';
}
