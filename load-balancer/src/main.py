from .entities import AtheneJob, JobStatus, NodeType, EmbeddingTask
from .errors import invalidAuthorization, invalidJson, missingCallbackUrl, missingSubmissions, missingTaskType,\
    missingChunkSize, invalidChunkSize, invalidTaskType, taskTypeError, missingJobId, invalidJobId, missingResultType,\
    invalidResultType, missingTextBlocks, missingEmbeddings, missingTaskId, invalidResults, noUpdateNeeded,\
    missingClusters, missingDistanceMatrix, missingClusterTree
from fastapi import BackgroundTasks, FastAPI, Request, Response, status
from requests.auth import HTTPBasicAuth
from src.ConfigParser import ConfigParser
import hashlib
import logging
import os
import requests
import sys
import src.clustering_pb2 as Protobuf

logger = logging.getLogger()
# Set log_level to logging.DEBUG to write log files with json contents (see writeJsonToFile())
# Warning: This will produce a lot of data in production systems
log_level = logging.INFO
logger.setLevel(log_level)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()
queue = list()
job_counter = 0

def sizeof(obj):
    size = sys.getsizeof(obj)
    if isinstance(obj, dict): return size + sum(map(sizeof, obj.keys())) + sum(map(sizeof, obj.values()))
    if isinstance(obj, (list, tuple, set, frozenset)): return size + sum(map(sizeof, obj))
    return size

def checkAuthorization(request: Request):
    auth_secret = str(os.environ['AUTHORIZATION_SECRET']) if "AUTHORIZATION_SECRET" in os.environ else ""
    if auth_secret == "":
        logger.warning("No Authorization secret set")
        return

    if request.headers.get("Authorization") != auth_secret:
        logger.error("Host {} placed a request with an invalid secret: {}".format(request.client.host,
                                                                                  request.headers.get("Authorization")))
        raise invalidAuthorization


async def parseJson(request: Request):
    try:
        return await request.json()
    except Exception as e:
        logger.error("Exception while parsing json: {}".format(str(e)))
        raise invalidJson


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
        if node_type == NodeType.gpu:
            requests.post(node.url, auth=HTTPBasicAuth(node.username, node.password))
        else:
            requests.post(node.url, timeout=5)


def potentiallyRewriteCallbackUrl(url: str):
    is_localhost_url = url.startswith("http://localhost/") or url.startswith("http://localhost:")
    if is_localhost_url and "REWRITE_LOCALHOST_CALLBACK_URL_TO" in os.environ:
        logger.info("Rewriting localhost callback url to {}".format(os.environ["REWRITE_LOCALHOST_CALLBACK_URL_TO"]))
        return url.replace("http://localhost", os.environ["REWRITE_LOCALHOST_CALLBACK_URL_TO"], 1)
    return url


