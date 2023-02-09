FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY ./tracking/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./tracking/src/ src/

EXPOSE 8000
CMD uvicorn --host 0.0.0.0 --port 8000 src.main:app
