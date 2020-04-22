import nltk
import string
import re

from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from num2words import num2words
from nltk.corpus import wordnet as wn
from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
from nltk.corpus import wordnet as wn

stemmer = nltk.stem.porter.PorterStemmer()
lemmatizer = WordNetLemmatizer()
tokenizer = RegexpTokenizer(r'\w+')


def remove_stopwords(text):
    """
    Remove stopwords from an input data based on nltk.punkt library
    Input: text{String}:for which all stop words should be removed
    Output: Sentence without stopwords (String)
    """
    stop_words = set(stopwords.words('english'))
    new_stop_words = set(['e.g', 'i.e', 'etc.'])
    stop_words = stop_words.union(new_stop_words)
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    return filtered_sentence


def preprocess_sentence(sentence):
    """
    Preprocess a single sentence by utilizing lemmatization, stemming, replacing of digits with strings and tokenizing
    :param sentence: Sentence which is to be preprocessed
    Output: Preprocessed sentence (String)
    """
    sentence = remove_stopwords(sentence)
    sentence = tokenizer.tokenize(' '.join(sentence))
    sentence = ' '.join(sentence)
    result = []
    for w in sentence.split():
        if w.isdigit():
            w = num2words(w)
        if w == 'a':
            w = 'one'
        w = stemmer.stem(w)
        result.append(w)
    sentence = ' '.join(result)
    return sentence


def lemmatize_sentence(sentence):
    """
    Lemmatizes a sentence
    :param sentence: sentence which should be lemmatized
    :return List: list which contanins the result 
    """
    result = []
    for w in sentence.split():
        w = lemmatizer.lemmatize(w)
        if w.isdigit():
            w = num2words(w)
        if w == 'a':
            w = 'one'
        w = stemmer.stem(w)
        result.append(w)
    result = tokenizer.tokenize(' '.join(result))
    return ''.join(result)


def preprocess_sentences(sentences):
    """
    Preprocess a List of sentences based on the preprocess_sentence function
    :param sentences: List of sentences (Strings)
    :return list:  of Words where every sentence is preprocessed
    """
    result = []
    for sentence in sentences:
        result.append(preprocess_sentence(sentence).split())
    return result


def generate_ngram(sentence, n):
    """
    Generates an ngram with the length of n for a given sentence
    :param sentence: String for which the n gram should be generated
    :param n: number which indicates the length of the n gram
    :return list: ngram as a List of Strings with the length n
    """
    tokens = [token for token in sentence.split(" ") if token != ""]
    return list(ngrams(tokens, n))


def generate_bag_of_ngram(sentences, n):
    """
    Generates a bag of ngram from 1..n based on the generate_ngram function
    :param sentences: list of strings for which the n grams should be generated
    :param n: number which indicates the length of the n grams
    :return: ngrams as a List of Strings with the length n
    """
    result = []
    for i in range(1, n):
        for sentence in sentences:
            result.append(generate_ngram(' '.join(sentence), i + 1))
    return result


def ngram_overlap(n_gram1, n_gram2):
    """
    Calculates the word for word overlap between two n-grams
    :param n_gram1: List of Strings which contain all tokens 
    :param n_gram2: List of Strings which contain all tokens 
    :return float: as percental match between n_gram1 and n_gram2
    """
    intersection = len(list(set(n_gram1).intersection(n_gram2)))
    union = (len(n_gram1) + len(n_gram2)) - intersection
    return float(intersection) / union


def lengthen_abbreviation(word):
    """
    :param word: word which should be transformed to longer form
    :return String: longer form of abbreviation
    """
    if word == "e.g":
        return "example"
    elif word == "i.e":
        return "other words"
    else:
        return word


def filter_keywords(n_gram, keywords):
    """
    :param n_gram: N_gram for which the keywords should be filtered
    :param keywords: keywords of the references
    :return: True if n_gram contains a keyword, false if not 
    """
    for word in n_gram.split(" "):
        if word in keywords:
            return True
    return False


def calculate_confidence(candidate, references):
    """
    Calculates the confidence of a candidate to its references
    :param candidate: Text block which should be tested for similarity to the references
    :param references: List of sentences(String) which the candidate is compared against
    :return: value between 0 and 100
    """
    # Determine percental weight of each measurement

    # Keyword weight
    q = float((len(references) - 1) / (float(len(references))))
    # Bigram weight
    s = 1.0 - q

    # Preprocess the candidate
    candidate = preprocess_sentence(candidate)

    # Preprocess the references
    references = preprocess_sentences(references)

    # Create a set of keywords which appear in every sentence of the references
    keywords = []
    for reference in references:
        keywords.append(set(reference))
    keywords = list(set(keywords[0].intersection(*keywords[1:])))

    # Get the number of key words which appear in the candidate
    keyword_match = len(
        list(set(candidate.split()).intersection(set(keywords))))

    # Generate bag of n grams from all references
    # Flat out list of lists
    bag_of_ngram = [
        ngram for ngram_list in generate_bag_of_ngram(references, 2) for ngram in ngram_list]

    # Create a dictionary which contains the number of n-gram overlap
    n_gram_dictionary = {}
    for n_gram in bag_of_ngram:
        similiar_ngram_count = len(list(filter(
            (lambda x: ngram_overlap(x, n_gram) == float(1)), bag_of_ngram)))
        n_gram_dictionary[' '.join(n_gram)] = similiar_ngram_count

    # Generate list of n grams from keywords for candidate and flat it out
    candidate_ngrams = [
        ngram for ngram_list in generate_bag_of_ngram([list(candidate.split())], 2) for ngram in ngram_list]

    # Convert ngrams of candidate into proper formatting for set intersection
    tmp = []
    for ngram in candidate_ngrams:
        tmp.append(' '.join(ngram))

    # Determine bigram overlap
    ngram_similarity = float(len(
        list(set(candidate_ngrams).intersection(set(bag_of_ngram)))) / len(list(set(candidate_ngrams))))

    # Avoid division by 0 exception
    if (len(keywords) == 0):
        keyword_similarity = float(0)
    else:
        keyword_similarity = float(keyword_match / len(keywords))

    # Return weighted confidence as percentage
    return ((q * keyword_similarity) + (s * ngram_similarity)) * 100
