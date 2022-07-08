import hashlib
import logging
import sys
from abc import abstractmethod
from .errors import missingTextBlocks, noUpdateNeeded, invalidResults, missingEmbeddings, missingTaskId, \
    missingClusters, missingDistanceMatrix, missingClusterTree
from .ConfigParser import ConfigParser
import requests
from requests.auth import HTTPBasicAuth
from .entities import Policy, NodeType, JobStatus
from .JSONHandler import JSONHandler, logger


class ResultJob:

    @staticmethod
    @abstractmethod
    def perform_result(self, job):
        pass


def sendBackResults(job):
    pass


def sizeof(obj):
    size = sys.getsizeof(obj)
    if isinstance(obj, dict): return size + sum(map(sizeof, obj.keys())) + sum(map(sizeof, obj.values()))
    if isinstance(obj, (list, tuple, set, frozenset)): return size + sum(map(sizeof, obj))
    return size


def triggerNodes(node_type: str):
        # hier muss noch ein node type rein
        node_types = (
            NodeType.segmentation, NodeType.embedding, NodeType.clustering, NodeType.embedding_wmt, NodeType.gpu)
        if node_type not in node_types:
            logger.error('Invalid node_type: \'{}\''.format(node_type))

        # Parse compute nodes
        config_parser = ConfigParser()
        logger.info("Parsing {} nodes".format(node_type))
        nodes = config_parser.parseConfig(node_type)

        # Trigger all parsed nodes
        logger.info("Triggering {} nodes".format(node_type))
        for node in nodes:
            if node_type == NodeType.gpu:
                requests.post(node.url, auth=HTTPBasicAuth(node.username, node.password))
            else:
                requests.post(node.url, timeout=5)


class SegmentationResult(ResultJob):

    def __init__(self):
        pass

    @staticmethod
    def send_result(job, result):
        logging.info("Segmentation Result")
        if "textBlocks" not in result:
            raise missingTextBlocks
        JSONHandler.writeJsonToFile(job.id, "segmentation_result", result)
        # Transform segmentation result to blocks (embedding input)
        for block in result["textBlocks"]:
            submission_id = int(block["id"])
            start_index = int(block["startIndex"])
            end_index = int(block["endIndex"])
            # Search for the corresponding submission and create block out of segmentation result information
            for submission in job.submissions:
                if submission["id"] == submission_id:
                    block_text = submission["text"][start_index:end_index]
                    id_string = str(submission_id) + ";" \
                                + str(start_index) + "-" \
                                + str(end_index) + ";" \
                                + block_text
                    block_id = hashlib.sha1(id_string.encode()).hexdigest()
                    new_block = {"id": block_id,
                                 "submissionId": submission_id,
                                 "text": block_text,
                                 "startIndex": start_index,
                                 "endIndex": end_index,
                                 "type": "AUTOMATIC"}
                    job.blocks.append(new_block)  # Will persist in job
                    job.blocks_to_embed.append(new_block)  # Will get removed with embedding queries
                    break
        job.status = JobStatus.embedding_queued
        logger.info("JobId {} transitioned to status {}".format(job.id, job.status))
        # Trigger embedding nodes
        # hier muss die Fallunterscheidung her!
        node_Type = Policy.define_embedding_type(job.multilingual)
        logging.info(node_Type)
        logger.info("Das ist der Node Type: " + node_Type)
        triggerNodes(node_type=node_Type)
        return {"detail": "Updated job: processed segmentation results"}


class EmbeddingResult:

    def __init__(self):
        pass

    @staticmethod
    def send_result(job, result):

        logging.info("Embedding Result")

        if "embeddings" not in result:
            raise missingEmbeddings
        if "taskId" not in result:
            raise missingTaskId

        JSONHandler.writeJsonToFile(job.id, "embedding_result_" + str(result["taskId"]), result)

        # Add results to job and remove corresponding embedding-task out of queue
        valid_results = False
        for task in job.embedding_tasks:
            if str(task.id) == str(result["taskId"]):
                # Check if number of embeddings is correct
                if not len(task.blocks) == len(result["embeddings"]):
                    raise invalidResults
                for embedding in result["embeddings"]:
                    job.embeddings.append(embedding)
                valid_results = True
                logger.info("embedding-task {} of JobId {} finished".format(task.id, job.id))
                job.embedding_tasks.remove(task)
                break

        if not valid_results:
            raise noUpdateNeeded

        # Check if all embeddings of job finished
        if len(job.blocks_to_embed) == 0 and len(job.embedding_tasks) == 0:
            job.status = JobStatus.clustering_queued
            logger.info("JobId {} transitioned to status {}".format(job.id, job.status))
            # Trigger clustering nodes
            triggerNodes(node_type=NodeType.clustering)

        return {"detail": "Updated job: processed embedding results"}


class ClusteringResult:

    def __init__(self):
        pass

    @staticmethod
    def send_result(job, result):
        logging.info("Clustering Job")
        if "clusters" not in result:
            raise missingClusters
        if "distanceMatrix" not in result:
            raise missingDistanceMatrix
        if "clusterTree" not in result:
            raise missingClusterTree

        JSONHandler.writeJsonToFile(job.id, "clustering_result", result)

        job.clusters = result["clusters"]
        job.distanceMatrix = result["distanceMatrix"]
        job.clusterTree = result["clusterTree"]

        # Send back results to Artemis via callback URL in the background
        job.status = JobStatus.sending_back
        return {"detail": "Updated job: processed clustering results"}