.PHONY: lint
lint:
	uv run ruff format .
	uv run ruff check --fix .
	uv run mypy . --explicit-package-bases
