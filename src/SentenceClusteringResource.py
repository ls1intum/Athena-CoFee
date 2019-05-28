from typing import List, Tuple
import json
import falcon
from .elmo import embed_sentences, Sentence, TwoSentences
from .clustering import cluster
import pandas as pd
from numpy import int64

class SentenceClusteringResource(object):

        
    def default(self, o):
        if isinstance(o, int64): return int(o)  
        raise TypeError

    def on_post(self, req, resp):
        badRequest = falcon.HTTPBadRequest("Need many sentences", "Must provide at least two sentences")
        if req.content_length == 0:
            raise badRequest
        
        doc = json.load(req.stream)
        sentences: List[Sentence] = doc['sentences']

        if len(sentences) < 2:
            raise badRequest

        embeddings = embed_sentences(sentences)
        print("embeddings", pd.DataFrame(embeddings).head())
        labels, probabilities = cluster(embeddings)
        print("labels", pd.DataFrame(labels).head())
        print("probabilities", pd.DataFrame(probabilities).head())
        
        doc = {
            'sentences': sentences,
            'labels': list(labels),
            'probabilities': list(probabilities),
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False, default=self.default)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200
