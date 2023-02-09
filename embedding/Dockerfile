FROM python:3.10.9
LABEL author="Jan Philip Bernius <janphilip.bernius@tum.de>"

COPY ./embedding/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --no-deps -qr /tmp/requirements.txt

WORKDIR /usr/src/app
COPY ./embedding/src/resources src/resources
RUN make -C src/resources/models
RUN mkdir -p /usr/lib/nltk_data \
 && python -m nltk.downloader -d /usr/lib/nltk_data stopwords wordnet punkt

COPY ./embedding/src/ src/
COPY ./text_preprocessing src/text_preprocessing

# Run the image as a non-root user
RUN groupadd -r textemb && useradd --no-log-init -r -g textemb textemb
RUN mkdir -p /home/textemb && chown -R textemb:textemb /home/textemb
RUN mkdir -p /usr/src/app/logs/ && chown -R textemb:textemb /usr/src/app/
VOLUME ["/usr/src/app/logs"]
USER textemb

EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "src.main:app"]
