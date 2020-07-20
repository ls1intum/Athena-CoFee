import json
from datetime import datetime
from logging import getLogger
import math
import os.path
from typing import List
from falcon import Request, Response, HTTP_200, HTTP_500
from numpy import ndarray
import requests
from threading import Thread
import yaml
from .entities import Embedding, ComputeNode
from .errors import emptyBody, requireTwoBlocks

class BalanceEmbedding:
    __logger = getLogger(__name__)

    def __default(self, o) -> int:
        if isinstance(o, Embedding): return o.__dict__
        if isinstance(o, ndarray): return o.tolist()
        raise TypeError

    def parseConfig(self):
        # Read config.yml file
        try:
            filepath = str(os.environ['CONFIG_FILE_PATH']) if "CONFIG_FILE_PATH" in os.environ else "src/config.yml"
            with open(filepath, 'r') as stream:
                config = yaml.safe_load(stream)
        except Exception as e:
            self.__logger.error("Error reading config: " + str(e))
            return

        # Parse config
        compute_nodes = list()
        for node in config['compute_nodes']:
            if 'name' not in node or 'url' not in node or 'chunk_size' not in node or 'compute_power' not in node or 'communication_cost' not in node:
                self.__logger.warning("Skipping Compute Node definition. Not all required variables set: " + str(node))
                continue
            try:
                new_node = ComputeNode(name=str(node['name']), url=str(node['url']), chunk_size=int(node['chunk_size']),
                                       compute_power=int(node['compute_power']),
                                       communication_cost=int(node['communication_cost']))
                compute_nodes.append(new_node)
                self.__logger.info("Parsed Compute Node definition - " + str(new_node))
            except Exception as e:
                self.__logger.error("Error during config parsing: " + str(e))

        return compute_nodes

    # Returns reduced doc and part of doc with length <size>
    def splitBlocks(self, doc, size):
        blockchunk = doc['blocks'][0:min(len(doc['blocks']), size)]
        rest = doc['blocks'][min(len(doc['blocks']), size):]
        # Pass through courseId if provided
        if "courseId" not in doc:
            request_chunk = {
                "blocks": blockchunk
            }
            rest = {
                "blocks": rest
            }
        else:
            request_chunk = {
                "courseId": doc["courseId"],
                "blocks": blockchunk
            }
            rest = {
                "courseId": doc["courseId"],
                "blocks": rest
            }
        return request_chunk, rest

    # Creates chunks of blocks
    def createChunks(self, doc, compute_nodes):
        total_compute_power = 0
        for node in compute_nodes:
            total_compute_power += node.compute_power

        rest = doc
        for node in compute_nodes:
            node.chunk_quantity = math.ceil(len(doc['blocks']) / total_compute_power * node.compute_power)
            # Minimum of 2 blocks is required to compute embeddings - prevent this case
            if len(rest['blocks']) == (node.chunk_quantity + 1):
                node.blocks, rest = self.splitBlocks(rest, node.chunk_quantity + 1)
            else:
                node.blocks, rest = self.splitBlocks(rest, node.chunk_quantity)

            self.__logger.info("Node {} will process {} blocks".format(node.name, len(node.blocks['blocks'])))
        # TODO: Balancing logic (communication cost)

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

        if "courseId" not in doc:
            self.__logger.info("No courseId provided in the request")

        # Computing preparation
        output = {"embeddings": []}                 # Declare output variable
        starttime = datetime.now()                  # Start timer
        computing_result = {}                       # Declare array for individual results
        thread_list = list()                        # Declare list for started threads

        # Parse available compute nodes using config file
        compute_nodes = self.parseConfig()
        if not compute_nodes:
            resp.status = HTTP_500
            resp.body = "Error parsing compute node config"
            return

        #request_chunks = self.createChunks(doc, compute_nodes)  # Split request into chunks
        self.createChunks(doc, compute_nodes)  # Split request into chunks

        # Function to process request chunk
        def threaded_request(thread_id, thread_name, url, request, timeout):
            self.__logger.info("Thread {} ({}) started processing ...".format(thread_id, thread_name))
            # TODO: Chunk according to compute node's chunkSize
            computing_result[thread_id] = requests.post(url, data=json.dumps(request), timeout=timeout)
            self.__logger.info("Thread {} ({}) finished processing.".format(thread_id, thread_name))

        # Process chunks concurrently
        self.__logger.info("Start load balanced computation ...")
        for i, node in enumerate(compute_nodes):
            # TODO: Distinguish between REST-call to processing-node or file-creation for GPU-node
            # TODO: Variable Timeout and error handling for timeout
            timeout = 60
            if len(node.blocks['blocks']) != 0:
                t = Thread(target=threaded_request, args=(i, node.name, node.url, node.blocks, timeout))
                t.start()
                thread_list.append(t)

        # Merge all computed embeddings together
        for i, thread in enumerate(thread_list):
            thread.join()
            if 'embeddings' in computing_result[i].json():
                output['embeddings'].extend(computing_result[i].json()['embeddings'])
            else:
                # TODO: Resend blocks to another compute node if processing failed
                self.__logger.error("Error while merging computed embeddings of thread {}: ".format(i))

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
