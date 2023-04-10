import numpy as np
# needed for compatibility with nltk, which assumes an old numpy version
np.int = int
np.bool = bool
np.float = float

from logging import getLogger
from typing import List, Tuple
from numpy import ndarray
from scipy.spatial import distance
from .elmo_factory import ELMoFactory
from .entities import ElmoVector, Sentence, Word

TwoSentences = Tuple[Sentence, Sentence]


class ELMo:
    __logger = getLogger(__name__)
    elmo_factory = ELMoFactory()

    def __init__(self, course_id=None):
        self.elmo = self.elmo_factory.get_model_for_course(course_id)

    def __split_sentence(self, sentence: Sentence) -> List[Word]:
        sentence = sentence.lower().replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ')
        words = sentence.split()
        words = map(lambda word: word.strip(), words)
        return list(words)

    def embed_sentences(self, sentences: List[Sentence]) -> List[ElmoVector]:
        word_list_iterator = map(self.__split_sentence, sentences)
        word_lists: List[List[str]] = list(word_list_iterator)
        vectors: List[ndarray] = self.elmo.embed_batch(word_lists)
        return list(map(lambda vector: vector[2].sum(axis=0), vectors))

    def __embed_two_sentences(self, sentences: TwoSentences) -> Tuple[ElmoVector, ElmoVector]:
        vectors = self.embed_sentences(list(sentences))
        return (vectors[0], vectors[1])

    def distance(self, sentences: TwoSentences) -> float:
        sentence_vector_1, sentence_vector_2 = self.__embed_two_sentences(sentences)
        return distance.cosine(sentence_vector_1, sentence_vector_2)
