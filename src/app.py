import falcon
from .SentenceSimilarityResource import SentenceSimilarityResource

api = application = falcon.API()

sentenceSimilarity = SentenceSimilarityResource()
api.add_route('/sentences', sentenceSimilarity)