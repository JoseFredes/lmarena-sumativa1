PYTHON ?= python3.12
VENV   := .venv
PY     := $(VENV)/bin/python

.PHONY: venv install data validate-dataset test run all clean

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e .
	$(PY) -c "import matplotlib.pyplot"  # builds the font cache once, so notebooks stay silent

data:
	@echo "TODO: dataset download (implemented in src/arena/io.py)"

validate-dataset:
	$(PY) -c "from arena.profile import export_flat_csv; export_flat_csv('data/interim/arena_flat.csv')"
	$(PY) validar_dataset.py data/interim/arena_flat.csv --informe docs/validacion_dataset.md

test:
	$(PY) -m pytest -q

run:
	@echo "TODO: run F1 and F2 notebooks with nbconvert"

all: install data test run

clean:
	rm -rf $(VENV) .pytest_cache
