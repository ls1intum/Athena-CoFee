import numpy as np
from logging import getLogger
from pathlib import Path
from typing import List, Tuple
from scipy.spatial import distance
from .entities import Sentence
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
TwoSentences = Tuple[Sentence, Sentence]


class WMT:

    __logger = getLogger(__name__)
    __RESOURCE_PATH = (Path.cwd() / "src/resources/models").resolve()

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(WMT.__RESOURCE_PATH)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(WMT.__RESOURCE_PATH)


    def embed_sentences(self, sentences: List[Sentence])  -> List[List[int]]:
        tokenized_sentences: List[List[str]] = list(map(lambda sentence: self.tokenizer(sentence, return_tensors="pt"), sentences))
        generated_tokens: List[List[int]]= list(map(lambda tokenized_sentence: self.model.generate(**tokenized_sentence), tokenized_sentences))
        encoded_tokens: List[List[int]]= list(map(lambda token: self.encode_tensor_as_vector(token), generated_tokens))
        return encoded_tokens

    def encode_two_sentences(self, sentences: TwoSentences):
        return self.embed_sentences(list(sentences))


    def distance(self, sentences: TwoSentences) -> float:
        token_vector_1, token_vector_2 = self.encode_two_sentences(sentences)
        return distance.cosine(token_vector_1, token_vector_2)

    def encode_tensor_as_vector(self, tokens_to_encode):
        tokens_to_encode = self.cut_special_tokens(tokens_to_encode)
        len_tokens = len(tokens_to_encode)
        self.__logger.info(len_tokens)
        vector = np.zeros(len_tokens)
        for i in range(len_tokens):
            vector[i] = tokens_to_encode[i].item()
        return vector


    def cut_special_tokens(self, tokens_to_encode):
            return tokens_to_encode[0][1:-1]


