import sys

from .errors import invalidTaskType, missingTaskType, invalidChunkSize, missingChunkSize, taskTypeError, noUpdateNeeded, \
    invalidJobId
from .TaskTypes import EmbeddingJob, SegmentationJob, ClusteringJob, TaskJob
from .entities import AtheneJob, JobStatus, NodeType, EmbeddingTask
import logging
from.ResultJob import SegmentationResult, EmbeddingResult, ClusteringResult

logger = logging.getLogger()

class TaskFactory:

    def __init__(self, job):
        self.job = job
        pass

    def set_status(task: dict):
        # Error handling
        if "taskType" not in task:
            raise missingTaskType

        if task["taskType"] == "segmentation":
            required_status = JobStatus.segmentation_queued
            new_status = JobStatus.segmentation_processing
            return required_status, new_status

        elif task["taskType"] == "embedding":
            if "chunkSize" not in task:
                raise missingChunkSize
            if int(task["chunkSize"]) < 2:
                raise invalidChunkSize
            required_status = [JobStatus.embedding_queued, JobStatus.embedding_queued_and_processing]
            new_status = JobStatus.embedding_queued_and_processing
            return required_status, new_status

        elif task["taskType"] == "clustering":
            required_status = JobStatus.clustering_queued
            new_status = JobStatus.clustering_processing
            return required_status, new_status
        else:
            raise invalidTaskType

    def define_job(task: dict, job : AtheneJob) -> TaskJob:
        if task["taskType"] == "segmentation":
            return SegmentationJob(job)
        elif task["taskType"] == "embedding":
            return EmbeddingJob(task, job)
        elif task["taskType"] == "clustering":
            return ClusteringJob(job)
        else:
            logger.error("Error with taskType {}".format(task["taskType"]))
            raise taskTypeError
        return

    def define_result(job, result):
        if job.status == JobStatus.segmentation_processing and result["resultType"] == "segmentation":
            return SegmentationResult()

        elif (job.status == JobStatus.embedding_processing
                      or job.status == JobStatus.embedding_queued_and_processing)\
                       and (result["resultType"] == "embedding" or result["resultType"] == "embedding_wmt"):
            return EmbeddingResult()

        elif job.status == JobStatus.clustering_processing and result["resultType"] == "clustering":
            return ClusteringResult()
        # No valid request
        else:
            logger.info("No such update for jobId {} needed. Job status is {}".format(result["jobId"], job.status))
            raise noUpdateNeeded
        raise invalidJobId





