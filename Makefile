install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

lint:
	pylint --disable=R,C,W1203,W0702 *.pylint

test:
	python -m pytest -vv --cov=app test_*.py

format:
	black *.py

all:
	install lint test format