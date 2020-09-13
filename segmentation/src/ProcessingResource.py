from logging import getLogger
from src.json_processor.serializer import load_result_to_json
from src.text_processor.data_cleaner import clean_data
from src.json_processor.deserialzer import load_submissions_from_json, load_keywords_from_json
from src.text_processor.keyword_extractor import get_top_n_words
from src.segmentor.segmentor import segment_data
from src.errors import tooFewSubmissions, noSubmissions
import json
import os
import requests


class ProcessingResource:
    __logger = getLogger(__name__)

    # Starts processing of a queried task
    def processTask(self, data):
        if "submissions" not in data:
            raise noSubmissions
        else:
            if "keywords" not in data:
                submissions = load_submissions_from_json(data)
                if len(submissions) < 10:
                    raise tooFewSubmissions
                corpus = clean_data(submissions)
                keywords = get_top_n_words(corpus, 10)
                segmentation_result = segment_data(submissions, keywords)
                output = load_result_to_json(keywords, segmentation_result)
            else:
                keywords = load_keywords_from_json(data)
                submissions = load_submissions_from_json(data)
                segmentation_result = segment_data(submissions, keywords)
                output = load_result_to_json(keywords, segmentation_result)
        output["jobId"] = data["jobId"]
        output["resultType"] = "segmentation"
        self.__logger.error("Send back segmentation-results")
        # Get container variable for load balancer url
        send_result_url = str(os.environ['BALANCER_SENDRESULT_URL']) if "BALANCER_SENDRESULT_URL" in os.environ else "http://localhost:8000/sendTaskResult"
        response = requests.post(send_result_url, data=json.dumps(output), timeout=5)
        if response.status_code != 200:
            self.__logger.error("Sending back failed: {}".format(response.text))

    # Queries the taskQueue and returns the task data (json)
    def getNewTask(self):
        try:
            # Get container variable for load balancer url
            get_task_url = str(os.environ['BALANCER_GETTASK_URL']) if "BALANCER_GETTASK_URL" in os.environ else "http://localhost:8000/getTask"
            task = requests.get(get_task_url, json={"taskType": "segmentation"}, timeout=5)
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
