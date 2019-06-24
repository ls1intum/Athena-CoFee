from typing import List, Tuple
from allennlp.commands.elmo import ElmoEmbedder
from numpy import array, ndarray
from pathlib import Path
import scipy

Word = str
Sentence = str
TwoSentences = Tuple[Sentence, Sentence]

class ELMo:
    __cwd = Path.cwd()
    __DEFAULT_OPTIONS_FILE = (__cwd / "src/resources/elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json").resolve()
    __DEFAULT_WEIGHT_FILE = (__cwd / "src/resources/elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5").resolve()

    __elmo = ElmoEmbedder(__DEFAULT_OPTIONS_FILE, __DEFAULT_WEIGHT_FILE)

    def __split_sentence(self, sentence: Sentence) -> List[Word]:
        sentence = sentence.lower().replace('\n', ' ').replace('\t', ' ').replace('\xa0',' ')
        words = sentence.split()
        words = map(lambda word: word.strip(), words)
        return list(words)

    def embed_sentences(self, sentences: List[Sentence]) -> List[array]:
        word_list_iterator = map(self.__split_sentence, sentences)
        word_lists: List[List[str]] = list(word_list_iterator)
        vectors: List[ndarray] = self.__elmo.embed_batch(word_lists)
        return list(map(lambda vector: vector[2].sum(axis=0), vectors))

    def __embed_two_sentences(self, sentences: TwoSentences) -> Tuple[array, array]:
        vectors = embed_sentences(list(sentences))
        return (vectors[0], vectors[1])
        

    def distance(self, sentences: TwoSentences) -> float:
        sentence_vector_1, sentence_vector_2 = self.__embed_two_sentences(sentences)
        return scipy.spatial.distance.cosine(sentence_vector_1, sentence_vector_2)
