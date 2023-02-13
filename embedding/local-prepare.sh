#!/usr/bin/env bash
# prepare running this service without docker

cp -r ../text_preprocessing ./src/

# create local virtual environment
python -m venv .venv

# activate virtual environment
source .venv/bin/activate

# install requirements
pip install -r requirements.txt --no-deps # no-deps is needed because otherwise there would be conflicts

echo "Downloading embedding models..."
make -C ./src/resources/models

echo "Downloading nltk data..."
mkdir -p ./.venv/nltk_data
python -m nltk.downloader -d ./.venv/nltk_data stopwords wordnet punkt
