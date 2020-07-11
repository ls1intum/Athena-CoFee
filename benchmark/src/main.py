import logging
import sys

import matplotlib.pyplot as plt

from benchmark.src.data.data_retriever import read_labeled_sentences_from_csv, read_sentences_feedback_from_csv
from benchmark.src.entities.cluster import Cluster
from benchmark.src.entities.text_block import TextBlock
from benchmark.src.networking.api_services import *
from benchmark.src.plotting import plot_embeddings
from benchmark.src.similarity_measure import PrecisionRecallSimilarity, L1Similarity, QWKSimilarity, \
    AdjustedRandIndexSimilarity

__logger = getLogger(__name__)


def process_text_blocks(text_blocks, courseId=None, plot=True, log_textblocks_to_clusters=False,
                        log_cluster_sizes=True):
    embeddings = embed(text_blocks, courseId=courseId)
    clusters = Cluster.clusters_from_network_response(cluster(embeddings))
    for text_block in text_blocks:
        text_block.extract_cluster(clusters)
        text_block.extract_embedding(embeddings)

    if plot:
        plot_embeddings(text_blocks)

    if log_textblocks_to_clusters:
        cluster_to_text = ["cluster {}: {}".format(textblock.computed_cluster.id, textblock.original_text) for textblock in
                           text_blocks]
        cluster_to_text.sort()
        for result in cluster_to_text:
            logger.info(result + "\n")

    if log_cluster_sizes:
        percentage_clustered = 100.0 * len(
            [text_block for text_block in text_blocks if text_block.computed_cluster.id != -1]) / len(text_blocks)
        avg_cluster_size = sum([len(c.block_ids) for c in clusters if c.id != -1]) / len(clusters)
        logger.info("Percentage of clustered sentences: {}".format(percentage_clustered))
        logger.info("Average cluster size: {}".format(avg_cluster_size))

    return text_blocks


def evaluate_by_labeled_sentences(courseId=None):
    text_blocks = read_labeled_sentences_from_csv()
    text_blocks = process_text_blocks(text_blocks, courseId)
    __logger.info("similarity labeled data for course {}".format(courseId))
    PrecisionRecallSimilarity(text_blocks).output_results()
    AdjustedRandIndexSimilarity(text_blocks).output_results()


def evaluate_by_artemis_data(courseId=None):
    text_blocks = read_sentences_feedback_from_csv( num_sentences=750)
    text_blocks = process_text_blocks(text_blocks, courseId)
    __logger.info("similarity grade-based for course {}".format(courseId))
    L1Similarity(text_blocks).output_results()
    QWKSimilarity(text_blocks).output_results()


def plot_sentences(sentences, courseId=None):
    text_blocks = [TextBlock(sentence) for sentence in sentences]
    process_text_blocks(text_blocks, courseId, plot=True)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    sentences = [
        "class diagram depicts the structure of the system",
        "class diagram is a system model",
        "one of the system models is a class diagram",
        "the structure of the system are represented in a class diagram",
        "class diagrams contain classes and relations between them ",
        "class diagram is a UML model",
        "a diagram was presented in class",
        "we didn't deal with diagrams in class ",
        "Diagrams are part of this class",
        "This is a first class flight",
        "there are different classes of diagrams",
        "I booked first class seat on the train",
    ]

    # plot_sentences(sentences, courseId="022")
    # plot_sentences(sentences)
    evaluate_by_labeled_sentences(courseId="021")
    evaluate_by_labeled_sentences( courseId="022")
    evaluate_by_labeled_sentences()

    plt.show()
