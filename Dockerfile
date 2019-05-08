FROM python:3.7.3

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -qr /tmp/requirements.txt

WORKDIR /usr/src/app
COPY src/ src/

# Run the image as a non-root user
RUN groupadd -r textsim && useradd --no-log-init -r -g textsim textsim
USER textsim

CMD gunicorn src.app
EXPOSE 8000
