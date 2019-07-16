from typing import List, Tuple, Generator
import json
import falcon
from .elmo import ELMo, Sentence, TwoSentences
from .clustering import Clustering
from pandas import DataFrame
from numpy import int64, array, ndarray

class TextBlock:
    id: str
    text: Sentence

    def __init__(self, id: str, text: Sentence):
        self.id = id
        self.text = text

class SentenceClusteringResource:

    __clustering: Clustering = Clustering()
    __elmo: ELMo = ELMo()

    def __default(self, o) -> int :
        if isinstance(o, int64): return int(o)
        if isinstance(o, ndarray): return o.tolist()
        if isinstance(o, TextBlock): return o.__dict__
        raise TypeError

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        badRequest = falcon.HTTPBadRequest("Need many sentences", "Must provide at least two sentences")
        if req.content_length == 0:
            raise badRequest
        
        doc = json.load(req.stream)
        blocks: List[TextBlock] = list(map(lambda dict: TextBlock(dict['id'], dict['text']), doc['blocks']))
        sentences: List[Sentence] = list(map(lambda b: b.text, blocks))

        if len(sentences) < 2:
            raise badRequest

        embeddings = list(self.__batchEmbedding(sentences, 100))
        print("embeddings", DataFrame(embeddings).head())
        labels, probabilities = self.__clustering.cluster(embeddings)
        print("labels", DataFrame(labels).head())
        print("probabilities", DataFrame(probabilities).head())

        clusterLabels = list(map(lambda i: int(i), set(labels)))
        clusters = {}
        for clusterLabel in clusterLabels:
            indices = [ i for i, x in enumerate(labels) if x == clusterLabel ]
            cluster = {}
            cluster['blocks'] = [ blocks[i] for i in indices ]
            cluster['probabilities'] = [ probabilities[i] for i in indices ]
            clusterEmbeddings = [ embeddings[i] for i in indices ]
            cluster['distanceMatrix'] = self.__clustering.distances_within_cluster(clusterEmbeddings)
            clusters[clusterLabel] = cluster


        doc = { 'clusters': clusters }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False, default=self.__default)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200

    def __batchEmbedding(self, sentences: List[Sentence], n: int) -> Generator[List[array], None, None]:
        for i in range(0, len(sentences), n):
            batch = sentences[i:i + n]
            yield self.__elmo.embed_sentences(sentences)
