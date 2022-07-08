import json
import os
import requests
from typing import List
from logging import getLogger
from datetime import datetime
from numpy import ndarray

from .entities import Sentence, TextBlock, Embedding
from .errors import requireTwoBlocks
from .wmt import WMT


class ProcessingResource:
    __logger = getLogger(__name__)


    def __default(self, o) -> int:
        if isinstance(o, Embedding): return o.__dict__
        if isinstance(o, ndarray): return o.tolist()
        raise TypeError

    # Starts processing of a queried task
    def processTask(self, data):
        self.__logger.debug("-" * 80)
        self.__logger.info("Start processing Embedding Request:")

        if "blocks" not in data:
            self.__logger.error("{} ({})".format(requireTwoBlocks.title, requireTwoBlocks.description))
            raise requireTwoBlocks

        self.__wmt = WMT()

        blocks: List[TextBlock] = list(map(lambda dict: TextBlock.from_dict(dict), data['blocks']))

        #sentences[i] = text des i'ten Text Block
        sentences: List[Sentence] = list(map(lambda b: b.text, blocks))

        #Was wird hier genau gemacht? --> clean_Text wird erstmal nicht gebraucht
        #sentences = [clean_text(sentence, lemmatization=False) for sentence in sentences]

        if len(blocks) < 2:
            self.__logger.error("{} ({})".format(requireTwoBlocks.title, requireTwoBlocks.description))
            raise requireTwoBlocks

        self.__logger.info("Computing embeddings of {} blocks.".format(len(blocks)))

        #Hier werden die einzelnen Sätze embeded
        vectors: List[List[int]] = self.__wmt.embed_sentences(sentences)

        self.__logger.info("Hier sind die Vektoren")
        self.__logger.info(vectors)



        #Hier werden die embeddeden Sätze in Embeddingsblöcke geschrieben
        embeddings: List[Embedding] = [Embedding(block.id, vectors[i]) for i, block in enumerate(blocks)]

        output = {
            'embeddings': embeddings
        }

        self.__logger.info("Hier sind die Embeddings")
        self.__logger.info(embeddings)

        #Embedding ist fertig, es wird zurück an x geschickt
        self.__logger.info("Completed Embedding Request.")
        self.__logger.debug("-" * 80)

        output["jobId"] = data["jobId"]
        output["taskId"] = data["taskId"]
        #type anpassen
        output["resultType"] = "embedding_wmt"

        try:
            self.__logger.info("Writing logfile")
            with open("logs/embedding-{}.json".format(datetime.now()), 'w') as outfile:
                json.dump(output, outfile, ensure_ascii=False, default=self.__default)
        except Exception as e:
            self.__logger.error("Error while writing logfile: {}".format(str(e)))

        self.__logger.info("Send back embedding-results")
        # Get container variable for load balancer url
        send_result_url = str(os.environ['BALANCER_SENDRESULT_URL']) if "BALANCER_SENDRESULT_URL" in os.environ else "http://localhost:8000/sendTaskResult"
        auth_secret = str(os.environ['BALANCER_AUTHORIZATION_SECRET']) if "BALANCER_AUTHORIZATION_SECRET" in os.environ else ""
        headers = {
            "Authorization": auth_secret
        }
        response = requests.post(send_result_url, data=json.dumps(output, default=self.__default), headers=headers, timeout=30)
        if response.status_code != 200:
            self.__logger.error("Sending back failed: {}".format(response.text))

    # Queries the taskQueue and returns the task data (json)
    def getNewTask(self):
        try:
            # Get container variable for load balancer url
            get_task_url = str(os.environ['BALANCER_GETTASK_URL']) if "BALANCER_GETTASK_URL" in os.environ else "http://localhost:8000/getTask"
            chunk_size = int(os.environ['CHUNK_SIZE']) if "CHUNK_SIZE" in os.environ else 50
            auth_secret = str(os.environ['BALANCER_AUTHORIZATION_SECRET']) if "BALANCER_AUTHORIZATION_SECRET" in os.environ else ""
            headers = {
                "Authorization": auth_secret
            }
            #hier embedding_wmt rein
            task = requests.get(get_task_url, json={"taskType": "embedding", "chunkSize": chunk_size}, headers=headers, timeout=60)
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
