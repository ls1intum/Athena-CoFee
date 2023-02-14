#!make

all: venv text_preprocessing nltk models

venv: requirements.txt
	python -m venv .venv
	source .venv/bin/activate; pip install -r requirements.txt --no-deps

text_preprocessing: ../text_preprocessing
	cp -r ../text_preprocessing ./src/

nltk:
	test -d ./.venv/nltk_data && echo "nltk_data exists, nothing to do"; exit 0
	mkdir -p ./.venv/nltk_data
	source .venv/bin/activate; python -m nltk.downloader -d ./.venv/nltk_data stopwords wordnet punkt

models: src/resources/models/Makefile
	@$(MAKE) -C ./src/resources/models

start:
	source .venv/bin/activate; python start.py

clean:
	rm -rf .venv
	rm -rf ./src/text_preprocessing
	rm -rf ./src/resources/models/elmo*