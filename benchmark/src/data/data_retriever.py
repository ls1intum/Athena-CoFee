import pandas as pd
from pandas import read_csv
from pathlib import Path
from benchmark.src.entities.text_block import TextBlock
from benchmark.src.entities.feedback_with_text_block import FeedbackWithTextBlock
import itertools

__cwd = Path.cwd()
PATH_LABELED_SUBMISSIONS = (__cwd / "data/resources/text_block.csv").resolve()
PATH_TEXT_BLOCKS = (__cwd / "data/resources/ArTEMiS_text_block.csv").resolve()
PATH_FEEDBACK = (__cwd / "data/resources/ArTEMiS_feedback.csv").resolve()
PATH_FEEDBACK_CONSISTENCY = (__cwd / "data/resources/feedback.csv").resolve()
PATH_FEEDBACK_CONSISTENCY_OUTPUT = (__cwd / "data/resources/feedback_inconsistencies.csv").resolve()


def read_labeled_sentences_from_csv(num_sentences=None):
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


def read_sentences_feedback_from_csv(num_sentences=None):
    text_blocks_csv = read_csv(PATH_TEXT_BLOCKS)
    feedback_csv = read_csv(PATH_FEEDBACK)
    result = pd.merge(text_blocks_csv, feedback_csv, left_on="id", right_on="reference")
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


def read_feedback_consistency_from_csv():
    data = read_csv(PATH_FEEDBACK_CONSISTENCY, sep=";", keep_default_na=False)
    feedback_ids = data[["feedback_id"]].values.flatten()
    feedback_texts = data[["feedback_text"]].values.flatten()
    feedback_scores = data[["score"]].values.flatten()
    references = data[["reference"]].values.flatten()
    ids = data[["textblock_id"]].values.flatten()
    texts = data[["textblock_text"]].values.flatten()
    submission_ids = data[["submission_id"]].values.flatten()
    cluster_ids = data[["cluster_id"]].values.flatten()
    blocks = [FeedbackWithTextBlock(textblock_id=ids[i], submission_id=submission_ids[i], cluster_id=cluster_ids[i],
                                    text=texts[i], feedback_id=feedback_ids[i], feedback_score=feedback_scores[i],
                                    feedback_text=feedback_texts[i], reference=references[i]) for i in
              range(len(data)) if feedback_texts[i] and cluster_ids[i] and texts[i] and not feedback_texts[i] == ' ']
    return [list(i) for j, i in
            itertools.groupby(sorted(blocks, key=lambda x: x.submission_id), lambda x: x.submission_id)]


def write_feedback_inconsistencies_to_csv(inconsistencies):
    df = pd.DataFrame(list(itertools.chain.from_iterable(inconsistencies)),
                      columns=['firstFeedbackId', 'secondFeedbackId', 'type'])
    df.to_csv(PATH_FEEDBACK_CONSISTENCY_OUTPUT, index=False, header=True)
