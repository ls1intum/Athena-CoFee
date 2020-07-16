import json
from datetime import datetime
from logging import getLogger
import os.path
from typing import List
from falcon import Request, Response, HTTP_200
from numpy import ndarray
import requests
from threading import Thread
from .entities import Sentence, TextBlock, ElmoVector, Embedding
from .errors import emptyBody, requireTwoBlocks

class BalanceEmbedding:
    __logger = getLogger(__name__)

    def __default(self, o) -> int:
        if isinstance(o, Embedding): return o.__dict__
        if isinstance(o, ndarray): return o.tolist()
        raise TypeError

    # Creates chunks of blocks
    def createChunks(self, doc):
        # TODO: Dynamic chunking dependent on target node settings
        # TODO: Calculate chunkSize for processing nodes
        # TODO: Balancing logic (communication cost)
        # TODO: Handle single block in last chunk (minimum of 2 required) -> Include in previous chunk
        blockchunks = []
        chunkSize = 50
        blockcount = len(doc['blocks'])
        self.__logger.info("Chunk request of {} total blocks in chunks of size {} ...".format(blockcount, chunkSize))
        # Create equally sized chunks
        for i in range(0, len(doc['blocks']), chunkSize):
            self.__logger.info("Adding chunk for blocks {}-{}".format(i+1, min(i + chunkSize, blockcount)))
            blockchunk = doc['blocks'][i:min(i + chunkSize, blockcount)]
            # Pass through courseId if provided
            if "courseId" not in doc:
                self.__logger.info("No courseId provided in the request")
                request_chunk = {
                    "blocks": blockchunk
                }
            else:
                request_chunk = {
                    "courseId": doc["courseId"],
                    "blocks": blockchunk
                }
            blockchunks.append(request_chunk)
        return blockchunks

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Incoming Embedding Request")

        # Error handling for faulty requests
        if req.content_length == 0:
            self.__logger.error("{} ({})".format(emptyBody.title, emptyBody.description))
            raise emptyBody

        doc = json.load(req.stream)
        if "blocks" not in doc:
            self.__logger.error("{} ({})".format(requireTwoBlocks.title, requireTwoBlocks.description))
            raise requireTwoBlocks

        # Computing preparation
        output = {"embeddings": []}                 # Declare output variable
        starttime = datetime.now()                  # Start timer
        computing_result = {}                       # Declare array for individual results
        thread_list = list()                        # Declare list for started threads
        request_chunks = self.createChunks(doc)     # Split request into chunks

        # Function to process request chunk
        def threaded_request(thread_id, url, request, timeout):
            self.__logger.info("Thread {} started processing ...".format(thread_id))
            computing_result[thread_id] = requests.post(url, data=json.dumps(request), timeout=timeout)
            self.__logger.info("Thread {} finished processing.".format(thread_id))

        # Process chunks concurrently
        self.__logger.info("Start load balanced computation ...")
        for i, request in enumerate(request_chunks):
            # TODO: Distinguish between REST-call to processing-node or file-creation for GPU-node
            # TODO: Variable url
            request_url = 'https://athene01.ase.in.tum.de/embed'
            # TODO: Variable Timeout and error handling for timeout
            timeout = 60
            t = Thread(target=threaded_request, args=(i, request_url, request, timeout))
            t.start()
            thread_list.append(t)

        # Merge all computed embeddings together
        for i, thread in enumerate(thread_list):
            thread.join()
            output['embeddings'].extend(computing_result[i].json()['embeddings'])

        endtime = datetime.now()                    # Stop timer
        processingtime = endtime - starttime        # Calculate processing time
        self.__logger.info("Processing took {} (h:mm:ss.ms)".format(processingtime))

        # Write result to outfile for debugging
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
