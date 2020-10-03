from numpy import array

Word = str
Sentence = str
ElmoVector = array


class TextBlock:
    id: str
    text: Sentence

    def __init__(self, id: str, text: Sentence = None):
        self.id = id
        if text is not None:
            self.text = text

    @classmethod
    def from_dict(cls, dict: dict) -> 'TextBlock':
        return cls(dict['id'], dict['text'])


class Embedding:
    id: str
    vector: ElmoVector

    def __init__(self, id: str, vector: ElmoVector):
        self.id = id
        self.vector = vector

    @classmethod
    def from_dict(cls, dict: dict) -> 'Embedding':
        return cls(dict['id'], dict['vector'])


class Feedback:
    id: str
    text: Sentence
    score: float
    feedbackEmbeddings: [ElmoVector]

    def __init__(self, _id: str, text: Sentence, score: float):
        self.id = _id
        self.text = text
        self.score = score
        self.feedbackEmbeddings = []


class FeedbackWithTextBlock:
    id: str
    cluster_id: str
    text: str
    text_embedding: ElmoVector
    feedback: Feedback

    def __init__(self, _id: str, cluster_id: str, text: str, feedback: Feedback):
        self.id = _id
        self.cluster_id = cluster_id
        self.text = text
        self.feedback = feedback

    def add_feedback_embedding(self, embedding: ElmoVector):
        self.feedback.feedbackEmbeddings.append(embedding)

