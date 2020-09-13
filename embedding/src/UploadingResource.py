import base64
import json
from datetime import datetime
from logging import getLogger
from src.cloud.cloud_connection import CloudConnection
from src.errors import invalidJson, requireCourseId, requireFileName, requireFileData
from fastapi import APIRouter, Request

logger = getLogger(name="UploadingResource")
router = APIRouter()

@router.post("/upload")
async def upload(request: Request):
    logger.debug("-" * 80)
    logger.info("Start processing Uploading Request:")

    # Parse json
    try:
        doc = await request.json()
    except Exception as e:
        logger.error("Exception while parsing json: {}".format(str(e)))
        raise invalidJson

    if "courseId" not in doc:
        logger.error("{} ({})".format(requireCourseId.title, requireCourseId.description))
        raise requireCourseId

    if "fileName" not in doc:
        logger.error("{} ({})".format(requireFileName.title, requireFileName.description))
        raise requireFileName

    if "fileData" not in doc:
        logger.error("{} ({})".format(requireFileData.title, requireFileData.description))
        raise requireFileData

    decoded_file_data = base64.b64decode(doc["fileData"])

    remote_path = CloudConnection.upload_file(doc["fileName"], decoded_file_data, str(doc["courseId"]))

    doc = {
        'remotePath': remote_path
    }

    with open("logs/uploading-{}.json".format(datetime.now()), 'w') as outfile:
        json.dump(doc, outfile, ensure_ascii=False)

    logger.info("Completed Uploading Request.")
    logger.debug("-" * 80)
    return doc
