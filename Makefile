.PHONY: doctor test lint build docker clean

doctor:
	python -m lazyforge doctor

test:
	python -m pytest -q

lint:
	python -m compileall -q src

build:
	python -m build

docker:
	docker build -t huzjie/lazyforge:latest .

clean:
	rm -rf build dist *.egg-info .pytest_cache __pycache__
	find src -name __pycache__ -type d -exec rm -rf {} +
