import pickle
import requests
from logging import getLogger
from typing import List
from src.elmo import ELMo
from src.database.Connection import Connection
from src.entities import FeedbackWithTextBlock, Feedback, Sentence, ElmoVector

SEGMENTATION_URL = "http://segmentation:8000/segment"


class FeedbackCommentResource:
    __conn: Connection = None
    __elmo: ELMo = None
    __logger = getLogger(__name__)
    __collection = 'feedback_test'

    def __init__(self):
        self.__elmo = ELMo()
        self.__conn = Connection()

    def __segment_feedback_comments(self, feedback_with_tb: list):
        self.__logger.info("Segment Feedback Comments.")
        feedback = []
        for f in feedback_with_tb:
            feedback.append({"id": f.feedback.id, "text": f.feedback.text})

        self.__logger.info(feedback)
        request = {"feedback": feedback}
        return self.post(SEGMENTATION_URL, request)

    def __embed_feedback_comments(self, sentence: List[Sentence]):
        return self.__elmo.embed_sentences(sentence)

    def __create_feedback_document(self, feedback_with_tb: FeedbackWithTextBlock):
        embeddings = []
        for embedding in feedback_with_tb.feedback.feedbackEmbeddings:
            embeddings.append({'embedding': pickle.dumps(embedding)})

        doc = {'_id': feedback_with_tb.id, 'submission_id': feedback_with_tb.submission_id,
               'cluster_id': feedback_with_tb.cluster_id,
               'position_in_cluster': feedback_with_tb.position_in_cluster,
               'added_distance': feedback_with_tb.added_distance,
               'text': feedback_with_tb.text, 'feedback': {'feedback_id': feedback_with_tb.feedback.id,
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
                return False
            else:
                self.__logger.info(
                    "Modified Count: {} Upserted id {}".format(result.modified_count, result.upserted_id))
        return True

    def store_feedback(self, feedback_with_tb: list):
        self.__logger.info("Store Feedback.")
        segmented_feedback_comments = self.__segment_feedback_comments(feedback_with_tb)

        docs = []
        for fwt in feedback_with_tb:
            blocks = (blocks for blocks in segmented_feedback_comments['textBlocks'] if fwt.feedback.id == blocks['id'])
            sentences: List[Sentence] = list(map(lambda b: fwt.feedback.text[b['startIndex']:b['endIndex']], blocks))
            vectors: List[ElmoVector] = self.__embed_feedback_comments(sentences)
            for v in vectors:
                fwt.add_feedback_embedding(v)
            docs.append(self.__create_feedback_document(feedback_with_tb=fwt))

        return self.__replace_insert_documents(documents=docs)

    def post(self, api_endpoint, data):
        response = requests.post(url=api_endpoint, json=data)

        if not response:
            self.__logger.error("POST failed on {}: Status Code: {} Response: {}".format(api_endpoint,
                                                                                         response.status_code,
                                                                                         response.content))
            return None

        return response.json()
