install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

lint:
	pylint --disable=R,C,W1203,W0702 *.py

test:
	python -m pytest tests
	
format:
	black *.py

all: install lint test format
