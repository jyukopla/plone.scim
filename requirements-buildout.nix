# Generated by pip2nix 0.8.0.dev1
# See https://github.com/johbo/pip2nix

{ pkgs, fetchurl, fetchgit, fetchhg }:

self: super: {
  "PyYAML" = super.buildPythonPackage {
    name = "PyYAML-5.1";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/9f/2c/9417b5c774792634834e730932745bc09a7d36754ca00acf1ccd1ac2594d/PyYAML-5.1.tar.gz";
      sha256 = "15czj11s2bcgchn2jx81k0jmswf2hjxry5cq820h7hgpxiscfss3";
    };
  };
  "argh" = super.buildPythonPackage {
    name = "argh-0.26.2";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/e3/75/1183b5d1663a66aebb2c184e0398724b624cecd4f4b679cb6e25de97ed15/argh-0.26.2.tar.gz";
      sha256 = "0rdv0n2aa181mkrybwvl3czkrrikgzd4y2cri6j735fwhj65nlz9";
    };
  };
  "buildout-requirements" = super.buildPythonPackage {
    name = "buildout-requirements-0.2.2";
    doCheck = false;
    propagatedBuildInputs = [
      self."setuptools"
      self."zc.buildout"
    ];
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/c1/28/2b3103f6d8f3145f310337fd9ec286724878332020c06da34a8c2de3c71d/buildout.requirements-0.2.2.tar.gz";
      sha256 = "1v4vcl7qbvgs8dwbclsnhxdxzjka5gjj197qbnv9p5r4pci2hq8j";
    };
  };
  "eggtestinfo" = super.buildPythonPackage {
    name = "eggtestinfo-0.3";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/e0/8e/77c064957ea14137407e29abd812160eafc41b73a377c30d9e22d76f14fd/eggtestinfo-0.3.tar.gz";
      sha256 = "0s77knsv8aglns4s98ib5fvharljcsya5clf02ciqzy5s794jjsg";
    };
  };
  "lxml" = super.buildPythonPackage {
    name = "lxml-4.3.3";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/7d/29/174d70f303016c58bd790c6c86e6e86a9d18239fac314d55a9b7be501943/lxml-4.3.3.tar.gz";
      sha256 = "141xvx096bh5xm8mhb4nrycgy1fp12ahnklh6h1a2dcf5xlds0sa";
    };
  };
  "pathtools" = super.buildPythonPackage {
    name = "pathtools-0.1.2";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/e7/7f/470d6fcdf23f9f3518f6b0b76be9df16dcc8630ad409947f8be2eb0ed13a/pathtools-0.1.2.tar.gz";
      sha256 = "1h7iam33vwxk8bvslfj4qlsdprdnwf8bvzhqh3jq5frr391cadbw";
    };
  };
  "pillow" = super.buildPythonPackage {
    name = "pillow-6.0.0";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/81/1a/6b2971adc1bca55b9a53ed1efa372acff7e8b9913982a396f3fa046efaf8/Pillow-6.0.0.tar.gz";
      sha256 = "1dgbhamlr5gxk9avfvmq3ivqqp6w9fpp2grinpbvqb03x4n0m740";
    };
  };
  "pyscss" = super.buildPythonPackage {
    name = "pyscss-1.3.5";
    doCheck = false;
    propagatedBuildInputs = [
      self."six"
    ];
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/01/7b/c6bfb2515ed08cbfb76b0e72254f24caf76f25676d72024837a85a1e68f5/pyScss-1.3.5.tar.gz";
      sha256 = "1c6dh299lw4mkkp3qczry8yqslknydks19h0y2qnp9i1q8rmr8hl";
    };
  };
  "pytest-runner" = super.buildPythonPackage {
    name = "pytest-runner-4.4";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/15/0a/1e73c3a3d3f4f5faf5eacac4e55675c1627b15d84265b80b8fef3f8a3fb5/pytest-runner-4.4.tar.gz";
      sha256 = "1x0d9n40lsiphblbs61rdc0d5r31f6vh0vcahqdv0mffakbnrb80";
    };
  };
  "setuptools" = super.buildPythonPackage {
    name = "setuptools-41.0.1";
    doCheck = false;
    nativeBuildInputs = [
      pkgs."unzip"
    ];
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/1d/64/a18a487b4391a05b9c7f938b94a16d80305bf0369c6b0b9509e86165e1d3/setuptools-41.0.1.zip";
      sha256 = "04sns22y2hhsrwfy1mha2lgslvpjsjsz8xws7h2rh5a7ylkd28m2";
    };
  };
  "setuptools-scm" = super.buildPythonPackage {
    name = "setuptools-scm-3.2.0";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/54/85/514ba3ca2a022bddd68819f187ae826986051d130ec5b972076e4f58a9f3/setuptools_scm-3.2.0.tar.gz";
      sha256 = "0n3knn3p1sqlx31k2lahn7z9bacvlv8nhlfidj77vz50bxqlgasj";
    };
  };
  "six" = super.buildPythonPackage {
    name = "six-1.12.0";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/dd/bf/4138e7bfb757de47d1f4b6994648ec67a51efe58fa907c1e11e350cddfca/six-1.12.0.tar.gz";
      sha256 = "0wxs1q74v07ssjywbbm7x6h5v9qx209ld2yfsif4060sxi0h2sni";
    };
  };
  "urllib3" = super.buildPythonPackage {
    name = "urllib3-1.24.2";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/fd/fa/b21f4f03176463a6cccdb612a5ff71b927e5224e83483012747c12fc5d62/urllib3-1.24.2.tar.gz";
      sha256 = "1hwscrsw77vbkzdbw0db74zzf1135521wwccngnlz73hvxrp494s";
    };
  };
  "vcversioner" = super.buildPythonPackage {
    name = "vcversioner-2.16.0.0";
    doCheck = false;
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/c5/cc/33162c0a7b28a4d8c83da07bc2b12cee58c120b4a9e8bba31c41c8d35a16/vcversioner-2.16.0.0.tar.gz";
      sha256 = "16z10sm78jd7ca3jbkgc3q5i8a8q7y1h21q1li21yy3rlhbhrrns";
    };
  };
  "watchdog" = super.buildPythonPackage {
    name = "watchdog-0.9.0";
    doCheck = false;
    propagatedBuildInputs = [
      self."PyYAML"
      self."argh"
      self."pathtools"
    ];
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/bb/e3/5a55d48a29300160779f0a0d2776d17c1b762a2039b36de528b093b87d5b/watchdog-0.9.0.tar.gz";
      sha256 = "07cnvvlpif7a6cg4rav39zq8fxa5pfqawchr46433pij0y6napwn";
    };
  };
  "zc.buildout" = super.buildPythonPackage {
    name = "zc.buildout-2.13.1";
    doCheck = false;
    propagatedBuildInputs = [
      self."setuptools"
    ];
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/3f/92/bf6ddecce944e3dcebfd8af4efef414a7131276b1433afb4f842012ed5ca/zc.buildout-2.13.1.tar.gz";
      sha256 = "110ln5d0zf1wnmqirimjclxjx7krs9wmibfzjmr52fln4rrd051x";
    };
  };
  "zc.recipe.egg" = super.buildPythonPackage {
    name = "zc.recipe.egg-2.0.7";
    doCheck = false;
    propagatedBuildInputs = [
      self."setuptools"
      self."zc.buildout"
    ];
    src = fetchurl {
      url = "https://files.pythonhosted.org/packages/7a/6f/c6871e8490a153c3b44ac43e4a6552d802561a12b4780c7ea088a7ec5ff0/zc.recipe.egg-2.0.7.tar.gz";
      sha256 = "1lz6yjavc7s01bqfn11sk05x0i935cbk312fpf23akk1g44v17mq";
    };
  };
}
