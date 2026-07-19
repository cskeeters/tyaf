package := $(shell yq '.project.name' pyproject.toml)

install:
	uv cache clean $(package)
	uv tool install . --force

run:
	uv run tool-example
