FROM python:3.10.9
LABEL author="Jan Philip Bernius <janphilip.bernius@tum.de>"

COPY ./clustering/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -qr /tmp/requirements.txt
# additional flag needed in hdbscan 0.8.29, see https://github.com/scikit-learn-contrib/hdbscan/issues/457
RUN pip install --no-cache-dir hdbscan==0.8.29 --no-binary :all: --use-feature=no-binary-enable-wheel-cache

WORKDIR /usr/src/app
COPY ./clustering/src/ src/

# Run the image as a non-root user
RUN groupadd -r textsim && useradd --no-log-init -r -g textsim textsim
RUN mkdir -p /usr/src/app/logs/ && chown -R textsim:textsim /usr/src/app/
VOLUME ["/usr/src/app/logs"]
USER textsim

EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "src.main:app"]
