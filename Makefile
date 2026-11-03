PYTHON ?= python3.12
VENV   := .venv
PY     := $(VENV)/bin/python

.PHONY: venv install data test run all clean

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

data:
	@echo "TODO: descarga del dataset (se implementa en src/arena/io.py)"

test:
	$(PY) -m pytest -q

run:
	@echo "TODO: ejecutar notebooks de F1 y F2 con nbconvert"

all: install data test run

clean:
	rm -rf $(VENV) .pytest_cache
