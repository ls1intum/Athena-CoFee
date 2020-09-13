from datetime import datetime
from logging import getLogger
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
            indices = [i for i, x in enumerate(labels) if x == clusterLabel]
            clusterEmbeddings = [embeddings[i].vector for i in indices]
            clusters[clusterLabel] = {
                'blocks': [TextBlock(embeddings[i].id) for i in indices],
                'probabilities': [probabilities[i] for i in indices],
                'distanceMatrix': self.__clustering.distances_within_cluster(clusterEmbeddings)
            }

        output = {'clusters': clusters}

        try:
            with open("logs/clustering-{}.json".format(datetime.now()), 'w') as outfile:
                json.dump(output, outfile, ensure_ascii=False, default=self.__default)
        except Exception as e:
            self.__logger.error("Error while writing logfile: {}".format(str(e)))

        self.__logger.info("Completed Clustering Request.")
        self.__logger.debug("-" * 80)

        output["jobId"] = data["jobId"]
        output["resultType"] = "clustering"
        self.__logger.error("Send back clustering-results")
        # Get container variable for load balancer url
        send_result_url = str(os.environ['BALANCER_SENDRESULT_URL']) if "BALANCER_SENDRESULT_URL" in os.environ else "http://localhost:8000/sendTaskResult"
        response = requests.post(send_result_url, data=json.dumps(output, default=self.__default), timeout=5)
        if response.status_code != 200:
            self.__logger.error("Sending back failed: {}".format(response.text))

    # Queries the taskQueue and returns the task data (json)
    def getNewTask(self):
        try:
            # Get container variable for load balancer url
            get_task_url = str(os.environ['BALANCER_GETTASK_URL']) if "BALANCER_GETTASK_URL" in os.environ else "http://localhost:8000/getTask"
            task = requests.get(get_task_url, json={"taskType": "clustering"}, timeout=5)
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
