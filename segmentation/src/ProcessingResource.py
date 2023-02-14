from datetime import datetime
from logging import getLogger
from src.json_processor.serializer import load_result_to_json
from src.text_preprocessing.data_cleaner import clean_data
from src.json_processor.deserialzer import load_submissions_from_json, load_keywords_from_json, load_feedback_from_json
from src.text_preprocessing.keyword_extractor import get_top_n_words
from src.segmentor.segmentor import segment_data, segment_feedback_data
from src.errors import tooFewSubmissions, noSubmissions
import json
import os
import requests


class ProcessingResource:
    __logger = getLogger(__name__)

    # Starts processing of a queried task
    def processTask(self, data):
        if "feedback" not in data and "submissions" not in data:
            raise noSubmissions
        elif "feedback" in data:
            feedback = load_feedback_from_json(data)
            segmentation_result = segment_feedback_data(feedback)
            output = load_result_to_json("", segmentation_result)
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
        return output

    def sendBackResults(self, result, job_id):
        result["jobId"] = job_id
        result["resultType"] = "segmentation"

        try:
            self.__logger.info("Writing logfile")
            with open("logs/segmentation-{}.json".format(datetime.now()), 'w') as outfile:
                json.dump(result, outfile, ensure_ascii=False)
        except Exception as e:
            self.__logger.error("Error while writing logfile: {}".format(str(e)))

        self.__logger.info("Send back segmentation-results")
        # Get container variable for load balancer url
        send_result_url = str(os.environ['BALANCER_SENDRESULT_URL']) if "BALANCER_SENDRESULT_URL" in os.environ else "http://localhost:8000/sendTaskResult"
        auth_secret = str(os.environ['AUTHORIZATION_SECRET']) if "AUTHORIZATION_SECRET" in os.environ else ""
        headers = {
            "Authorization": auth_secret
        }
        response = requests.post(send_result_url, data=json.dumps(result), headers=headers, timeout=30)
        if response.status_code != 200:
            self.__logger.error("Sending back failed: {}".format(response.text))

    # Queries the taskQueue and returns the task data (json)
    def getNewTask(self):
        try:
            # Get container variable for load balancer url
            get_task_url = str(os.environ['BALANCER_GETTASK_URL']) if "BALANCER_GETTASK_URL" in os.environ else "http://localhost:8000/getTask"
            auth_secret = str(os.environ['AUTHORIZATION_SECRET']) if "AUTHORIZATION_SECRET" in os.environ else ""
            headers = {
                "Authorization": auth_secret
            }
            task = requests.get(get_task_url, json={"taskType": "segmentation"}, headers=headers, timeout=30)
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
