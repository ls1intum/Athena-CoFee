FROM python:3.7.7
LABEL author="Jan Philip Bernius <janphilip.bernius@tum.de>"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -qr /tmp/requirements.txt

WORKDIR /usr/src/app
COPY src/ src/
RUN make -C src/resources

# Run the image as a non-root user
RUN groupadd -r textsim && useradd --no-log-init -r -g textsim textsim
RUN mkdir -p /usr/src/app/logs/ && chown -R textsim:textsim /usr/src/app/
VOLUME ["/usr/src/app/logs"]
USER textsim

EXPOSE 8000
CMD gunicorn -b 0.0.0.0:8000 src.app
