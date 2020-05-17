import string

from pandas import read_csv
from pathlib import Path

__cwd = Path.cwd()
PATH_SUBMISSIONS = (__cwd / "data/resources/ArTEMiS_submission.csv").resolve()


def read_sentences_from_csv():
    submissions = read_csv(PATH_SUBMISSIONS)
    sentences = [sentence for sentence_array in submissions[['Unnamed: 9']].values for sentence in sentence_array if isinstance(sentence, str)]
    return sentences[:10]
