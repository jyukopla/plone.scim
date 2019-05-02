# Requires .netrc file with
#
# machine repo.kopla.jyu.fi
# login username
# password secret

INDEX_URL ?= https://repo.kopla.jyu.fi/api/pypi/pypi/simple
INDEX_HOSTNAME ?= repo.kopla.jyu.fi

BUILDOUT_CFG ?= buildout.cfg
BUILDOUT_ARGS ?= -N
PYBOT_ARGS ?=

.PHONY: all
all: .installed.cfg

# Cannot be --pure to allow configuring CI build with environment variables
nix-%: requirements.nix .netrc
	nix-shell --option netrc-file .netrc setup.nix -A develop \
	--run "$(MAKE) $*"

.PHONY: nix-shell
nix-shell:
	nix-shell --pure setup.nix -A develop

build: result

.PHONY: check
check: .installed.cfg
	bin/code-analysis

.PHONY: clean
clean:
	rm -rf .installed bin develop-eggs parts

.PHONY: deploy
deploy: dist
	@echo "Not implemented"

.PHONY: dist
dist:
	@echo "Not implemented"

.PHONY: docs
docs: .installed.cfg
	bin/pocompile
	LANGUAGE=fi bin/sphinx-build docs html

.PHONY: format
format: .installed.cfg
	bin/yapf -r -i src
	bin/isort -rc -y src

.PHONY: show
show:
	buildout -c $(BUILDOUT_CFG) $(BUILDOUT_ARGS) annotate

.PHONY: test
test: check
	bin/pocompile
	bin/test --all
#	LANGUAGE=fi bin/pybot $(PYBOT_ARGS) -d parts/test docs

.PHONY: watch
watch: .installed.cfg
	RELOAD_PATH=src bin/instance fg

.PHONY: robot
robot: .installed.cfg
	bin/robot -d parts/test docs

.PHONY: robot-server
robot-server: .installed.cfg
	LANGUAGE=fi RELOAD_PATH=src \
	bin/robot-server plone.scim.testing.SCIM_ACCEPTANCE_TESTING -v

.PHONY: sphinx
sphinx: .installed.cfg
	bin/robot-sphinx-build -d html docs html

###

.installed.cfg: $(wildcard *.cfg)
	buildout -c $(BUILDOUT_CFG) $(BUILDOUT_ARGS)

.netrc:
	@echo machine ${INDEX_HOSTNAME} > .netrc
	@echo login ${PYPI_USERNAME} >> .netrc
	@echo password ${PYPI_PASSWORD} >> .netrc

netrc: .netrc
	ln -s .netrc netrc

result:
	nix-build --option netrc-file .netrc setup.nix -A env

requirements.txt: BUILDOUT_ARGS=buildout:overwrite-requirements-file=true
requirements.txt: requirements-buildout.nix
	nix-shell --pure --option netrc-file .netrc \
	setup.nix -A develop --arg buildout true \
	--run "buildout -c $(BUILDOUT_CFG) $(BUILDOUT_ARGS)"

requirements.nix: requirements.txt requirements-buildout.txt
	@make netrc
	HOME=$(PWD) NIX_CONF_DIR=$(PWD) nix-shell -p libffi nix \
	--run 'nix-shell setup.nix -A pip2nix \
	--run "pip2nix generate -r requirements.txt -r requirements-buildout.txt \
	--index-url $(INDEX_URL) \
	--output=requirements.nix"'

requirements-buildout.nix: requirements-buildout.txt
	nix-shell --pure -p libffi nix \
	--run 'nix-shell setup.nix -A pip2nix \
	--run "pip2nix generate -r requirements-buildout.txt \
	--output=requirements-buildout.nix"'

.PHONY: freeze
freeze:
	@grep "name" requirements.nix |grep -Eo "\"(.*)\""|grep -Eo "[^\"]+"|sed -r "s|-([0-9\.]+)|==\1|g"|grep -v "setuptools="

.PHONY: freeze-buildout
freeze-buildout:
	@grep "name" requirements-buildout.nix |grep -Eo "\"(.*)\""|grep -Eo "[^\"]+"|sed -r "s|-([0-9\.]+)|==\1|g"|grep -v "setuptools="

.PHONY: setup.nix
setup.nix:
	@echo "Updating nixpkgs/nixos-19.03 revision"; \
	rev=$$(curl https://api.github.com/repos/NixOS/nixpkgs-channels/branches/nixos-19.03|jq -r .commit.sha); \
	echo "Updating nixpkgs $$rev hash"; \
	sha=$$(nix-prefetch-url --unpack https://github.com/NixOS/nixpkgs-channels/archive/$$rev.tar.gz); \
	sed -i "2s|.*|    url = \"https://github.com/NixOS/nixpkgs-channels/archive/$$rev.tar.gz\";|" setup.nix; \
	sed -i "3s|.*|    sha256 = \"$$sha\";|" setup.nix;
	@echo "Updating setup.nix revision"; \
	rev=$$(curl https://api.github.com/repos/datakurre/setup.nix/branches/master|jq -r ".commit.sha"); \
	echo "Updating setup.nix $$rev hash"; \
	sha=$$(nix-prefetch-url --unpack https://github.com/datakurre/setup.nix/archive/$$rev.tar.gz); \
	sed -i "6s|.*|    url = \"https://github.com/datakurre/setup.nix/archive/$$rev.tar.gz\";|" setup.nix; \
	sed -i "7s|.*|    sha256 = \"$$sha\";|" setup.nix

.PHONY: upgrade
upgrade:
	nix-shell --pure -p curl gnumake jq nix --run "make setup.nix"
