from typing import List, Tuple
import json
import falcon
from numpy import ndarray
from .elmo import ELMo
from .entities import Sentence, TextBlock, ElmoVector, Embedding
from .errors import emptyBody, requireTwoBlocks

class EmbeddingResource:

    __elmo: ELMo = ELMo()

    def __default(self, o) -> int :
        if isinstance(o, Embedding): return o.__dict__
        if isinstance(o, ndarray): return o.tolist()
        raise TypeError

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        if req.content_length == 0:
            raise emptyBody
        
        doc = json.load(req.stream)
        if "blocks" not in doc:
            raise requireTwoBlocks

        blocks: List[TextBlock] = list(map(lambda dict: TextBlock.from_dict(dict), doc['blocks']))
        sentences: List[Sentence] = list(map(lambda b: b.text, blocks))

        if len(blocks) < 2:
            raise  requireTwoBlocks

        vectors: List[ElmoVector] = self.__elmo.embed_sentences(sentences)

        embeddings: List[Embedding] = [ Embedding(block.id, vectors[i]) for i, block in enumerate(blocks) ]

        doc = {
            'embeddings': embeddings
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False, default=self.__default)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200