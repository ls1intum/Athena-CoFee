from typing import List, Tuple
from allennlp.commands.elmo import ElmoEmbedder
from numpy import ndarray
from pathlib import Path
from scipy.spatial import distance
from .entities import ElmoVector, Sentence, Word

TwoSentences = Tuple[Sentence, Sentence]

class ELMo:
    __RESOURCE_PATH = (Path.cwd() / "src/resources/").resolve()
    __OPTIONS_PATH = (__RESOURCE_PATH / "elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json").resolve()

    __DEFAULT_WEIGHT_FILE = "elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5"
    __INCREMENTALLY_TRAINED_WEIGHTS_FILE = "weights_book.hdf5"

    def __init__(self, course_id = None):
        if course_id is None:
            self.weights_path = (self.__RESOURCE_PATH / self.__DEFAULT_WEIGHT_FILE).resolve()
        else:
            self.weights_path = (self.__RESOURCE_PATH / self.__INCREMENTALLY_TRAINED_WEIGHTS_FILE).resolve()

        self.elmo = ElmoEmbedder(self.__OPTIONS_PATH, self.weights_path)

    def __split_sentence(self, sentence: Sentence) -> List[Word]:
        sentence = sentence.lower().replace('\n', ' ').replace('\t', ' ').replace('\xa0',' ')
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
