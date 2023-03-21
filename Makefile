.PHONY: install \
        tests \
		lint \
		run

install:
	poetry install

lint:
	bin/run-black.sh && \
    bin/run-flake8.sh && \
    bin/run-mypy.sh

tests:
	poetry run pytest

run: install
	bin/run-demo.sh
