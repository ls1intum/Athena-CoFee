from typing import List, Tuple
import json
import falcon
from .elmo import ELMo, Sentence, TwoSentences

class SentenceSimilarityResource:

    __elmo: ELMo = ELMo()

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        badRequest = falcon.HTTPBadRequest("Need two sentences", "Must provide exactly two sentences")
        if req.content_length == 0:
            raise badRequest
        
        doc = json.load(req.stream)
        sentences: List[Sentence] = doc['sentences']

        if len(sentences) != 2:
            raise badRequest

        sentences_to_compare: TwoSentences = tuple(sentences)
        dist: float = self.__elmo.distance(sentences_to_compare)
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