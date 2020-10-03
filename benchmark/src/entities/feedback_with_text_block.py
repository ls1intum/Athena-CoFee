
class FeedbackWithTextBlock:

    def __init__(self, feedback_id: int, feedback_text: str, feedback_score: float, reference: str, textblock_id: str, text: str,
                 submission_id: int, cluster_id: int):
        self.id = textblock_id
        self.submission_id = submission_id
        self.cluster_id = cluster_id
        self.text = text
        self.feedback_id = feedback_id
        self.feedback_text = feedback_text
        self.feedback_score = feedback_score
        self.reference = reference

    def json_rep(self):
        return {
            'textBlockId': self.id,
            'clusterId': str(self.cluster_id),
            'text': self.text,
            'feedbackId': str(self.feedback_id),
            'feedbackText': self.feedback_text,
            'credits': self.feedback_score
        }
