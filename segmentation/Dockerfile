FROM python:3.7.7
LABEL author="Anna Kovaleva <anna.kovaleva@tum.de>"

COPY ./segmentation/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /usr/src/app
COPY ./segmentation/src/ src/
COPY ./text_preprocessing src/text_preprocessing
RUN mkdir -p /usr/lib/nltk_data \
 && python -m nltk.downloader -d /usr/lib/nltk_data stopwords wordnet punkt

# Run the image as a non-root user
RUN groupadd -r textseg && useradd --no-log-init -r -g textseg textseg
RUN mkdir -p /usr/src/app/logs/ && chown -R textseg:textseg /usr/src/app/
VOLUME ["/usr/src/app/logs"]
USER textseg

EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--reload", "src.main:app"]