def sendBackResults(job: AtheneJob):
    job.callback_url = potentiallyRewriteCallbackUrl(job.callback_url)
    logger.info("Sending back results for jobId {} to Artemis (URL: {})".format(job.id, job.callback_url))
    response = Protobuf.AtheneResponse()
    del job.distanceMatrix
    del job.clusterTree
    del job.embeddings

    logger.info("Job has size {}.".format(sizeof(job)))
    logger.info("Converting Segments into Protobuf format.")
    for block in job.blocks:
        segment = response.segments.add()
        segment.id = block["id"]
        segment.submissionId = block["submissionId"]
        segment.startIndex = block["startIndex"]
        segment.endIndex = block["endIndex"]
        segment.text = block["text"]
    del job.blocks

    logger.info("Converting Clusters into Protobuf format.")
    for cluster in job.clusters.values():
        c = response.clusters.add()
        c.treeId = cluster["treeId"]
        for block in cluster["blocks"]:
            segment = c.segments.add()
            segment.id = block["id"]
        dm = cluster["distanceMatrix"]
        for i in range(len(dm)):
            for j in range(len(dm[i])):
                entry = c.distanceMatrix.add()
                entry.x = i
                entry.y = j
                entry.value = dm[i][j]
    del job.clusters

    # Currently unused:
    #
    #
    # for i in range(len(job.distanceMatrix)):
    #     for j in range(len(job.distanceMatrix[i])):
    #         entry = response.distanceMatrix.add()
    #         entry.x = i
    #         entry.y = j
    #         entry.value = job.distanceMatrix[i][j]
    # del job.distanceMatrix
    #
    # for leaf in job.clusterTree:
    #     node = response.clusterTree.add()
    #     node.parent = leaf["parent"]
    #     node.child = leaf["child"]
    #     node.lambdaVal = leaf["lambdaVal"]
    #     node.childSize = leaf["childSize"]
    # del job.clusterTree
    #

    logger.info("Protobuf builder has size {}.".format(sizeof(response)))
    final_result = response.SerializeToString()
    del response;
    logger.info("Serialized Protobuf has size {}.".format(sizeof(final_result)))
    try:
        auth_secret = str(os.environ['AUTHORIZATION_SECRET']) if "AUTHORIZATION_SECRET" in os.environ else ""
        headers = {
            "Authorization": auth_secret,
            "Content-type": "application/x-protobuf"
        }
        response = requests.post(job.callback_url, data=final_result, headers=headers, timeout=600)
        if response.status_code == status.HTTP_200_OK:
            logger.info("Callback successful")
            logger.info("Athene Job finished: " + str(job))
            queue.remove(job)
        else:
            logger.error("Callback failed. Status Code {}: {}".format(str(response.status_code), str(response.content)))
            # TODO: Retry callback
    except Exception as e:
        logger.error("Exception while sending back results: {}".format(str(e)))
        # TODO: Retry callback


# Endpoint for Artemis to submit a job
# This will create a new job and queue up the first task (segmentation)
@app.post("/submit")
async def submit_job(request: Request, response: Response):
    checkAuthorization(request)

    job_request = await parseJson(request)

    # Error handling
    if "courseId" in job_request:
        course_id = job_request["courseId"]
    else:
        course_id = -1

    if "callbackUrl" not in job_request:
        raise missingCallbackUrl

    if "submissions" not in job_request:
        raise missingSubmissions

    # Queue up new job
    global job_counter
    job_counter += 1
    writeJsonToFile(job_counter, "submission", job_request)
    new_job = AtheneJob(id=job_counter,
                        course_id=course_id,
                        callback_url=job_request["callbackUrl"],
                        submissions=job_request["submissions"])
    queue.append(new_job)
    logger.info("New Athene Job added: " + str(new_job))
    # Trigger segmentation nodes
    triggerNodes(node_type=NodeType.segmentation)
    # Trigger GPU Server
    triggerNodes(node_type=NodeType.gpu)
    return {"detail": "Submission successful"}


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
    checkAuthorization(request)

    task = await parseJson(request)

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

    logger.info("Host {} requested {}-task".format(request.client.host, task["taskType"]))

    # TODO: Check for timed out jobs and put back in queue
    for job in queue:
        if hasattr(job, 'status') and job.status in required_status:
            job.status = new_status
            logger.info("Host {} gets {}-task for JobId {}".format(request.client.host, task["taskType"], job.id))
            if task["taskType"] == "segmentation":
                response_json = {"jobId": job.id, "submissions": job.submissions}
                writeJsonToFile(job.id, "segmentation_task", response_json)
                return response_json
            elif task["taskType"] == "embedding":
                # Create chunk of blocks for embedding node
                chunk, rest = createEmbeddingChunk(job.blocks_to_embed, task["chunkSize"])
                job.embedding_task_count += 1
                new_task = EmbeddingTask(id=job.embedding_task_count, course_id=job.course_id, blocks=chunk)
                job.embedding_tasks.append(new_task)
                job.blocks_to_embed = rest
                if len(job.blocks_to_embed) == 0:
                    job.status = JobStatus.embedding_processing
                logger.info("embedding-task for JobId {} created: "
                            "taskId={}, size={}/{} (actual/requested)".format(job.id,
                                                                              new_task.id,
                                                                              len(new_task.blocks),
                                                                              task["chunkSize"]))

                response_json = {"jobId": job.id,
                                 "taskId": new_task.id,
                                 "courseId": new_task.course_id,
                                 "blocks": new_task.blocks}
                writeJsonToFile(job.id, "embedding_task_" + str(new_task.id), response_json)
                return response_json
            elif task["taskType"] == "clustering":
                response_json = {"jobId": job.id, "embeddings": job.embeddings}
                writeJsonToFile(job.id, "clustering_task", response_json)
                return response_json
            else:
                logger.error("Error with taskType {}".format(task["taskType"]))
                raise taskTypeError
    response.status_code = status.HTTP_204_NO_CONTENT
    return {"detail": "No {}-task available".format(str(task["taskType"]))}


