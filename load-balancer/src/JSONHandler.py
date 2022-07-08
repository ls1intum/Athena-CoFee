from .errors import invalidJson
from fastapi import Request

import logging
import os
import sys

logger = logging.getLogger()


class JSONHandler:

    @staticmethod
    async def parseJson(request: Request):
        try:
            return await request.json()
        except Exception as e:
            logger.error("Exception while parsing json: {}".format(str(e)))
            raise invalidJson

    @staticmethod
    def writeJsonToFile(job_id: int, filename: str, data):
        # Only write file if log-level is DEBUG
        if logger.level == logging.DEBUG:
            try:
                directory = "logs/job_" + str(job_id)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                logger.debug("Writing data to logfile: {}".format(filename))
                with open(directory + "/" + filename + ".json", 'w') as outfile:
                    outfile.write(data)
            except Exception as e:
                logger.error("Error while writing logfile: {}".format(str(e)))
