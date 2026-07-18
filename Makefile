install:
	uv cache clean tool-example
	uv tool install . --force
