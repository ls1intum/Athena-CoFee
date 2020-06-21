from logging import getLogger

from benchmark.src.networking.api_requests import post
from benchmark.src.entities.feedback_with_text_block import FeedbackWithTextBlock
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


def __check_feedback_consistency(text_blocks, feedback):
    # request with {"text_blocks":[{'id':,'submission_id':,'cluster_id':,'text':,'reference':}]}
    # {"feedback":[{'id':,'text':,'score':,'reference'}]} response with true and false at the moment
    request = {"text_blocks": text_blocks, "feedback": feedback}
    return post(FEEDBACK_CONSISTENCY_URL, request)


def check_feedback_consistency(feedback_with_text_blocks: [FeedbackWithTextBlock]):
    step_size = 5
    responses = []
    for i in range(0, len(feedback_with_text_blocks), step_size):
        blocks = feedback_with_text_blocks[i:i + step_size]
        text_blocks = [block.json_rep_text_block() for block in blocks]
        feedback = [block.json_rep_feedback() for block in blocks]
        responses.append(__check_feedback_consistency(text_blocks, feedback))
    return responses


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


t = [
    {'id': 7, 'submission_id': 3, 'cluster_id': 3, 'text': "First Answer", 'position_in_cluster': 0,
     'added_distance': 0,
     'reference': "ref"},
    {'id': 8, 'submission_id': 3, 'cluster_id': 4, 'text': "Second answer", 'position_in_cluster': 0,
     'added_distance': 0,
     'reference': "ref2"}]
f = [{'id': 8,
      'text': "Well done! Great answer.",
      'score': 1, 'reference': "ref"},
     {'id': 9, 'text': "Aggregation example is not detailed enough. Your composition example is incorrect, that's an aggregation.", 'score': 1, 'reference': "ref2"}]
x = __check_feedback_consistency(text_blocks=t, feedback=f)
print(x)
# "Well done! Correct explanation, but it's not entirely clear." 'silhouette': 0.23047011119693042
# "Well done! Correct explanation, but it's not entirely clear. this is an example for inheritance." 'silhouette': 0.16875091164932954
# "Good example, well done! Correct explanation, but it's not entirely clear what you mean by. this is an example for inheritance."
# [[0.42518826151003386, 0.5443454057650379, 0.5818820121801975], [0.6612295672577371, 0.593989990570547, 0.6768367871277435], [0.4096789407036616, 0.38561426973970303, 0.2813647948879576]]
# [[0.4204443091615502, 0.5426907687878102, 0.5779279218374214], [0.6588718630986558, 0.5926580588976887, 0.6740467468747203], [0.4099106413129088, 0.39017932192938576, 0.2875782998545642