# Endpoint for compute nodes to send back their task results
# This will update the job and queue up the subsequent task
@app.post("/sendTaskResult")
async def send_result(request: Request, response: Response, background_tasks: BackgroundTasks):
    checkAuthorization(request)

    result = await parseJson(request)

    # Error handling
    if "jobId" not in result:
        raise missingJobId
    if not str(result["jobId"]).isdigit():
        raise invalidJobId
    if "resultType" not in result:
        raise missingResultType
    if result["resultType"] not in ["segmentation", "embedding", "clustering"]:
        raise invalidResultType

    logger.info("Host {} sent result for {}-task with jobId {}".format(request.client.host,
                                                                        result["resultType"],
                                                                        result["jobId"]))

    # Search for job with provided jobId
    for job in queue:
        if job.id == int(result["jobId"]):
            # Segmentation results
            if job.status == JobStatus.segmentation_processing and result["resultType"] == "segmentation":
                if "textBlocks" not in result:
                    raise missingTextBlocks
                writeJsonToFile(job.id, "segmentation_result", result)
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
                            new_block = {"id": block_id,
                                        "submissionId": submission_id,
                                        "text": block_text,
                                        "startIndex": start_index,
                                        "endIndex": end_index,
                                        "type": "AUTOMATIC"}
                            job.blocks.append(new_block)                # Will persist in job
                            job.blocks_to_embed.append(new_block)       # Will get removed with embedding queries
                            break
                job.status = JobStatus.embedding_queued
                logger.info("JobId {} transitioned to status {}".format(job.id, job.status))
                # Trigger embedding nodes
                triggerNodes(node_type=NodeType.embedding)
                return {"detail": "Updated job: processed segmentation results"}
            # Embedding results
            elif (job.status == JobStatus.embedding_processing
                  or job.status == JobStatus.embedding_queued_and_processing)\
                    and result["resultType"] == "embedding":
                if "embeddings" not in result:
                    raise missingEmbeddings
                if "taskId" not in result:
                    raise missingTaskId

                writeJsonToFile(job.id, "embedding_result_" + str(result["taskId"]), result)

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
                if len(job.blocks_to_embed) == 0 and len(job.embedding_tasks) == 0:
                    job.status = JobStatus.clustering_queued
                    logger.info("JobId {} transitioned to status {}".format(job.id, job.status))
                    # Trigger clustering nodes
                    triggerNodes(node_type=NodeType.clustering)

                return {"detail": "Updated job: processed embedding results"}
            # Clustering results
            elif job.status == JobStatus.clustering_processing and result["resultType"] == "clustering":
                if "clusters" not in result:
                    raise missingClusters
                if "distanceMatrix" not in result:
                    raise missingDistanceMatrix
                if "clusterTree" not in result:
                    raise missingClusterTree

                writeJsonToFile(job.id, "clustering_result", result)

                job.clusters = result["clusters"]
                job.distanceMatrix = result["distanceMatrix"]
                job.clusterTree = result["clusterTree"]

                # Send back results to Artemis via callback URL in the background
                job.status = JobStatus.sending_back
                background_tasks.add_task(sendBackResults, job)
                return {"detail": "Updated job: processed clustering results"}
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
        = sending_back\
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
        elif job.status == JobStatus.sending_back:
            sending_back += 1
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
            "sending_back": sending_back,
            "finished": finished,
            "total": total}
