from logging import getLogger

from benchmark.src.networking.api_requests import post
import numpy as np

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


def __embed(text_blocks, courseId=None):
    # embedding function without splitting of the sentences into smaller chunks
    # request with {'courseId': 25, 'blocks': [{'id': 1, 'text': 'this is the first block'}, {'id': 2, 'text': 'this is the second block'}]}
    # response with { 'embeddings': [{'id': , 'vector':[]}] }
    request = {"blocks": [text_block.json_rep() for text_block in text_blocks]}
    if courseId is not None:
        request["courseId"] = courseId
    return post(EMBEDDING_URL, request)['embeddings']

def embed(text_blocks, courseId=None):
    # splits the text_blocks into chunks of 50 blocks and embeds them
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


