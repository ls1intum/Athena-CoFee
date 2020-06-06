import base64
import json
from datetime import datetime
from logging import getLogger
from typing import List

from falcon import Request, Response, HTTP_200

from src.cloud.cloud_connection import CloudConnection
from src.errors import emptyBody, requireCourseId, requireFileName, requireFileData


class UploadingResource:
    __logger = getLogger(__name__)

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Start processing Uploading Request:")

        if req.content_length == 0:
            self.__logger.error("{} ({})".format(emptyBody.title, emptyBody.description))
            raise emptyBody

        doc = json.load(req.stream)

        if "courseId" not in doc:
            self.__logger.error("{} ({})".format(requireCourseId.title, requireCourseId.description))
            raise requireCourseId

        if "fileName" not in doc:
            self.__logger.error("{} ({})".format(requireFileName.title, requireFileName.description))
            raise requireFileName

        if "fileData" not in doc:
            self.__logger.error("{} ({})".format(requireFileData.title, requireFileData.description))
            raise requireFileData

        decoded_file_data = base64.b64decode(doc["fileData"])

        remote_path = CloudConnection.upload_file(doc["fileName"], decoded_file_data,  str(doc["courseId"]))

        doc = {
            'remotePath': remote_path
        }

        with open("logs/uploading-{}.json".format(datetime.now()), 'w') as outfile:
            json.dump(doc, outfile, ensure_ascii=False)

        # Create a JSON representation of the resource
        resp.body = json.dumps(doc, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = HTTP_200
        self.__logger.info("Completed Uploading Request.")
        self.__logger.debug("-" * 80)
