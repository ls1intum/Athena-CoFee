from pathlib import Path

import pandas as pd
from pandas import read_csv

from benchmark.src.entities.text_block import TextBlock

__cwd = Path.cwd()
PATH_LABELED_SUBMISSIONS = (__cwd / "data/resources/clustered_text_blocks.csv").resolve()
PATH_TEXT_BLOCKS = (__cwd / "data/resources/ArTEMiS_text_block.csv").resolve()
PATH_FEEDBACK = (__cwd / "data/resources/ArTEMiS_feedback.csv").resolve()


def read_clustered_sentences_from_csv(num_sentences=None):
    submissions = read_csv(PATH_LABELED_SUBMISSIONS)
    submissions = submissions[~submissions["manual_cluster_id"].isnull()]
    sentences = submissions[["text"]].values.flatten()
    ground_truth_clusters = submissions[["manual_cluster_id"]].values.flatten()
    ids = submissions[["id"]].values.flatten()
    if num_sentences is None:
        num_sentences = len(sentences)
    else:
        num_sentences = min(num_sentences, len(sentences))
    return [TextBlock(sentences[i], ground_truth_cluster=ground_truth_clusters[i], id=ids[i]) for i in
            range(num_sentences)]


def read_graded_sentences_from_csv(num_sentences=None):
    text_blocks_csv = read_csv(PATH_TEXT_BLOCKS)
    feedback_csv = read_csv(PATH_FEEDBACK)
    result = pd.merge(text_blocks_csv, feedback_csv, left_on="id",  right_on="reference")
    result = result[~result["points"].isnull()]
    result = result[~result["text"].isnull()]
    ids = result[["id"]].values.flatten()
    text_blocks = result[["text"]].values.flatten()
    points = result[["points"]].values.flatten()
    if num_sentences is None:
        num_sentences = len(text_blocks)
    else:
        num_sentences = min(num_sentences, len(text_blocks))
    return [TextBlock(text_blocks[i], ground_truth_grade=points[i], id=ids[i]) for i in range(num_sentences)]
