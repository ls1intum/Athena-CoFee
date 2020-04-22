FROM python:3.7.7
LABEL author="Anna Kovaleva <anna.kovaleva@tum.de>"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /usr/src/app
VOLUME ["/usr/src/app/logs"]
COPY src/ src/
RUN mkdir -p src/lib/nltk_data \
 && python -m nltk.downloader -d src/lib/nltk_data stopwords wordnet punkt

# Run the image as a non-root user
RUN groupadd -r textseg && useradd --no-log-init -r -g textseg textseg
USER textseg

EXPOSE 8000
CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "src.app"]
