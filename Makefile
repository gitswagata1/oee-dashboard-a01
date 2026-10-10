help:
	@echo "Available commands:"
	@echo "  lint    - Run flake8 linter"
	@echo "  test    - Run pytest"
	@echo "  clean   - Remove cache files"

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

test:
	pytest -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

.PHONY: help lint test clean
