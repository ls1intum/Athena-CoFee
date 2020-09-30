import logging
import sys
import matplotlib.pyplot as plt
from benchmark.src.data.data_retriever import read_labeled_sentences_from_csv, read_sentences_feedback_from_csv, \
    read_feedback_consistency_from_csv, write_feedback_inconsistencies_to_csv
from benchmark.src.entities.cluster import Cluster
from benchmark.src.entities.text_block import TextBlock
from benchmark.src.networking.api_services import *
from benchmark.src.plotting import plot_embeddings
from benchmark.src.similarity_measure import PrecisionRecallSimilarity, GradeBasedSimilarity

__logger = getLogger(__name__)


def process_text_blocks(text_blocks, courseId=None, plot=True, log_clusters=False):
    embeddings = embed(text_blocks, courseId=courseId)
    clusters = Cluster.clusters_from_network_response(cluster(embeddings))
    for text_block in text_blocks:
        text_block.extract_cluster(clusters)
        text_block.extract_embedding(embeddings)
    if plot:
        plot_embeddings(text_blocks)
    if log_clusters:
        cluster_to_text = ["cluster {}: {}".format(textblock.cluster.id, textblock.original_text) for textblock in
                           text_blocks]
        cluster_to_text.sort()
        for result in cluster_to_text:
            logger.info(result + "\n")
    return text_blocks


def evaluate_by_labeled_sentences(courseId=None):
    text_blocks = read_labeled_sentences_from_csv()
    text_blocks = process_text_blocks(text_blocks, courseId)
    similarity_measure = PrecisionRecallSimilarity(text_blocks)
    __logger.info("similarity labeled data for course {}".format(courseId))
    similarity_measure.output_results()


def evaluate_by_artemis_data(courseId=None):
    text_blocks = read_sentences_feedback_from_csv(num_sentences=1000)
    text_blocks = process_text_blocks(text_blocks, courseId)
    similarity_measure = GradeBasedSimilarity(text_blocks)
    __logger.info("similarity grade-based for course {}".format(courseId))
    similarity_measure.output_results()


def plot_sentences(sentences, courseId=None):
    text_blocks = [TextBlock(sentence) for sentence in sentences]
    process_text_blocks(text_blocks, courseId, plot=True)


def feedback_consistency_test(exercise_id):
    data = read_feedback_consistency_from_csv()
    inconsistencies = check_feedback_consistency(feedback_with_text_blocks=data, exercise_id=exercise_id)
    write_feedback_inconsistencies_to_csv(inconsistencies)


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

    feedback_consistency_test('1')

    evaluate_by_labeled_sentences(1478643)
    evaluate_by_labeled_sentences(81)
    evaluate_by_labeled_sentences()

    plt.show()
