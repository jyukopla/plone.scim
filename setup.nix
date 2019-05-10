{ pkgs ? import (fetchTarball {
    url = "https://github.com/NixOS/nixpkgs-channels/archive/7bb74e653654dbf9206e751574b5132b15f46bb5.tar.gz";
    sha256 = "1dbdy4f58yqz4l67n032184rx7ci94hx3wl52c8h2bg06awkzq87";
  }) {}
 , setup ? import (fetchTarball {
    url = "https://github.com/datakurre/setup.nix/archive/b453d65d700bf1e709538c03f5c67c3a01f6d406.tar.gz";
    sha256 = "07qavdvv4qxs3fcvb6dwlyh23bvc0dgwx4pw339rsdv21zg60cv2";
  })
#, setup ? import ../setup.nix
, python ? "python3"
, pythonPackages ? builtins.getAttr (python + "Packages") pkgs
, requirements ? ./requirements.nix
}:

let overrides = self: super: {

  # TODO: why tests failed with Plone 4.3 versions...
  "funcsigs" = super."funcsigs".overridePythonAttrs(old: {
    doCheck = false;
  });

  # TODO: why tests failed with Plone 4.3 versions...
  "mock" = super."mock".overridePythonAttrs(old: {
    doCheck = false;
  });

  # Should be fixed with new plone.dexterity release
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

  # should be fixed by updating jsonschema
  "jsonschema" = super."jsonschema".overridePythonAttrs(old: {
    nativeBuildInputs = [ self."vcversioner" ];
  });

  # should be fixed by updating nixpkgs
  "testfixtures" = super."testfixtures".overridePythonAttrs(old: {
    patches = [];
  });

  # fix zc.buildout to generate scripts with nix wrapped python env
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
