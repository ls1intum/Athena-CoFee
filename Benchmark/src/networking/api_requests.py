from logging import getLogger

import requests

__logger = getLogger(__name__)


def post(api_endpoint, data):
    response = requests.post(url=api_endpoint, json=data)

    if response:
        __logger.info("POST successful on {}: {}".format(api_endpoint, data))
    else:
        __logger.error("POST failed on {}: Status Code: {}".format(api_endpoint, response.status_code))

    return response.json()
