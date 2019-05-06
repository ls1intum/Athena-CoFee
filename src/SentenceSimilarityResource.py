from typing import List, Tuple
import json
import falcon
from .elmo import distance, Sentence, TwoSentences

class SentenceSimilarityResource(object):

    def on_post(self, req, resp):
        badRequest = falcon.HTTPBadRequest("Need two sentences", "Must provide exactly two sentences")
        if req.content_length == 0:
            raise badRequest
        
        doc = json.load(req.stream)
        sentences: List[Sentence] = doc['sentences']

        if len(sentences) != 2:
            raise badRequest

        sentences_to_compare: TwoSentences = tuple(sentences)
        dist: float = distance(sentences_to_compare)
        doc = {
            'sentences': sentences_to_compare,
            'distance': dist
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200