.PHONY: install test lint
install:
	pip install -r requirements-dev.txt
test:
	pytest -q
lint:
	cfn-lint labs/*/template.yaml
