from typing import List, Tuple
from allennlp.commands.elmo import ElmoEmbedder
from numpy import array, ndarray
import scipy

Word = str
Sentence = str
TwoSentences = Tuple[Sentence, Sentence]

DEFAULT_OPTIONS_FILE = "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_options.json" # pylint: disable=line-too-long
DEFAULT_WEIGHT_FILE = "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_weights.hdf5" # pylint: disable=line-too-long

elmo = ElmoEmbedder(DEFAULT_OPTIONS_FILE, DEFAULT_WEIGHT_FILE)

def split_sentence(sentence: Sentence) -> List[Word]:
    sentence = sentence.lower().replace('\n', ' ').replace('\t', ' ').replace('\xa0',' ')
    words = sentence.split()
    words = map(lambda word: word.strip(), words)
    return list(words)

def embed_sentences(sentences: TwoSentences) -> Tuple[array, array]:
    word_list_iterator = map(split_sentence, list(sentences))
    word_lists: List[List[str]] = list(word_list_iterator)
    vectors: List[ndarray] = elmo.embed_batch(word_lists)
    return (vectors[0][2], vectors[1][2])
    

def distance(sentences: TwoSentences) -> float:
    embeddings: Tuple[array. array] = embed_sentences(sentences)
    sentence_vector_1: array = embeddings[0].sum(axis=0)
    sentence_vector_2: array = embeddings[1].sum(axis=0)
    return scipy.spatial.distance.cosine(sentence_vector_1, sentence_vector_2)
