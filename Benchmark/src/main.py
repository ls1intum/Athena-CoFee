import logging
import sys

from Benchmark.src.networking.api_requests import post

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

data = {
    "courseId": 25,
    "blocks": [
        {
            "id": 1,
            "text": "hi there kljfhf"
        },
        {
            "id": 2,
            "text": "sdfsdfg dh dh hfg hf ff"
        }
    ]
}

print(post("http://localhost:8001/embed", data))
