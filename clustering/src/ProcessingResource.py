from datetime import datetime
from logging import getLogger
from math import isinf
from numpy import int64, ndarray
from src.clustering import Clustering
from src.errors import requireTwoEmbeddings
from src.entities import TextBlock, ElmoVector, Embedding
from typing import List
import json
import os
import requests


class ProcessingResource:
    __logger = getLogger(__name__)
    __clustering: Clustering = Clustering()

    def __default(self, o) -> int :
        if isinstance(o, int64): return int(o)
        if isinstance(o, ndarray): return o.tolist()
        if isinstance(o, TextBlock): return o.__dict__
        raise TypeError

    # Starts processing of a queried task
    def processTask(self, data):
        self.__logger.debug("-" * 80)
        self.__logger.info("Start processing Clustering Request:")

        if "embeddings" not in data:
            self.__logger.error("{} ({})".format(requireTwoEmbeddings.title, requireTwoEmbeddings.description))
            raise requireTwoEmbeddings

        embeddings: List[Embedding] = list(map(lambda dict: Embedding.from_dict(dict), data['embeddings']))
        if len(embeddings) < 2:
            self.__logger.error("{} ({})".format(requireTwoEmbeddings.title, requireTwoEmbeddings.description))
            raise requireTwoEmbeddings

        self.__logger.info("Computing clusters of {} embeddings.".format(len(embeddings)))
        vectors: List[ElmoVector] = list(map(lambda e: e.vector, embeddings))
        labels, probabilities = self.__clustering.cluster(vectors)

        clusterLabels: List[int] = list(map(lambda i: int(i), set(labels)))
        clusters = {}
        for clusterLabel in clusterLabels:
            # Skip cluster of unassgined elements
            if clusterLabel == -1: continue

            indices = [i for i, x in enumerate(labels) if x == clusterLabel]
            clusterEmbeddings = [embeddings[i].vector for i in indices]
            clusters[clusterLabel] = {
                'blocks': [TextBlock(embeddings[i].id) for i in indices],
                'probabilities': [probabilities[i] for i in indices],
                'distanceMatrix': self.__clustering.distances_within_cluster(clusterEmbeddings),
                'treeId': self.__clustering.label_to_tree_id(clusterLabel)
            }

        output = {'clusters': clusters, 'distanceMatrix': [], 'clusterTree': []}

        # For now, do not compute cluster tree.
        # self.__computeClusterTree(vectors, output)

        self.__logger.info("Completed Clustering Request.")
        self.__logger.debug("-" * 80)

        output["jobId"] = data["jobId"]
        output["resultType"] = "clustering"

        try:
            self.__logger.info("Writing logfile")
            with open("logs/clustering-{}.json".format(datetime.now()), 'w') as outfile:
                json.dump(output, outfile, ensure_ascii=False, default=self.__default)
        except Exception as e:
            self.__logger.error("Error while writing logfile: {}".format(str(e)))

        self.__logger.info("Send back clustering-results")
        # Get container variable for load balancer url
        send_result_url = str(os.environ['BALANCER_SENDRESULT_URL']) if "BALANCER_SENDRESULT_URL" in os.environ else "http://localhost:8000/sendTaskResult"
        auth_secret = str(os.environ['AUTHORIZATION_SECRET']) if "AUTHORIZATION_SECRET" in os.environ else ""
        headers = {
            "Authorization": auth_secret
        }
        response = requests.post(send_result_url, data=json.dumps(output, default=self.__default), headers=headers, timeout=240)
        if response.status_code != 200:
            self.__logger.error("Sending back failed: {}".format(response.text))
    
    # Persist Cluster Structure as Cluster Tree and Distance Matrix between all blocks.
    def __computeClusterTree(self, vectors, output):
        matrix = self.__clustering.distances_within_cluster(vectors)
        # Following loop removes duplicates in matrix
        for i in range(len(matrix)):
            for j in range(i):
                matrix[i][j] = 0

        for row in matrix:
            output['distanceMatrix'].append(list([float(row[i]) for i in range(len(row))]))

        tree = self.__clustering.clusterer.condensed_tree_.to_pandas()
        # A row in the tree data frame has the following structure:
        # [ parent, child, lambdaVal, childSize ]
        for row in tree.values.tolist():
            # Store infinite lambda values as -1
            if isinf(float(row[2])):
                row[2] = -1
            output['clusterTree'].append({
                'parent': int(row[0]),
                'child': int(row[1]),
                'lambdaVal': float(row[2]),
                'childSize': int(row[3])
            })
        # Add an artificial root node
        rootId = len(vectors)
        output['clusterTree'].append({
            'parent': int(-1),
            'child': int(rootId),
            'lambdaVal': float(-1),
            'childSize': int(rootId)
        })

    # Queries the taskQueue and returns the task data (json)
    def getNewTask(self):
        try:
            # Get container variable for load balancer url
            get_task_url = str(os.environ['BALANCER_GETTASK_URL']) if "BALANCER_GETTASK_URL" in os.environ else "http://localhost:8000/getTask"
            auth_secret = str(os.environ['AUTHORIZATION_SECRET']) if "AUTHORIZATION_SECRET" in os.environ else ""
            headers = {
                "Authorization": auth_secret
            }
            task = requests.get(get_task_url, json={"taskType": "clustering"}, headers=headers, timeout=30)
        except Exception as e:
            self.__logger.error("getTask-API seems to be down: {}".format(str(e)))
            return None

        if task.status_code != 200:
            return None

        try:
            return task.json()
        except Exception as e:
            self.__logger.error("Exception while parsing json: {}".format(str(e)))
            return None
