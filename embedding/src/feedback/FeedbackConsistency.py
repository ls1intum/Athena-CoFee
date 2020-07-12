import pickle
import numpy as np
from logging import getLogger
from sklearn.metrics import pairwise_distances, silhouette_score
from src.feedback.FeedbackCommentResource import FeedbackCommentResource


class FeedbackConsistency:
    __logger = getLogger(__name__)
    __feedback_with_text_blocks: list = None

    def __init__(self):
        self.__feedback_comment_resource = FeedbackCommentResource()
        self.__comment_threshold = 0.37
        self.__text_block_threshold = 0.21

    def __get_inconsistency(self, score_diff: float, comment_distance: float, text_block_distance: float):
        if text_block_distance < self.__text_block_threshold:
            if score_diff:
                return 'inconsistent score' if comment_distance < self.__comment_threshold else 'inconsistent feedback'
            else:
                return 'inconsistent comment' if comment_distance > self.__comment_threshold else None
        else:
            return None

    def __calculate_distance_with_silhouette_score(self, x: [], y: []):
        if len(x) < 2 and len(y) < 2:
            distance = pairwise_distances(X=x, Y=y, metric='cosine').flatten()[0]
        else:
            samples = np.concatenate((x, y))
            labels = np.concatenate([np.full((1, len(x)), 1).flatten(), np.full((1, len(y)), 2).flatten()])
            distance = silhouette_score(X=samples, labels=labels, metric='cosine')
        return distance

    def __calculate_mean_distance(self, x: [], y: []):
        distance = pairwise_distances(X=x, Y=y, metric='cosine')
        return np.mean(np.mean(distance, axis=1))

    def check_consistency(self, feedback_with_text_blocks):
        self.__logger.info("Check Consistencies")
        # Find embeddings for each feedback comment
        self.__feedback_with_text_blocks = self.__feedback_comment_resource.embed_feedback(feedback_with_tb=feedback_with_text_blocks)
        doc = {}
        # Compare each new assessment with the ones in the database
        for fwt in self.__feedback_with_text_blocks:
            vector_x = fwt.feedback.feedbackEmbeddings
            # Get the assessments which have same the same cluster id
            cluster = self.__feedback_comment_resource.get_feedback_in_same_cluster(cluster_id=fwt.cluster_id)
            distances = []
            # Calculate distances between each feedback embeddings and text block embeddings(student answers)
            for item in cluster:
                vector_y = list(map(lambda embedding: pickle.loads(embedding['embedding']),
                                    item['feedback']['feedback_text_blocks']))
                distance = self.__calculate_mean_distance(x=vector_x, y=vector_y)
                text_block_embeddings = self.__feedback_comment_resource.embed_feedback_text_blocks([fwt.text, item['text']])
                text_block_distance = self.__calculate_mean_distance(x=text_block_embeddings[0].reshape(1, -1).tolist(), y=text_block_embeddings[1].reshape(1, -1).tolist())
                inconsistency = self.__get_inconsistency(score_diff=abs(fwt.feedback.score - item['feedback']['feedback_score']), comment_distance=distance, text_block_distance=text_block_distance)
                if inconsistency:
                    distances.append({"second_feedback_id": item['feedback']['feedback_id'], "inconsistency_type": inconsistency})

            if distances:
                doc.update({"first_feedback_id": fwt.feedback.id, "comparison": distances})
        return None if not doc else doc

    def store_feedback(self):
        self.__feedback_comment_resource.store_feedback(self.__feedback_with_text_blocks)
