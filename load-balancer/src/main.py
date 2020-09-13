from .entities import AtheneJob, JobStatus, NodeType, EmbeddingTask
from .errors import *
from fastapi import FastAPI, Request, Response, status
from src.ConfigParser import ConfigParser
import hashlib
import logging
import requests
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()
queue = list()
job_counter = 0


def triggerNodes(node_type: str):
    node_types = (NodeType.segmentation, NodeType.embedding, NodeType.clustering, NodeType.gpu)
    if node_type not in node_types:
        logger.error('Invalid node_type: \'{}\''.format(node_type))

    # Parse compute nodes
    config_parser = ConfigParser()
    logger.info("Parsing {} nodes".format(node_type))
    nodes = config_parser.parseConfig(node_type)

    # Trigger all parsed nodes
    logger.info("Triggering {} nodes".format(node_type))
    for node in nodes:
        requests.post(node.url, timeout=5)

# Endpoint for Artemis to submit a job
# This will create a new job and queue up the first task (segmentation)
@app.post("/submit")
async def submit_job(request: Request, response: Response):
    # TODO: Authentication
    # Parse json
    try:
        job = await request.json()
    except Exception as e:
        logger.error("Exception while parsing json: {}".format(str(e)))
        raise invalidJson

    # Error handling
    if "courseId" in job:
        course_id = job["courseId"]
    else:
        course_id = -1
    if "callbackUrl" in job:
        callback_url = job["callbackUrl"]
    else:
        callback_url = ""
    if "submissions" not in job:
        raise missingSubmissions

    # Queue up new job
    global job_counter
    job_counter += 1
    newJob = AtheneJob(id=job_counter, course_id=course_id, callback_url=callback_url, submissions=job["submissions"])
    queue.append(newJob)
    logger.info("New Athene Job added: " + str(newJob))
    # Trigger segmentation nodes
    triggerNodes(node_type=NodeType.segmentation)
    # Trigger GPU Server
    triggerNodes(node_type=NodeType.gpu)
    return {'Submission successful'}


# Returns a chunk of size <size> of the blocks <blocks> and the rest of the blocks
def createEmbeddingChunk(blocks, size):
    # Minimum of 2 blocks is required to compute embeddings - prevent 1 single remaining block
    if len(blocks) == (size + 1):
        size += 1

    blockchunk = blocks[0:min(len(blocks), size)]
    rest = blocks[min(len(blocks), size):]
    return blockchunk, rest


# Endpoint for compute nodes to get a task
# This will update the corresponding job and set the status to "processing"
@app.get("/getTask")
async def get_task(request: Request, response: Response):
    # TODO: Authentication
    # Parse json
    try:
        task = await request.json()
    except Exception as e:
        logger.error("Exception while parsing json: {}".format(str(e)))
        raise invalidJson

    # Error handling
    if "taskType" not in task:
        raise missingTaskType

    if task["taskType"] == "segmentation":
        required_status = JobStatus.segmentation_queued
        new_status = JobStatus.segmentation_processing
    elif task["taskType"] == "embedding":
        if "chunkSize" not in task:
            raise missingChunkSize
        if int(task["chunkSize"]) < 2:
            raise invalidChunkSize
        required_status = [JobStatus.embedding_queued, JobStatus.embedding_queued_and_processing]
        new_status = JobStatus.embedding_queued_and_processing
    elif task["taskType"] == "clustering":
        required_status = JobStatus.clustering_queued
        new_status = JobStatus.clustering_processing
    else:
        raise invalidTaskType

    logger.debug("Host {} requested {}-task".format(request.client.host, task["taskType"]))

    # TODO: Check for timed out jobs and put back in queue
    for job in queue:
        if hasattr(job, 'status') and job.status in required_status:
            job.status = new_status
            logger.info("Host {} gets {}-task for JobId {}".format(request.client.host, task["taskType"], job.id))
            if task["taskType"] == "segmentation":
                return {"jobId": job.id, "submissions": job.submissions}
            elif task["taskType"] == "embedding":
                # Create chunk of blocks for embedding node
                chunk, rest = createEmbeddingChunk(job.blocks, task["chunkSize"])
                job.embedding_task_count += 1
                new_task = EmbeddingTask(id=job.embedding_task_count, course_id=job.course_id, blocks=chunk)
                job.embedding_tasks.append(new_task)
                job.blocks = rest
                if len(job.blocks) == 0:
                    job.status = JobStatus.embedding_processing
                logger.info("embedding-task for JobId {} created: taskId={}, size={}".format(job.id,
                                                                                             new_task.id,
                                                                                             task["chunkSize"]))
                return {"jobId": job.id,
                        "taskId": new_task.id,
                        "courseId": new_task.course_id,
                        "blocks": new_task.blocks}
            elif task["taskType"] == "clustering":
                return {"jobId": job.id, "embeddings": job.embeddings}
            else:
                logger.error("Error with taskType {}".format(task["taskType"]))
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {'Problem with taskType'}
    response.status_code = status.HTTP_204_NO_CONTENT
    return {'No {}-task available'.format(str(task["taskType"]))}


