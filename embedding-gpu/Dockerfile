FROM nvidia/cuda:10.1-runtime-ubuntu18.04
LABEL author="Jan Philip Bernius <janphilip.bernius@tum.de>"

RUN apt-get update && \
    apt-get -y install python3 python3-pip curl pkg-config git cmake && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY ./embedding-gpu/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -qr /tmp/requirements.txt

WORKDIR /usr/src/app
COPY ./embedding-gpu/src/processing/resources src/processing/resources
RUN make -C src/processing/resources/models
RUN mkdir -p /usr/lib/nltk_data \
 && python3 -m nltk.downloader -d /usr/lib/nltk_data stopwords wordnet punkt

COPY ./embedding-gpu/src/ src/
COPY ./text_preprocessing src/processing/text_preprocessing

# Run the image as a non-root user
RUN groupadd -r textemb && useradd --no-log-init -r -g textemb textemb
RUN chown -R textemb:textemb /usr/src/app/
USER textemb

CMD python3 src/main.py
