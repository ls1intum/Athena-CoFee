from logging import getLogger

from Benchmark.src.networking.api_requests import post

__logger = getLogger(__name__)

SEGMENTATION_URL = "http://localhost:8000/segment"
EMBEDDING_URL = "http://localhost:8001/embed"
CLUSTERING_URL = "http://localhost:8002/cluster"


def segment(submissions, keywords=None):
    # request with {"submissions":[{id:,text:}],"keywords":[]}
    # response with {"keywords":[],"textBlocks":[{id:,startIndex:,endIndex}]}
    request = {"submissions": submissions}
    if keywords is not None:
        request["keywords"] = keywords
    return post(SEGMENTATION_URL, request)


def embed(text_blocks, courseId=None):
    # request with {'courseId': 25, 'blocks': [{'id': 1, 'text': 'this is the first block'}, {'id': 2, 'text': 'this is the second block'}]}
    # response with { 'embeddings': [{'id': , 'vector':[]}] }
    request = {"blocks": text_blocks}
    if courseId is not None:
        request["courseId"] = courseId
    return post(EMBEDDING_URL, request)


def cluster(embeddings):
    # request with { "embeddings": [{"id": ,"vector":[]}] }
    # response with {"clusters": {"-1": {"blocks": [{"id": 1}, {"id": 2}], "probabilities": [0.0, 0.0], "distanceMatrix": [[0.0, 0.22923004776660816], [0.22923004776660816, 0.0]]}}}
    request = {"embeddings": embeddings}
    return post(CLUSTERING_URL, request)
