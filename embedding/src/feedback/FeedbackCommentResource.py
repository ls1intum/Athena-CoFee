import numpy as np
import os
import json
import pickle
import requests
from logging import getLogger
from typing import List
from src.elmo import ELMo
from src.database.Connection import Connection
from src.entities import FeedbackWithTextBlock, Feedback, Sentence, ElmoVector

# Get container variable for segmentation url
SEGMENTATION_URL = str(os.environ['SEGMENTATION_URL']) if "SEGMENTATION_URL" in os.environ else "http://segmentation:8000/segment"


class FeedbackCommentResource:
    __logger = getLogger(__name__)
    __collection = 'feedback_consistency'

    def __init__(self, exercise_id):
        self.__elmo = ELMo()
        self.__conn = Connection()
        self.__collection = 'feedback_consistency_' + (str(exercise_id) if exercise_id != -1 else 'test')

    def __segment_feedback_comments(self, feedback_with_tb: list):
        self.__logger.info("Segment Feedback Comments.")
        feedback = []
        for f in feedback_with_tb:
            feedback.append({"id": f.feedback.id, "text": f.feedback.text})

        request = {"feedback": feedback}
        return self.post(SEGMENTATION_URL, request)

    def __embed_sentences(self, sentence: List[Sentence]):
        return self.__elmo.embed_sentences(sentence)

    def __create_feedback_document(self, feedback_with_tb: FeedbackWithTextBlock):
        embeddings = []
        for embedding in feedback_with_tb.feedback.feedbackEmbeddings:
            embeddings.append({'embedding': pickle.dumps(np.array(embedding).flatten().tolist())})

        doc = {'_id': feedback_with_tb.id,
               'cluster_id': feedback_with_tb.cluster_id,
               'text': feedback_with_tb.text,
               'text_embedding': pickle.dumps(np.array(feedback_with_tb.text_embedding).flatten().tolist()),
               'feedback': {'feedback_id': feedback_with_tb.feedback.id,
                            'feedback_text': feedback_with_tb.feedback.text,
                            'feedback_score': feedback_with_tb.feedback.score,
                            'feedback_text_blocks': embeddings}}

        return doc

    def __replace_insert_documents(self, documents: []):
        self.__logger.info("Replace-Insert Feedback.")
        for doc in documents:
            __filter = {'_id': doc['_id']}
            try:
                result = self.__conn.replace_document(collection=self.__collection, filter_dict=__filter,
                                                      replacement_dict=doc, upsert=True)
            except Exception as e:
                self.__logger.error(e)
            else:
                self.__logger.info(
                    "Modified Count: {} Upserted id {}".format(result.modified_count, result.upserted_id))

    def embed_feedback(self, feedback_with_tb: list):
        self.__logger.info("Embed Feedback.")
        segmented_feedback_comments = self.__segment_feedback_comments(feedback_with_tb)

        for fwt in feedback_with_tb:
            blocks = (blocks for blocks in segmented_feedback_comments['textBlocks'] if fwt.feedback.id == blocks['id'])
            sentences: List[Sentence] = list(map(lambda b: fwt.feedback.text[b['startIndex']:b['endIndex']], blocks))
            vectors: List[ElmoVector] = self.__embed_sentences(sentences)
            for v in vectors:
                fwt.add_feedback_embedding(v)

        return feedback_with_tb

    def embed_feedback_text_blocks(self, feedback_with_tb: list):
        sentences: List[Sentence] = list(map(lambda b: b.text, feedback_with_tb))
        vectors: List[ElmoVector] = self.__embed_sentences(sentences)
        for fwt, vector in zip(feedback_with_tb, vectors):
            fwt.text_embedding = vector
        return feedback_with_tb

    def store_feedback(self, feedback_with_tb: list):
        self.__logger.info("Store Feedback.")

        docs = []
        for fwt in feedback_with_tb:
            docs.append(self.__create_feedback_document(feedback_with_tb=fwt))

        self.__replace_insert_documents(documents=docs)

    def get_feedback_in_same_cluster(self, cluster_id: str, feedback_id: str):
        self.__logger.info("Get feedback with same cluster id.")
        _filter = {'$and': [{'cluster_id': cluster_id}, {'feedback.feedback_id': {'$ne': feedback_id}}]}
        try:
            result = self.__conn.find_documents(collection=self.__collection, filter_dict=_filter)
        except Exception as e:
            self.__logger.error(e)
            return None
        else:
            return result

    def set_feedback_consistency_results(self, collection, doc):
        try:
            result = self.__conn.insert_document(collection=collection, document=doc)
        except Exception as e:
            self.__logger.error(e)
            return None
        else:
            return result

    def post(self, api_endpoint, data):
        response = requests.post(url=api_endpoint, json=data)

        if not response:
            self.__logger.error("POST failed on {}: Status Code: {} Response: {}".format(api_endpoint,
                                                                                         response.status_code,
                                                                                         response.content))
            return None

        return json.loads(response.json())
