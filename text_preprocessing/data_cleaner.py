import re

from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


def get_stop_words(language):
    """Gets stop_words from nltk corpus

    :param language: language for stop words
    :return: list of stop words
    """
    stop_words = set(stopwords.words(language))
    if language == "english":
        new_words = ["using", "show", "result", "large", "also",
                     "iv", "one", "two", "new", "previously", "shown", "would"]
        stop_words = stop_words.union(new_words)
    return stop_words


def clean_data(dataset):
    """Preprocesses documents in dataset

    :param dataset: dictionary of all documents (answers)
    :return: cleaned text of all documents: lemmatized, lower-case, without punctuation
    """
    # Creating a list of stop words in english and german
    stop_words = get_stop_words("english")
    stop_words = stop_words.union(get_stop_words("german"))

    corpus = []
    for submission_id, submission_text in dataset.items():
        text = clean_text(submission_text)
        corpus.append(text)

    return corpus


def clean_text(text, lemmatization=True):
    # Creating a list of stop words in english and german
    stop_words = get_stop_words("english")
    stop_words = stop_words.union(get_stop_words("german"))

    # Remove punctuations
    text = re.sub(r"[^a-zA-Z]", " ", text)
    # Convert to lowercase
    text = text.lower()
    # remove tags
    text = re.sub("&lt;/?.*?&gt;", " &lt;&gt; ", text)
    # remove special characters and digits
    text = re.sub("(\\d|\\W)+", " ", text)
    # Convert to list from string
    text = text.split()
    # Lemmatisation
    lem = WordNetLemmatizer()
    text = [lem.lemmatize(word) if lemmatization else word for word in text if
            word not in
            stop_words]
    text = " ".join(text)

    return text
