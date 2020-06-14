
class FeedbackWithTextBlock:

    def __init__(self, feedback_id: int, feedback_text: str, feedback_score: float, reference: str, textblock_id: str, text: str,
                 submission_id: int, cluster_id: int, position_in_cluster: float, added_distance: float):
        self.id = textblock_id
        self.submission_id = submission_id
        self.cluster_id = cluster_id
        self.text = text
        self.position_in_cluster = position_in_cluster
        self.added_distance = added_distance
        self.feedback_id = feedback_id
        self.feedback_text = feedback_text
        self.feedback_score = feedback_score
        self.reference = reference

    def json_rep_text_block(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'cluster_id': self.cluster_id,
            'position_in_cluster': self.position_in_cluster,
            'added_distance': self.added_distance,
            'text': self.text,
            'reference': self.reference
        }

    def json_rep_feedback(self):
        return {
            'id': self.feedback_id,
            'text': self.feedback_text,
            'score': self.feedback_score,
            'reference': self.reference
        }
