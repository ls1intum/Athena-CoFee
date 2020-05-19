import re

import nltk.data
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


def get_stop_words(language):
    """Gets stop_words from nltk corpus

    :param language: language for stop words
    :return: list of stop words
    """
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt')
    stop_words = set(stopwords.words(language))
    if language == "english":
        new_words = ["using", "show", "result", "large", "also",
                     "iv", "one", "two", "new", "previously", "shown", "would"]
        stop_words = stop_words.union(new_words)
    return stop_words


def clean_data(sentence):
    # Creating a list of stop words in english and german
    stop_words = get_stop_words("english")
    stop_words = stop_words.union(get_stop_words("german"))

    # join seperated words
    sentence.replace('-', '')
    # Convert to lowercase
    sentence = sentence.lower()
    # # Convert to list from string
    sentence = sentence.split()
    # Lemmatisation
    lem = WordNetLemmatizer()
    sentence = [lem.lemmatize(word) for word in sentence if not word in stop_words]
    sentence = " ".join(sentence)

    return sentence
