# allennlp is broken starting in 3.10 because of this: https://stackoverflow.com/questions/70013988/importerror-cannot-import-name-mutablemapping-from-collections-usr-local
FROM python:3.9
LABEL author="Jan Philip Bernius <janphilip.bernius@tum.de>"

COPY ./embedding/requirements.txt /tmp/requirements.txt
# scikit-learn needs numpy to already be installed and Cython to be built
RUN pip install --no-cache-dir numpy==1.20 Cython==0.29.34
RUN pip install -r /tmp/requirements.txt --no-cache-dir --no-deps

# install pytorch GPU version or CPU version depending on the build context
ARG USE_GPU=1
# use cpuonly version if USE_GPU is 0
RUN pip install torch==1.13.1 --index-url https://download.pytorch.org/whl/cpu

WORKDIR /usr/src/app
COPY ./embedding/src/resources src/resources
RUN make -C src/resources/models
RUN mkdir -p /usr/lib/nltk_data \
 && python -m nltk.downloader -d /usr/lib/nltk_data stopwords wordnet punkt

# we need to upgrade numpy again for it to be detected by pytorch later
RUN pip install --no-cache-dir numpy==1.24.1

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
