import falcon
from .SentenceSimilarityResource import SentenceSimilarityResource
from .SentenceClusteringResource import SentenceClusteringResource

api = application = falcon.API()

sentenceSimilarity = SentenceSimilarityResource()
sentenceClustering = SentenceClusteringResource()
api.add_route('/sentences', sentenceSimilarity)
api.add_route('/cluster', sentenceClustering)