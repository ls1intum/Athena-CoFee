from typing import List, Tuple
import json
import falcon
from .elmo import ELMo, Sentence, TwoSentences
from .clustering import Clustering
from pandas import DataFrame
from numpy import int64, ndarray

class SentenceClusteringResource:

    __clustering: Clustering = Clustering()
    __elmo: ELMo = ELMo()

    def __default(self, o) -> int :
        if isinstance(o, int64): return int(o)
        if isinstance(o, ndarray): return o.tolist()
        print(o)
        raise TypeError

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        badRequest = falcon.HTTPBadRequest("Need many sentences", "Must provide at least two sentences")
        if req.content_length == 0:
            raise badRequest
        
        doc = json.load(req.stream)
        sentences: List[Sentence] = doc['sentences']

        if len(sentences) < 2:
            raise badRequest

        embeddings = self.__elmo.embed_sentences(sentences)
        print("embeddings", DataFrame(embeddings).head())
        labels, probabilities = self.__clustering.cluster(embeddings)
        print("labels", DataFrame(labels).head())
        print("probabilities", DataFrame(probabilities).head())

        clusterLabels = list(map(lambda i: int(i), set(labels)))
        clusters = {}
        for clusterLabel in clusterLabels:
            indices = [ i for i, x in enumerate(labels) if x == clusterLabel ]
            cluster = {}
            cluster['sentences'] = [ sentences[i] for i in indices ]
            cluster['probabilities'] = [ probabilities[i] for i in indices ]
            clusterEmbeddings = [ embeddings[i] for i in indices ]
            cluster['distanceMatrix'] = self.__clustering.distances_within_cluster(clusterEmbeddings)
            clusters[clusterLabel] = cluster


        doc = {
            'sentences': sentences,
            'labels': labels,
            'probabilities': probabilities,
            'clusters': clusters
        }

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False, default=self.__default)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200
