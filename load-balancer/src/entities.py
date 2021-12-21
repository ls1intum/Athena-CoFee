from datetime import datetime
from numpy import array

Word = str
Sentence = str
ElmoVector = array


class NodeType:
    segmentation = "segmentation"
    embedding = "embedding"
    clustering = "clustering"
    gpu = "gpu"


class JobStatus:
    # Job submission by Artemis done, segmentation queued
    segmentation_queued = "segmentation_queued"
    # Segmentation node got segmentation task and is currently processing it
    segmentation_processing = "segmentation_processing"
    # Segmentation done, embedding queued
    embedding_queued = "embedding_queued"
    # Some embedding node already started processing, but there are more tasks for embedding remaining
    embedding_queued_and_processing = "embedding_queued_and_processing"
    # Embedding node got last embedding task and is currently processing it
    embedding_processing = "embedding_processing"
    # Embedding done, embedding queued
    clustering_queued = "clustering_queued"
    # Clustering node got clustering task and is currently processing it
    clustering_processing = "clustering_processing"
    # All calculation done, sending results back
    sending_back = "sending_back"


class Embedding:
    id: str
    vector: ElmoVector

    def __init__(self, id: str, vector: ElmoVector):
        self.id = id
        self.vector = vector

    @classmethod
    def from_dict(cls, dict: dict) -> 'Embedding':
        return cls(dict['id'], dict['vector'])


class EmbeddingTask:
    id: int
    course_id: int
    blocks = list()
    submission_date: str

    def __init__(self, id: int, course_id: int, blocks: dict):
        self.id = id
        self.course_id = course_id
        self.submission_date = datetime.now()
        self.blocks = blocks


class AtheneJob:
    id: int                         # Consecutive number
    course_id: int                  # Sent by Artemis
    callback_url: str               # Sent by Artemis to send back results
    submissions: dict               # Sent by Artemis
    submission_date: str            # Timestamp
    blocks: list                    # Blocks calculated from segmentation result
    blocks_to_embed: list           # Blocks remaining for embedding
    embeddings: list                # Embedding results
    embedding_tasks: list           # List of pending embedding-tasks
    embedding_task_count: int       # Counter to assign taskId's
    clusters: dict                  # Clustering result
    distanceMatrix: list            # distance Matrix for blocks
    clusterTree: list               # cluster tree of the clusters
    status: str                     # See class JobStatus

    def __init__(self, id: int, course_id: int, callback_url: str, submissions: dict):
        self.id = id
        self.course_id = course_id
        self.callback_url = callback_url
        self.submissions = submissions
        self.submission_date = datetime.now()
        self.blocks = list()
        self.blocks_to_embed = list()
        self.embeddings = list()
        self.embedding_tasks = list()
        self.embedding_task_count = 0
        self.status = JobStatus.segmentation_queued

    def __str__(self):
        return "AtheneJob - ID: " + str(self.id) + ", courseId: " + str(self.course_id) + ", CallbackURL: " + str(self.callback_url) + ", submission_date: " + str(self.submission_date)


class ComputeNode:
    name: str  # Can be chosen freely (Appears in log)
    type: str  # Defines NodeType
    url: str  # URL of the trigger-API
    username: str      # Username for the trigger-API (only gpu-nodes)
    password: str      # Password for the trigger-API (only gpu-nodes)

    def __init__(self, name: str, type: str, url: str):
        self.name = name
        self.type = type
        self.url = url

    def __str__(self):
        return "Name: " + self.name + ", Type: " + self.type + ", URL: " + self.url
