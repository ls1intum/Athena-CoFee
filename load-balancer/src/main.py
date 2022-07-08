from .entities import AtheneJob, JobStatus, NodeType, Policy
from .errors import invalidAuthorization, invalidJson, missingCallbackUrl, missingSubmissions, missingTaskType,\
    missingChunkSize, invalidChunkSize, invalidTaskType, taskTypeError, missingJobId, invalidJobId, missingResultType,\
    invalidResultType, missingTextBlocks, missingEmbeddings, missingTaskId, invalidResults, noUpdateNeeded,\
    missingClusters, missingDistanceMatrix, missingClusterTree
from fastapi import BackgroundTasks, FastAPI, Request, Response, status
from requests.auth import HTTPBasicAuth
from src.ConfigParser import ConfigParser
from src.TaskFactory import TaskFactory
from src.JSONHandler import JSONHandler
from src.ResultJob import ClusteringResult
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


class JobQueue:

    def __init__(self):
        self.queue = list()
        self.job_counter = 0

    def get_queue(self):
        return self.queue

    def get_job_counter(self):
        return self.job_counter


jsonHandler = JSONHandler()
policy = Policy()
job_queue = JobQueue()
queue = job_queue.get_queue()
job_counter = job_queue.get_job_counter()



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

def triggerNodes(node_type: str):
    node_types = (NodeType.segmentation, NodeType.embedding, NodeType.clustering, NodeType.embedding_wmt, NodeType.gpu)
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


def sendBackResults(job: AtheneJob):
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
        response = requests.post(job.callback_url, data=final_result, headers=headers, timeout=1800)
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

    job_request = await JSONHandler.parseJson(request)

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

    JSONHandler.writeJsonToFile(job_counter, "submission", job_request)
    new_job = AtheneJob(id=job_counter,
                        course_id=course_id,
                        callback_url=job_request["callbackUrl"],
                        submissions=job_request["submissions"],
                        multilingual=job_request["multilingual"])
    queue.append(new_job)
    logger.info("New Athene Job added: " + str(new_job))
    # Trigger segmentation nodes
    triggerNodes(node_type=NodeType.segmentation)
    # Trigger GPU Server
    triggerNodes(node_type=NodeType.gpu)
    return {"detail": "Submission successful"}


# Endpoint for compute nodes to get a task
# This will update the corresponding job and set the status to "processing"

@app.get("/getTask")
async def get_task(request: Request, response: Response):
    checkAuthorization(request)
    task = await JSONHandler.parseJson(request)

    required_status, new_status = TaskFactory.set_status(task)
    logger.info("Host {} requested {}-task".format(request.client.host, task["taskType"]))

    # TODO: Check for timed out jobs and put back in queue
    for job in queue:
        if hasattr(job, 'status') and job.status in required_status:
            job.status = new_status
            logger.info("Host {} gets {}-task for JobId {}".format(request.client.host, task["taskType"], job.id))
            defined_job = TaskFactory.define_job(task, job)
            return defined_job.perform_task()
    response.status_code = status.HTTP_204_NO_CONTENT
    return {"detail": "No {}-task available".format(str(task["taskType"]))}


# Endpoint for compute nodes to send back their task results
# This will update the job and queue up the subsequent task
@app.post("/sendTaskResult")
async def send_result(request: Request, response: Response, background_tasks: BackgroundTasks):
    checkAuthorization(request)

    result = await JSONHandler.parseJson(request)

    # Error handling
    if "jobId" not in result:
        raise missingJobId
    if not str(result["jobId"]).isdigit():
        raise invalidJobId
    if "resultType" not in result:
        raise missingResultType
    if result["resultType"] not in ["segmentation", "embedding", "clustering", "embedding_wmt"]:
        raise invalidResultType


    logger.info("Host {} sent result for {}-task with jobId {}".format(request.client.host,
                                                                        result["resultType"],
                                                                        result["jobId"],
                                                                        ))

    # Search for job with provided jobId
    for job in queue:
        if job.id == int(result["jobId"]):

            result_type = TaskFactory.define_result(job, result)

            result_type.send_result(job, result)

            if isinstance(result_type, ClusteringResult):
                background_tasks.add_task(sendBackResults, job)




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