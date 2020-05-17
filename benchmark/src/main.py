import logging
import sys

from benchmark.src.data.data_retriever import read_sentences_from_csv
from benchmark.src.entities.cluster import Cluster
from benchmark.src.networking.api_services import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


text_blocks = read_sentences_from_csv()
embeddings = embed(text_blocks)
clusters = Cluster.clusters_from_network_response(cluster(embeddings))
