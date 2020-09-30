FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src/ src/

EXPOSE 80
CMD uvicorn --port 80 --host 0.0.0.0 src.main:app
