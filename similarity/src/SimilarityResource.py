import json
from datetime import datetime
from logging import getLogger
from pathlib import Path
from typing import List

from falcon import Request, Response, HTTP_200
from numpy import ndarray

from .entities import ElmoVector, Embedding
from .errors import emptyBody, requireTwoEmbeddings
from .siamese_network import SiameseNetwork


class SimilarityResource:
    __logger = getLogger(__name__)
    __siameseNetwork: SiameseNetwork = SiameseNetwork()

    def __default(self, o) -> int:
        if isinstance(o, Embedding): return o.__dict__
        if isinstance(o, ndarray): return o.tolist()
        raise TypeError

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Start processing Similarity Request:")
        if req.content_length == 0:
            self.__logger.error("{} ({})".format(emptyBody.title, emptyBody.description))
            raise emptyBody

        doc = json.load(req.stream)
        if "embeddings" not in doc:
            self.__logger.error("{} ({})".format(requireTwoEmbeddings.title, requireTwoEmbeddings.description))
            raise requireTwoEmbeddings

        embeddings: List[Embedding] = list(map(lambda dict: Embedding.from_dict(dict), doc['embeddings']))
        if len(embeddings) < 2:
            self.__logger.error("{} ({})".format(requireTwoEmbeddings.title, requireTwoEmbeddings.description))
            raise requireTwoEmbeddings

        self.__logger.info("Found {} embeddings.".format(len(embeddings)))
        vectors: List[ElmoVector] = list(map(lambda e: e.vector, embeddings))

        self.__logger.info("Loading network model.")
        self.__siameseNetwork.load_model("src/resources/siamese-model")

        self.__logger.info("Computing similarities of {} embeddings.".format(len(embeddings)))
        matrix = self.__siameseNetwork.compute_similarity_matrix(vectors)

        doc = {'similarity_matrix': matrix}

        with open("logs/similarity-{}.json".format(datetime.now()), 'w') as outfile:
            json.dump(doc, outfile, ensure_ascii=False, default=self.__default)

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False, default=self.__default)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = HTTP_200
        self.__logger.info("Completed Similarity Request.")
        self.__logger.debug("-" * 80)