# Endpoint for compute nodes to send back their task results
# This will update the job and queue up the subsequent task
@app.post("/sendTaskResult")
async def send_result(request: Request, response: Response):
    # TODO: Authentication
    # Parse json
    try:
        result = await request.json()
    except Exception as e:
        logger.error("Exception while parsing json: {}".format(str(e)))
        raise invalidJson

    # Error handling
    if "jobId" not in result:
        raise missingJobId
    if not str(result["jobId"]).isdigit():
        raise invalidJobId
    if "resultType" not in result:
        raise missingResultType
    if result["resultType"] not in ["segmentation", "embedding", "clustering"]:
        raise invalidResultType

    logger.debug("Host {} sent result for {}-task with jobId {}".format(request.client.host,
                                                                        result["resultType"],
                                                                        result["jobId"]))

    # Search for job with provided jobId
    for job in queue:
        if job.id == int(result["jobId"]):
            # Segmentation results
            if job.status == JobStatus.segmentation_processing and result["resultType"] == "segmentation":
                if "textBlocks" not in result:
                    raise missingTextBlocks
                # Transform segmentation result to blocks (embedding input)
                for block in result["textBlocks"]:
                    submission_id = int(block["id"])
                    start_index = int(block["startIndex"])
                    end_index = int(block["endIndex"])
                    # Search for the corresponding submission and create block out of segmentation result information
                    for submission in job.submissions:
                        if submission["id"] == submission_id:
                            block_text = submission["text"][start_index:end_index]
                            id_string = str(submission_id) + ";"\
                                        + str(start_index) + "-"\
                                        + str(end_index) + ";"\
                                        + block_text
                            block_id = hashlib.sha1(id_string.encode()).hexdigest()
                            job.blocks.append({"id": block_id,
                                               "text": block_text,
                                               "startIndex": start_index,
                                               "endIndex": end_index,
                                               "type": "AUTOMATIC"})
                            break
                job.status = JobStatus.embedding_queued
                logger.info("JobId {} transitioned to status {}".format(job.id, job.status))
                # Trigger embedding nodes
                triggerNodes(node_type=NodeType.embedding)
                return {'Updated job: processed segmentation results'}
            # Embedding results
            elif (job.status == JobStatus.embedding_processing
                  or job.status == JobStatus.embedding_queued_and_processing)\
                    and result["resultType"] == "embedding":
                if "embeddings" not in result:
                    raise missingEmbeddings
                if "taskId" not in result:
                    raise missingTaskId

                # Add results to job and remove corresponding embedding-task out of queue
                valid_results = False
                for task in job.embedding_tasks:
                    if str(task.id) == str(result["taskId"]):
                        # Check if number of embeddings is correct
                        if not len(task.blocks) == len(result["embeddings"]):
                            raise invalidResults
                        for embedding in result["embeddings"]:
                            job.embeddings.append(embedding)
                        valid_results = True
                        logger.info("embedding-task {} of JobId {} finished".format(task.id, job.id))
                        job.embedding_tasks.remove(task)
                        break

                if not valid_results:
                    raise noUpdateNeeded

                # Check if all embeddings of job finished
                if len(job.blocks) == 0 and len(job.embedding_tasks) == 0:
                    job.status = JobStatus.clustering_queued
                    logger.info("JobId {} transitioned to status {}".format(job.id, job.status))
                    # Trigger clustering nodes
                    triggerNodes(node_type=NodeType.clustering)

                return {'Updated job: processed embedding results'}
            # Clustering results
            elif job.status == JobStatus.clustering_processing and result["resultType"] == "clustering":
                if "clusters" not in result:
                    raise missingClusters
                job.clusters = result["clusters"]
                logger.info("Sending back results for jobId {} to Artemis (URL: {})".format(job.id, job.callback_url))
                # TODO: Send back results to Artemis via callback URL
                logger.info("Athene Job finished: " + str(job))
                queue.remove(job)
                return {'Updated job: processed clustering results'}
            # No valid request
            else:
                logger.info("No such update for jobId {} needed. Job status is {}".format(result["jobId"], job.status))
                raise noUpdateNeeded
    raise invalidJobId


# Provides statistics about the number of jobs summarized by their status
@app.get("/queueStatus")
def queueStatus():
    total\
        = segmentation_queued\
        = segmentation_processing\
        = embedding_queued\
        = embedding_queued_and_processing \
        = pending_embedding_tasks \
        = embedding_processing\
        = clustering_queued\
        = clustering_processing\
        = pending = 0
    for job in queue:
        pending += 1
        if job.status == JobStatus.segmentation_queued:
            segmentation_queued += 1
        elif job.status == JobStatus.segmentation_processing:
            segmentation_processing += 1
        elif job.status == JobStatus.embedding_queued:
            embedding_queued += 1
        elif job.status == JobStatus.embedding_queued_and_processing:
            embedding_queued_and_processing += 1
            pending_embedding_tasks += len(job.embedding_tasks)
        elif job.status == JobStatus.embedding_processing:
            embedding_processing += 1
            pending_embedding_tasks += len(job.embedding_tasks)
        elif job.status == JobStatus.clustering_queued:
            clustering_queued += 1
        elif job.status == JobStatus.clustering_processing:
            clustering_processing += 1
    total = job_counter
    finished = total - pending
    return {"segmentation_queued": segmentation_queued,
            "segmentation_processing": segmentation_processing,
            "embedding_queued": embedding_queued,
            "embedding_queued_and_processing": embedding_queued_and_processing,
            "embedding_processing": embedding_processing,
            "pending_embedding_tasks": pending_embedding_tasks,
            "clustering_queued": clustering_queued,
            "clustering_processing": clustering_processing,
            "finished": finished,
            "total": total}
