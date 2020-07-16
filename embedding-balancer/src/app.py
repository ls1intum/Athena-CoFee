import sys
import falcon
import logging
from .BalanceEmbedding import BalanceEmbedding

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

api = application = falcon.API()

api.add_route('/embed', BalanceEmbedding())
