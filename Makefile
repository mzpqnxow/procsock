#
# Use pybuild to create a venv w/o dependencies
#
# If you have dependencies for your venv you want available
# you can set them using requirements.txt
#
# $ mkdir venv; cat > venv/requirements.txt << 'EOF'
# pep8
# pyflakes
# jinja2
# EOF
# $ make
# $ source venv/bin/activate
# $ ...
#
# Copyright (C) 2017 copyright /at/ mzpqnxow.com under the MIT license
# Please see COPYRIGHT for terms
#
PYTHON = /usr/bin/python
VENV_DIR = venv
RM_RF := /bin/rm -rf
PYBOOT := ./pybuild
VENV_FILES := $(VENV_DIR)/lib64 $(VENV_DIR)/bin $(VENV_DIR)/lib

all: $(VENV_DIR)
	@echo "Executing pyboot (`basename $(PYBOOT)` -p $(PYTHON) $(VENV_DIR))"
	@$(PYBOOT) -p $(PYTHON) $(VENV_DIR)

$(VENV_DIR):
	@echo "----"
	@echo "WARN: VENV_DIR does not exist, creating it with no requirements"
	@echo "----"
	@mkdir -p $(VENV_DIR)

clean:
	$(RM_RF) $(VENV_DIR)/bin $(VENV_DIR)/lib $(VENV_DIR)/include $(VENV_DIR)/pip-selfcheck.json $(VENV_FILES)

rebuild: clean all
