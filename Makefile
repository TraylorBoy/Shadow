install:
	pipenv install --dev
	pipenv install --editable .
	pipenv run pre-commit install -t pre-commit
	pipenv run pre-commit install -t pre-push

test:
	pipenv run isort
	pipenv run flake8
	pipenv run black
	pipenv run mypy
	pipenv run pytest

clean logs:
	rm -r shadow/logs/server/
	rm -r shadow/logs/client/

clean cache:
	rm shadow/cache/*
	rm .pytest_cache/*
	rm .mypy_cache/*

run:
	python3 -m shadow

missing:
	pytest --cov --cov-report=term-missing

pre:
	git add .
	pre-commit

init:
	pipenv install --editable .
