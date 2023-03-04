# create environment for the project

env:
	python3 -m venv .venvbw && source .venvbw/bin/activate && pip install -r requirements.txt

env-win:
	python3 -m venv .venvbw && .venvbw\Scripts\activate && pip install -r requirements.txt


# tests 

ci-test-py:
	python3 -m pytest --cov=src --cov-report=xml --cov-report=term-missing --cov-fail-under=100 tests

ci-test-js:
	npm test --prefix ./src

ci-test: ci-test-py ci-test-js


