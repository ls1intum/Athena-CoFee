#!make

all: .venv text_preprocessing ./.venv/nltk_data models

.venv: requirements.txt
	python -m venv .venv
	source .venv/bin/activate; pip install -r requirements.txt --no-deps

text_preprocessing: ../text_preprocessing
	cp -r ../text_preprocessing ./src/

./.venv/nltk_data: .venv
	mkdir -p ./.venv/nltk_data
	source .venv/bin/activate; python -m nltk.downloader -d ./.venv/nltk_data stopwords wordnet punkt

models: ./src/resources/models/Makefile
	@$(MAKE) -C ./src/resources/models

start:
	source .venv/bin/activate; python start.py

clean:
	rm -rf .venv
	rm -rf ./src/text_preprocessing
	rm -rf ./src/resources/models/elmo*

.PHONY: all start clean