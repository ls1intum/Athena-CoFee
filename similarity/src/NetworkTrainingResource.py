import json
import os.path
from datetime import datetime
from logging import getLogger
from typing import List

from falcon import Request, Response, HTTP_200
from keras.callbacks import History
from numpy import ndarray

from .entities import EmbeddingsPair
from .errors import emptyBody, requireEmbeddingPairs
from .siamese_network import SiameseNetwork


class NetworkTrainingResource:
    __logger = getLogger(__name__)
    __siameseNetwork: SiameseNetwork = SiameseNetwork()
    __dimension = str(os.environ['INPUT_DIMENSION']) if "INPUT_DIMENSION" in os.environ else "(1024, 1)"

    def __default(self, o) -> int:
        if isinstance(o, EmbeddingsPair): return o.__dict__
        if isinstance(o, ndarray): return o.tolist()
        if isinstance(o, History): return o.history
        if isinstance(o, dict): return o.__dict__
        self.__logger.info("Type Error. Type {} not JSON serializable.".format(type(o)))
        raise TypeError

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Start Network Training Request:")
        if req.content_length == 0:
            self.__logger.error("{} ({})".format(emptyBody.title, emptyBody.description))
            raise emptyBody

        doc = json.load(req.stream)
        if "embeddingPairs" not in doc:
            self.__logger.error("{} ({})".format(requireEmbeddingPairs.title, requireEmbeddingPairs.description))
            raise requireEmbeddingPairs

        embeddingPairs: List[EmbeddingsPair] = list(map(lambda dict: EmbeddingsPair.from_dict(dict), doc['embeddingPairs']))

        #input dimension can be adapted here
        self.__logger.info("Building model.")
        self.__siameseNetwork.build_siamese_model(self.__dimension)

        #train siamese network
        self.__logger.info("Start training on {} pairs.".format(len(embeddingPairs)))
        training_history = self.__siameseNetwork.train_siamese_network(embeddingPairs, "src/resources/siamese-model")

        doc = {
            'training_history': str(training_history.history)
        }

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
