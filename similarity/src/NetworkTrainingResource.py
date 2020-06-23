from logging import getLogger
from falcon import Request, Response, HTTP_200
from numpy import ndarray
from .errors import emptyBody, requireTwoEmbeddings, requireTextBlockPairs
import json
from typing import List
from datetime import datetime
from .entities import ElmoVector, Embedding, EmbeddingsPair
from .siamese_network import SiameseNetwork


class NetworkTrainingResource:
    __logger = getLogger(__name__)
    __siameseNetwork: SiameseNetwork = SiameseNetwork()

    def __default(self, o) -> int:
        if isinstance(o, Embedding): return o.__dict__
        if isinstance(o, ndarray): return o.tolist()
        raise TypeError

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Start Network Training Request:")
        if req.content_length == 0:
            self.__logger.error("{} ({})".format(emptyBody.title, emptyBody.description))
            raise emptyBody

        doc = json.load(req.stream)
        if "textBlockPairs" not in doc:
            self.__logger.error("{} ({})".format(requireTextBlockPairs.title, requireTextBlockPairs.description))
            raise requireTextBlockPairs

        embeddingPairs: List[EmbeddingsPair] = list(map(lambda dict: EmbeddingsPair.from_dict(dict), doc['embeddingPairs']))

        self.__logger.info("Train on {} pairs.".format(len(embeddingPairs)))

        #input dimension can be adapted here
        self.__siameseNetwork.build_siamese_model((1024, 1))

        #train siamese network
        training_history = self.__siameseNetwork.train_siamese_network(embeddingPairs, "resources/siamese-model")

        doc = {'training_history': training_history}

        with open("logs/networkTraining-{}.json".format(datetime.now()), 'w') as outfile:
            json.dump(doc, outfile, ensure_ascii=False, default=self.__default)

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False, default=self.__default)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = HTTP_200
        self.__logger.info("Completed Network Training Request.")
        self.__logger.debug("-" * 80)