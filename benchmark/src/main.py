import logging
import sys

from benchmark.src.data.data_retriever import read_sentences_from_csv
from benchmark.src.entities.cluster import Cluster
from benchmark.src.networking.api_services import *
from benchmark.src.similarity_measure import SimilarityMeasure
from clustering.src.entities import TextBlock

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


text_blocks = read_sentences_from_csv()
for text_block in text_blocks:
    text_block.clean_text()
embeddings = embed(text_blocks, courseId=1602)
clusters = Cluster.clusters_from_network_response(cluster(embeddings))
for text_block in text_blocks:
    text_block.extract_cluster(clusters)
similarity_measure = SimilarityMeasure(text_blocks)
logger.info('Number of Clusters is {}'.format(len(clusters)))
logger.info('The achieved precision is {}'.format(similarity_measure.precision))
logger.info('The achieved recall is {}'.format(similarity_measure.recall))
logger.info('The achieved F1_score is {}'.format(similarity_measure.f1_score))



