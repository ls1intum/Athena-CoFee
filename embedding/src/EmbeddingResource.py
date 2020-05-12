import json
from datetime import datetime
from logging import getLogger
from typing import List
from falcon import Request, Response, HTTP_200
from numpy import ndarray
from .elmo import ELMo
from .entities import Sentence, TextBlock, ElmoVector, Embedding
from .errors import emptyBody, requireTwoBlocks


class EmbeddingResource:
    __elmo: ELMo = None
    __logger = getLogger(__name__)

    def __default(self, o) -> int:
        if isinstance(o, Embedding): return o.__dict__
        if isinstance(o, ndarray): return o.tolist()
        raise TypeError

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Start processing Embedding Request:")
        if req.content_length == 0:
            self.__logger.error("{} ({})".format(emptyBody.title, emptyBody.description))
            raise emptyBody

        doc = json.load(req.stream)
        if "blocks" not in doc:
            self.__logger.error("{} ({})".format(requireTwoBlocks.title, requireTwoBlocks.description))
            raise requireTwoBlocks

        if "courseId" not in doc:
            self.__logger.info("No courseId provided in the request")
            self.__elmo = ELMo()
        else:
            self.__elmo = ELMo(doc["courseId"])

        blocks: List[TextBlock] = list(map(lambda dict: TextBlock.from_dict(dict), doc['blocks']))
        sentences: List[Sentence] = list(map(lambda b: b.text, blocks))

        if len(blocks) < 2:
            self.__logger.error("{} ({})".format(requireTwoBlocks.title, requireTwoBlocks.description))
            raise requireTwoBlocks

        self.__logger.info("Computing embeddings of {} blocks.".format(len(blocks)))
        vectors: List[ElmoVector] = self.__elmo.embed_sentences(sentences)

        embeddings: List[Embedding] = [Embedding(block.id, vectors[i]) for i, block in enumerate(blocks)]

        doc = {
            'embeddings': embeddings
        }

        with open("logs/embedding-{}.json".format(datetime.now()), 'w') as outfile:
            json.dump(doc, outfile, ensure_ascii=False, default=self.__default)

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False, default=self.__default)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = HTTP_200
        self.__logger.info("Completed Embedding Request.")
        self.__logger.debug("-" * 80)
