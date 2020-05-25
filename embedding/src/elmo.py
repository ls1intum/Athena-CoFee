from logging import getLogger
from typing import List, Tuple
from allennlp.commands.elmo import ElmoEmbedder
from numpy import ndarray
from pathlib import Path
from scipy.spatial import distance
from .entities import ElmoVector, Sentence, Word

TwoSentences = Tuple[Sentence, Sentence]


class ELMo:
    ELMo_models_cache = {}

    __RESOURCE_PATH = (Path.cwd() / "src/resources/models").resolve()
    __OPTIONS_PATH = (__RESOURCE_PATH / "elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json").resolve()
    __DEFAULT_WEIGHT_FILE = "elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5"

    # courseId_to_model = {
    #     1601: "weights_book_bs16.hdf5",
    #     1602: "weights_bs16_epochs2.hdf5",
    #     6401: "weights_book_bs64.hdf5",
    #     640101: "weights_book_bs64_fullclean.hdf5"
    # }

    __logger = getLogger(__name__)

    @staticmethod
    def __courseId_to_model(course_id, default_model):
        epochs = course_id % 10
        bs = course_id // 100
        return "weights_bs{}_epochs{}.hdf5".format(bs, epochs)

    def __init__(self, course_id=None):
        if course_id is None:
            self.weights_path = (self.__RESOURCE_PATH / self.__DEFAULT_WEIGHT_FILE).resolve()
        else:
            model_name = self.__DEFAULT_WEIGHT_FILE #self.__courseId_to_model(course_id, self.__DEFAULT_WEIGHT_FILE)
            self.weights_path = (self.__RESOURCE_PATH / model_name).resolve()

        self.__logger.info("Using the ELMo Model {}".format(self.weights_path))

        if self.weights_path not in ELMo.ELMo_models_cache:
            ELMo.ELMo_models_cache[self.weights_path] = ElmoEmbedder(self.__OPTIONS_PATH, self.weights_path)

        self.elmo = ELMo.ELMo_models_cache[self.weights_path]

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
