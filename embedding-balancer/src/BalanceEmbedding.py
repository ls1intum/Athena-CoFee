import json
from datetime import datetime
from logging import getLogger
import os.path
from typing import List
from falcon import Request, Response, HTTP_200
from numpy import ndarray
import requests
from .entities import Sentence, TextBlock, ElmoVector, Embedding
from .errors import emptyBody, requireTwoBlocks


class BalanceEmbedding:
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

        # Declare output variable
        output = {"embeddings": []}

        # Split into chunks and start processing
        chunkSize = 50
        starttime = datetime.now()
        blockcount = len(doc['blocks'])
        self.__logger.info("Computing embeddings of {} blocks with a chunk size of {}".format(blockcount, chunkSize))
        # TODO: Dynamic chunking dependent on target node settings
        # TODO: Read chunkSize out of config
        # TODO: Balancing logic
        for i in range(0, len(doc['blocks']), chunkSize):
            # TODO: Threaded approach to process blockchunks in parallel
            self.__logger.info("Processing blocks {} to {}".format(i, min(i + chunkSize, blockcount)))
            blockchunk = doc['blocks'][i:min(i + chunkSize, blockcount)]

            # Pass through courseId if provided
            if "courseId" not in doc:
                self.__logger.info("No courseId provided in the request")
                request = {
                    "blocks": blockchunk
                }
            else:
                request = {
                    "courseId": doc["courseId"],
                    "blocks": blockchunk
                }

            # TODO: Distinguish between REST-call to processing-node or file-creation for GPU-node
            # TODO: Timeout
            response = requests.post('http://localhost:8001/embed', data=json.dumps(request), timeout=60)

            # Append processed embeddings to output variable
            output['embeddings'].extend(response.json()['embeddings'])

        endtime = datetime.now()
        processingtime = endtime - starttime
        self.__logger.info("Processing took {} (h:mm:ss.ms)".format(processingtime))

        with open("logs/embedding-{}.json".format(datetime.now()), 'w') as outfile:
            json.dump(output, outfile, ensure_ascii=False, default=self.__default)

        # Create a JSON representation of the resource
        resp.body = json.dumps(output, ensure_ascii=False, default=self.__default)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = HTTP_200
        self.__logger.info("Completed Embedding Request.")
        self.__logger.debug("-" * 80)
