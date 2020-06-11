import string
import pandas as pd
from pandas import read_csv
from pathlib import Path

from benchmark.src.entities.text_block import TextBlock

__cwd = Path.cwd()
PATH_LABELED_SUBMISSIONS = (__cwd / "data/resources/text_block.csv").resolve()
PATH_TEXT_BLOCKS = (__cwd / "data/resources/ArTEMiS_text_block.csv").resolve()
PATH_FEEDBACK = (__cwd / "data/resources/ArTEMiS_feedback.csv").resolve()


def read_labeled_sentences_from_csv():
    submissions = read_csv(PATH_LABELED_SUBMISSIONS)
    sentences = submissions[["text"]].values.flatten()
    ground_truth_clusters = submissions[["manual_cluster_id"]].values.flatten()
    ids = submissions[["id"]].values.flatten()
    return [TextBlock(sentences[i], ground_truth_cluster=ground_truth_clusters[i], id=ids[i]) for i in
            range(len(sentences))]


def read_sentences_feedback_from_csv():
    text_blocks_csv = read_csv(PATH_TEXT_BLOCKS)
    feedback_csv = read_csv(PATH_FEEDBACK)
    result = pd.merge(text_blocks_csv, feedback_csv, left_on="id",  right_on="reference")
    result = result[~result["points"].isnull()]
    result = result[~result["text"].isnull()]
    ids = result[["id"]].values.flatten()[:1000]
    text_blocks = result[["text"]].values.flatten()[:1000]
    points = result[["points"]].values.flatten()[:1000]
    return [TextBlock(text_blocks[i], ground_truth_grade=points[i], id=ids[i]) for i in range(len(text_blocks))]
