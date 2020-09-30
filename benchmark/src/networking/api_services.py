from logging import getLogger
from benchmark.src.networking.api_requests import post
import numpy as np

__logger = getLogger(__name__)

SEGMENTATION_URL = "http://localhost:8000/segment"
EMBEDDING_URL = "http://localhost:8001/embed"
CLUSTERING_URL = "http://localhost:8002/cluster"
FEEDBACK_CONSISTENCY_URL = "http://localhost:8001/feedback_consistency"


def segment(submissions, keywords=None):
    # request with {"submissions":[{id:,text:}],"keywords":[]}
    # response with {"keywords":[],"textBlocks":[{id:,startIndex:,endIndex}]}
    request = {"submissions": submissions}
    if keywords is not None:
        request["keywords"] = keywords
    return post(SEGMENTATION_URL, request)


def __check_feedback_consistency(feedback_with_text_block, exerciseId):
    # request with {"feedbackWithTextBlock":[{'textBlockId':,'clusterId':,'text':,'feedbackId':,'feedbackText':,'credits':}]}
    # {"feedbackInconsistencies":[{'firstFeedbackId':,'secondFeedbackId':,'type':]}
    request = {"feedbackWithTextBlock": feedback_with_text_block, "exerciseId": exerciseId}
    return post(FEEDBACK_CONSISTENCY_URL, request)


def check_feedback_consistency(feedback_with_text_blocks, exercise_id):
    inconsistencies = []
    for fwt in feedback_with_text_blocks:
        feedback_with_text_block = [block.json_rep() for block in fwt]
        response = __check_feedback_consistency(feedback_with_text_block, exercise_id)
        if response['feedbackInconsistencies']:
            inconsistencies.append(response['feedbackInconsistencies'])
    return np.array(inconsistencies).flatten().tolist()


def __embed(text_blocks, courseId=None):
    # request with {'courseId': 25, 'blocks': [{'id': 1, 'text': 'this is the first block'}, {'id': 2, 'text': 'this is the second block'}]}
    # response with { 'embeddings': [{'id': , 'vector':[]}] }
    request = {"blocks": [text_block.json_rep() for text_block in text_blocks]}
    if courseId is not None:
        request["courseId"] = courseId
    return post(EMBEDDING_URL, request)['embeddings']


def embed(text_blocks, courseId=None):
    split_text_blocks = [text_blocks]
    if len(text_blocks) > 50:
        split_text_blocks = np.array_split(np.array(text_blocks), len(text_blocks) / 50)
    embeddings = list(map(lambda blocks: __embed(blocks, courseId), split_text_blocks))
    return [embedding for embedding_list in embeddings for embedding in embedding_list]


def cluster(embeddings):
    # request with { "embeddings": [{"id": ,"vector":[]}] }
    # response with {"clusters": {"-1": {"blocks": [{"id": 1}, {"id": 2}], "probabilities": [0.0, 0.0], "distanceMatrix": [[0.0, 0.22923004776660816], [0.22923004776660816, 0.0]]}}}
    request = {"embeddings": embeddings}
    return post(CLUSTERING_URL, request)['clusters']
