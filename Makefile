run := poetry run

.PHONY: test
test:
	$(run) pytest tests/ -n 16 --dist=loadgroup $(ARGS)

.PHONY: typecheck
typecheck:
	$(run) mypy r2s

.PHONY: format
format:
	$(run) black r2s

.PHONY: format-check
format-check:
	$(run) black --check r2s

.PHONY: setup
setup:
	poetry install
	poetry install --extras colcon

.PHONY: update
update:
	poetry update

.PHONY: install-pre-commit
install-pre-commit:
	$(run) pre-commit install
