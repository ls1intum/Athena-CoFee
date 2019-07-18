import falcon
from .EmbeddingResource import EmbeddingResource
from .ClusteringResource import ClusteringResource

api = application = falcon.API()

api.add_route('/embed', EmbeddingResource())
api.add_route('/cluster', ClusteringResource())
