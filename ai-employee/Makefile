.PHONY: install test run clean

install:
	pip install -e .
	pip install -r requirements.txt
	playwright install chromium

test:
	python -m pytest tests/ -v

run:
	ai-employee server

clean:
	rm -rf build/ dist/ *.egg-info .eggs/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f data/*.db data/logs/*.log
