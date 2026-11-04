PYTHON    ?= python3.12
VENV      := .venv
PY        := $(VENV)/bin/python
EVIDENCE  := docs/evidence
NOTEBOOKS := $(wildcard F1/*.ipynb) $(wildcard F2/*.ipynb)

.PHONY: venv install data validate-dataset test run evidence metadata all clean

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e .
	$(PY) -c "import matplotlib.pyplot"  # builds the font cache once, so notebooks stay silent

# Downloads what is missing and checks every file against data/raw/CHECKSUMS.txt.
data:
	$(PY) -c "from arena.io import ensure_dataset; print(ensure_dataset())"

validate-dataset:
	$(PY) -c "from arena.profile import export_flat_csv; export_flat_csv('data/interim/arena_flat.csv')"
	$(PY) validar_dataset.py data/interim/arena_flat.csv --informe docs/validacion_dataset.md

# Runs the tests and keeps the output as evidence; the exit status is pytest's.
test:
	@mkdir -p $(EVIDENCE)
	@$(PY) -m pytest -q > $(EVIDENCE)/pytest.txt 2>&1; status=$$?; cat $(EVIDENCE)/pytest.txt; exit $$status

# Executes every notebook in place and keeps the log as evidence.
run:
	@mkdir -p $(EVIDENCE)
	@: > $(EVIDENCE)/nbconvert.txt
	@for nb in $(NOTEBOOKS); do \
		echo "== $$nb" | tee -a $(EVIDENCE)/nbconvert.txt; \
		$(PY) -m jupyter nbconvert --to notebook --execute --inplace --KernelManager.transport=ipc $$nb >> $(EVIDENCE)/nbconvert.txt 2>&1 \
			|| { echo "FAILED: $$nb"; tail -20 $(EVIDENCE)/nbconvert.txt; exit 1; }; \
	done

# Environment snapshot: interpreter, git state and every installed package.
evidence:
	@mkdir -p $(EVIDENCE)
	@{ $(PY) --version; echo "commit: $$(git rev-parse --short HEAD) branch: $$(git branch --show-current)"; $(PY) -m pip freeze; } > $(EVIDENCE)/entorno.txt
	@echo "wrote $(EVIDENCE)/entorno.txt"

metadata:
	$(PY) -c "from arena.env import write_phase_metadata, write_project_metadata; write_phase_metadata('docs/metadatos_fase1.json', 'F1'); write_project_metadata('docs/metadatos_proyecto.csv')"

all: install data test run evidence

clean:
	rm -rf $(VENV) .pytest_cache
