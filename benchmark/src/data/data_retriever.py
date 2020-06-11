import string

from pandas import read_csv
from pathlib import Path

from benchmark.src.entities.text_block import TextBlock

__cwd = Path.cwd()
PATH_SUBMISSIONS = (__cwd / "data/resources/text_block.csv").resolve()


def read_sentences_from_csv():
    submissions = read_csv(PATH_SUBMISSIONS)
    sentences = submissions[["text"]].values.flatten()
    ground_truth_clusters = submissions[["manual_cluster_id"]].values.flatten()
    ids = submissions[["id"]].values.flatten()
    return [TextBlock(sentences[i], ground_truth_cluster=ground_truth_clusters[i], id=ids[i]) for i in
            range(len(sentences))]
