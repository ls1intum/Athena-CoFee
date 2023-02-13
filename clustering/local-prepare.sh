#!/usr/bin/env bash
# prepare running this service without docker

# create local virtual environment
python -m venv .venv

# activate virtual environment
source .venv/bin/activate

# install requirements
pip install -r requirements.txt
