#!make

all: .venv

.venv: requirements.txt
	python -m venv .venv
	source .venv/bin/activate; pip install -r requirements.txt

start:
	source .venv/bin/activate; python start.py

clean:
	rm -rf .venv

.PHONY: all start clean