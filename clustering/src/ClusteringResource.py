from typing import List
import json
from falcon import Request, Response, HTTP_200
from logging import getLogger
from .clustering import Clustering
from numpy import int64, ndarray
from .entities import TextBlock, ElmoVector, Embedding
from .errors import emptyBody, requireTwoEmbeddings
from datetime import datetime

class ClusteringResource:

    __clustering: Clustering = Clustering()
    __logger = getLogger(__name__)

    def __default(self, o) -> int :
        if isinstance(o, int64): return int(o)
        if isinstance(o, ndarray): return o.tolist()
        if isinstance(o, TextBlock): return o.__dict__
        raise TypeError

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Start processing Clustering Request:")
        if req.content_length == 0:
            self.__logger.error("{} ({})".format(emptyBody.title, emptyBody.description))
            raise emptyBody
        
        doc = json.load(req.stream)
        if "embeddings" not in  doc:
            self.__logger.error("{} ({})".format(requireTwoEmbeddings.title, requireTwoEmbeddings.description))
            raise  requireTwoEmbeddings

        embeddings: List[Embedding] = list(map(lambda dict: Embedding.from_dict(dict), doc['embeddings']))
        if len(embeddings) < 2:
            self.__logger.error("{} ({})".format(requireTwoEmbeddings.title, requireTwoEmbeddings.description))
            raise requireTwoEmbeddings

        self.__logger.info("Computing clusters of {} embeddings.".format(len(embeddings)))
        vectors: List[ElmoVector] = list(map(lambda e: e.vector,  embeddings))
        labels, probabilities = self.__clustering.cluster(vectors)

        clusterLabels: List[int] = list(map(lambda i: int(i), set(labels)))
        clusters = {}
        for clusterLabel in clusterLabels:
            indices = [ i for i, x in enumerate(labels) if x == clusterLabel ]
            clusterEmbeddings = [ embeddings[i].vector for i in indices ]
            clusters[clusterLabel] = {
                'blocks': [ TextBlock(embeddings[i].id) for i in indices ],
                'probabilities': [ probabilities[i] for i in indices ],
                'distanceMatrix': self.__clustering.distances_within_cluster(clusterEmbeddings)
            }

        doc = { 'clusters': clusters }

        with open("logs/clustering-{}.json".format(datetime.now()), 'w') as outfile:
            json.dump(doc, outfile, ensure_ascii=False, default=self.__default)

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False, default=self.__default)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = HTTP_200
        self.__logger.info("Completed Clustering Request.")
        self.__logger.debug("-" * 80)
