FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./tracking/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./tracking/src/ src/

EXPOSE 80
CMD uvicorn --host 0.0.0.0 --port 8000 --reload src.main:app
