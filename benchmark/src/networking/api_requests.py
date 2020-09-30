from logging import getLogger

import requests

__logger = getLogger(__name__)


def post(api_endpoint, data):
    response = requests.post(url=api_endpoint, json=data)

    if not response:
        __logger.error("POST failed on {}: Status Code: {}".format(api_endpoint, response.status_code))
        return None

    return response.json() if response.status_code != 204 else None
