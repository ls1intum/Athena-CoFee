FROM python:3.9
LABEL author="Jan Philip Bernius <janphilip.bernius@tum.de>"

COPY ./embedding_wmt/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -qr /tmp/requirements.txt


WORKDIR /usr/src/app
COPY ./embedding_wmt/src/resources src/resources

RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y install git-lfs

RUN git clone https://huggingface.co/facebook/wmt19-de-en src/resources/models


# Run the image as a non-root user
RUN groupadd -r textemb && useradd --no-log-init -r -g textemb textemb
RUN mkdir -p /usr/src/app/logs/ &&  chown -R textemb:textemb /usr/src/app/
VOLUME ["/usr/src/app/logs"]
USER textemb

EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "src.main:app"]
