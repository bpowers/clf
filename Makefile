# get the project name from setup.py
#PROJECT := $(shell grep 'name=' setup.py | head -n1 | cut -d '=' -f 2 | sed "s/['\", ]//g")
PYTHON := $(PWD)/env/bin/python

# first rule in a makefile is the default one, calling it "all" is a
# common GNU Make convention.
all: run

env: Makefile requirements.txt
	@echo "  VENV update"
	@virtualenv env -q -p python2
	@$(PWD)/env/bin/easy_install -q -U distribute
	@$(PWD)/env/bin/easy_install -q -U pip
	$(PWD)/env/bin/pip install -r requirements.txt
	@touch -c env

run: env
	$(PYTHON) ./scrape.py

.PHONY: clean distclean run all
