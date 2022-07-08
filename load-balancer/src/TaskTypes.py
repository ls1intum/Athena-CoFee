from abc import abstractmethod

from .entities import JobStatus, EmbeddingTask
from .JSONHandler import JSONHandler, logger



class TaskJob:

    @staticmethod
    @abstractmethod
    def perform_task(self):
        pass


class EmbeddingJob(TaskJob):
    def __init__(self, task, job):
        self.task = task
        self.job = job
        pass

    def perform_task(self):
        # Create chunk of blocks for embedding node
        chunk, rest = self.createEmbeddingChunk(self.job.blocks_to_embed, self.task["chunkSize"])
        self.job.embedding_task_count += 1
        new_task = EmbeddingTask(id=self.job.embedding_task_count, course_id=self.job.course_id, blocks=chunk)
        self.job.embedding_tasks.append(new_task)
        self.job.blocks_to_embed = rest
        if len(self.job.blocks_to_embed) == 0:
            self.job.status = JobStatus.embedding_processing
        logger.info("embedding-task for JobId {} created: "
                    "taskId={}, size={}/{} (actual/requested)".format(self.job.id,
                                                                      new_task.id,
                                                                      len(new_task.blocks),
                                                                      self.task["chunkSize"]))

        response_json = {"jobId": self.job.id,
                         "taskId": new_task.id,
                         "courseId": new_task.course_id,
                         "blocks": new_task.blocks,
                         }
        JSONHandler.writeJsonToFile(self.job.id, "embedding_task_" + str(new_task.id), response_json)
        return response_json

    def createEmbeddingChunk(self, blocks, size):
        # Minimum of 2 blocks is required to compute embeddings - prevent 1 single remaining block
        if len(blocks) == (size + 1):
            size += 1

        blockchunk = blocks[0:min(len(blocks), size)]
        rest = blocks[min(len(blocks), size):]
        return blockchunk, rest


class SegmentationJob(TaskJob):

    def __init__(self, job):
        self.job = job
        pass

    def perform_task(self):
        response_json = {"jobId": self.job.id, "submissions": self.job.submissions}
        JSONHandler.writeJsonToFile(self.job.id, "segmentation_task", response_json)
        return response_json




class ClusteringJob(TaskJob):

    def __init__(self, job):
        self.job = job
        pass

    def perform_task(self):
        response_json = {"jobId": self.job.id, "embeddings": self.job.embeddings, "multilingual": self.job.multilingual}
        JSONHandler.writeJsonToFile(self.job.id, "clustering_task", response_json)
        return response_json
