FROM python:3.7.3
LABEL author="Ngoc-Minh Tran <minh.tran@tum.de>"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /usr/src/app
VOLUME ["/usr/src/app/logs"]
COPY src/ src/
RUN mkdir -p /home/fbvalid/nltk_data \
 && python -m nltk.downloader -d /home/fbvalid/nltk_data stopwords wordnet punkt


# Run the image as a non-root user
RUN groupadd -r fbvalid && useradd --no-log-init -r -g fbvalid fbvalid
USER fbvalid

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "src.app"]
