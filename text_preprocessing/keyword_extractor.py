from sklearn.feature_extraction.text import CountVectorizer


# Most frequently occuring words
def get_top_n_words(corpus, n):
    """Function that returns n keywords for a preprocessed corpus

    :param corpus: preprocessed documents: lower-case, lemmatized without punctuation
    :param n: number of keywords to return
    :return: n keywords extracted from the corpus
    """
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in
                  vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1],
                        reverse=True)
    keywords = []
    for key in (i[0] for i in words_freq):
        keywords.append(key)

    return keywords[:n]
