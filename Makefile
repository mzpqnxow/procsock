#
# Boilerplate pyboot venv build/clean/rebuild Makefile
#
# If you have dependencies for your venv:
# $ mkdir venv; cat > venv/requirements.txt << 'EOF'
# pep8
# pyflakes
# jinja2
# EOF
# $ make
# $ source venv/bin/activate
# $ ...
#

PYTHON = /usr/bin/python
VENV_DIR = venv
RM_RF := /bin/rm -rf
PYBOOT := ./pyboot
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
