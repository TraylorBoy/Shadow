install:
	pipenv install --dev
	pipenv run pre-commit install -t pre-commit
	pipenv run pre-commit install -t pre-push

test:
	pipenv run isort
	pipenv run flake8
	pipenv run black
	pipenv run mypy
	pipenv run pytest

clean:
	rm -r shadow/logs
	rm -r .pytest_cache
	rm -r .mypy_cache
