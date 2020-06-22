import logging
import sys
import matplotlib.pyplot as plt
from benchmark.src.data.data_retriever import read_labeled_sentences_from_csv, read_sentences_feedback_from_csv
from benchmark.src.entities.cluster import Cluster
from benchmark.src.entities.text_block import TextBlock
from benchmark.src.networking.api_services import *
from benchmark.src.plotting import plot_embeddings
from benchmark.src.similarity_measure import SimilarityMeasure, PrecisionRecallSimilarity, GradeBasedSimilarity


def process_text_blocks(text_blocks, courseId = None, plot=True):
    for text_block in text_blocks:
        text_block.clean_text()
    embeddings = embed(text_blocks, courseId=courseId)
    clusters = Cluster.clusters_from_network_response(cluster(embeddings))
    for text_block in text_blocks:
        text_block.extract_cluster(clusters)
        text_block.extract_embedding(embeddings)
    if plot:
        plot_embeddings(text_blocks)
    return text_blocks


def evaluate_by_labeled_sentences(courseId = None):
    text_blocks = read_labeled_sentences_from_csv()
    text_blocks = process_text_blocks(text_blocks, courseId)
    similarity_measure = PrecisionRecallSimilarity(text_blocks)
    similarity_measure.output_results()


def evaluate_by_artemis_data(courseId = None):
    text_blocks = read_sentences_feedback_from_csv(num_sentences=150)
    text_blocks = process_text_blocks(text_blocks, courseId)
    similarity_measure = GradeBasedSimilarity(text_blocks)
    similarity_measure.output_results()


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # evaluate_by_artemis_data(643)
    # evaluate_by_artemis_data()

    evaluate_by_labeled_sentences(1478643)
    evaluate_by_labeled_sentences(81)
    evaluate_by_labeled_sentences()

    plt.show()