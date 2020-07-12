from pandas import read_csv
from pathlib import Path
from benchmark.src.entities.text_block import TextBlock
from benchmark.src.entities.feedback_with_text_block import FeedbackWithTextBlock
import itertools

__cwd = Path.cwd()
PATH_SUBMISSIONS = (__cwd / "data/resources/text_block.csv").resolve()
PATH_FEEDBACK = (__cwd / "data/resources/feedback_comments.csv").resolve()


def read_sentences_from_csv():
    submissions = read_csv(PATH_SUBMISSIONS)
    sentences = submissions[["text"]].values.flatten()
    ground_truth_clusters = submissions[["manual_cluster_id"]].values.flatten()
    ids = submissions[["id"]].values.flatten()
    return [TextBlock(sentences[i], ground_truth_cluster=ground_truth_clusters[i], id=ids[i]) for i in
            range(len(sentences))]


def read_feedback_from_csv():
    data = read_csv(PATH_FEEDBACK, sep=";", keep_default_na=False)
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
              range(len(data)) if feedback_texts[i] and cluster_ids[i] and texts[i]]
    return [list(i) for j, i in itertools.groupby(sorted(blocks, key=lambda x: x.submission_id), lambda x: x.submission_id)]

