import json
from datetime import datetime
from logging import getLogger
import math
from falcon import Request, Response, HTTP_200, HTTP_500
from numpy import ndarray
import requests
from threading import Thread
from .entities import Embedding, ComputeNode
from .errors import emptyBody, requireTwoBlocks
from .ConfigParser import ConfigParser

class BalanceEmbedding:
    __logger = getLogger(__name__)

    def __default(self, o) -> int:
        if isinstance(o, Embedding): return o.__dict__
        if isinstance(o, ndarray): return o.tolist()
        raise TypeError

    # Returns and part of doc with length <size> and the rest of doc
    def splitBlocks(self, doc, size):
        # Minimum of 2 blocks is required to compute embeddings - prevent 1 single remaining block
        if len(doc['blocks']) == (size + 1):
            size += 1

        blockchunk = doc['blocks'][0:min(len(doc['blocks']), size)]
        rest = doc['blocks'][min(len(doc['blocks']), size):]
        # Pass through courseId if provided
        if "courseId" not in doc:
            blockchunk = {
                "blocks": blockchunk
            }
            rest = {
                "blocks": rest
            }
        else:
            blockchunk = {
                "courseId": doc["courseId"],
                "blocks": blockchunk
            }
            rest = {
                "courseId": doc["courseId"],
                "blocks": rest
            }
        return blockchunk, rest

    # Creates chunks of blocks
    def createChunks(self, doc, compute_nodes):
        # Evaluate total compute power of all parsed nodes
        total_compute_power = 0
        for node in compute_nodes:
            total_compute_power += node.compute_power

        # Process whole doc and split according to compute power of nodes
        for node in compute_nodes:
            # TODO: Balancing logic (communication cost)
            node.chunk_quantity = math.ceil(len(doc['blocks']) / total_compute_power * node.compute_power)
            node.blocks, doc = self.splitBlocks(doc, node.chunk_quantity)
            self.__logger.info("Node {} will process {} blocks".format(node.name, len(node.blocks['blocks'])))

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Incoming Embedding Request")

        # Error handling for faulty requests
        if req.content_length == 0:
            self.__logger.error("{} ({})".format(emptyBody.title, emptyBody.description))
            raise emptyBody

        doc = json.load(req.stream)
        if "blocks" not in doc or len(doc['blocks']) < 2:
            self.__logger.error("{} ({})".format(requireTwoBlocks.title, requireTwoBlocks.description))
            raise requireTwoBlocks

        if "courseId" not in doc:
            self.__logger.info("No courseId provided in the request")

        # Computing preparation
        output = {"embeddings": []}                 # Declare output variable
        starttime = datetime.now()                  # Start timer
        computing_result = {}                       # Declare array for thread results
        thread_list = list()                        # Declare list for started threads

        # Parse available compute nodes using config file
        compute_nodes = ConfigParser().parseConfig()
        if not compute_nodes:
            # Override response status code
            resp.status = HTTP_500
            resp.body = "Error parsing compute node config or no available nodes"
            self.__logger.error("No compute nodes. Abort Processing.")
            self.__logger.debug("-" * 80)
            return

        # Split request into chunks and assign to nodes
        self.createChunks(doc, compute_nodes)

        # Function to process request chunk of a node
        def threaded_request(thread_id: int, node: ComputeNode):
            self.__logger.info("Thread {} ({}) started processing ...".format(thread_id, node.name))
            rest = node.blocks
            thread_result = {"embeddings": []}
            # Process all blocks assigned to compute node
            while len(rest['blocks']) != 0:
                # Split request according to supported chunkSize of compute node
                request_chunk, rest = self.splitBlocks(rest, node.chunk_size)
                try:
                    # 20 seconds static for ELMo initialization and model download (if required)
                    timeout = 20 + (len(request_chunk['blocks']) / node.compute_power)
                    response = requests.post(node.url, data=json.dumps(request_chunk), timeout=timeout)
                    thread_result['embeddings'].extend(response.json()['embeddings'])
                except Exception as e:
                    self.__logger.error("Thread {} had an error during processing: {}".format(thread_id, str(e)))
                    return
            # Write merged results into global result array
            computing_result[thread_id] = thread_result
            self.__logger.info("Thread {} ({}) finished processing.".format(thread_id, node.name))

        # Process chunks concurrently (one thread for each compute node)
        self.__logger.info("Start load balanced computation ...")
        for i, node in enumerate(compute_nodes):
            # TODO: Distinguish between REST-call to processing-node or file-creation for GPU-node
            if len(node.blocks['blocks']) != 0:
                t = Thread(target=threaded_request, args=(i, node))
                t.start()
                thread_list.append(t)

        # Merge all computed embeddings together
        for i, thread in enumerate(thread_list):
            thread.join()
            if i in computing_result and 'embeddings' in computing_result[i]:
                output['embeddings'].extend(computing_result[i]['embeddings'])
            else:
                self.__logger.error("Error while merging computed embeddings of thread {}: ".format(i))

        endtime = datetime.now()                    # Stop timer
        processingtime = endtime - starttime        # Calculate processing time
        self.__logger.info("Processing took {} (h:mm:ss.µs) and includes {} embeddings".format(processingtime,len(output['embeddings'])))

        # Write result to outfile for debugging
        with open("logs/embedding-{}.json".format(datetime.now()), 'w') as outfile:
            json.dump(output, outfile, ensure_ascii=False, default=self.__default)

        # Create a JSON representation of the resource
        resp.body = json.dumps(output, ensure_ascii=False, default=self.__default)

        # Default response status code is 200
        self.__logger.info("Completed Embedding Request.")
        self.__logger.debug("-" * 80)
