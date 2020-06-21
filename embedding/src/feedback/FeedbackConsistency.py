import pickle
import numpy as np
from logging import getLogger
from sklearn.metrics import pairwise_distances, silhouette_score
from src.elmo import ELMo
from src.database.Connection import Connection


class FeedbackConsistency:
    __conn: Connection = None
    __elmo: ELMo = None
    __logger = getLogger(__name__)
    __collection = 'feedback'

    def __init__(self):
        self.__conn = Connection()
        self.base_threshold = 0.25
        self.upper_threshold = 0.75
        self.score_divider = 10

    def __get_feedback_in_same_cluster(self, cluster_id: int):
        __filter = {'cluster_id': cluster_id}
        try:
            result = self.__conn.find_documents(collection=self.__collection, filter_dict=__filter)
        except Exception as e:
            self.__logger.error(e)
            return None
        else:
            return result

    def __get_threshold(self, score_diff: float):
        threshold = self.base_threshold + score_diff / self.score_divider
        return threshold if threshold < self.upper_threshold else self.upper_threshold

    def __get_consistency(self, threshold: float, distance: float):
        lower_threshold = threshold - self.base_threshold
        if threshold >= distance >= lower_threshold:
            return "consistent"
        elif distance - threshold <= 0.05 or lower_threshold - distance <= 0.05:
            return "slight inconsistency"
        elif distance - threshold <= 0.1 or lower_threshold - distance <= 0.1:
            return "inconsistent"
        else:
            return "high inconsistency"

    def __calculate_distance_with_cohesion(self, x: [], y: []):
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
        response = {}
        for fwt in feedback_with_text_blocks:
            vector_x = fwt.feedback.feedbackEmbeddings
            cluster = self.__get_feedback_in_same_cluster(cluster_id=fwt.cluster_id)
            distances = []
            for item in cluster:
                vector_y = list(map(lambda embedding: pickle.loads(embedding['embedding']),
                                    item['feedback']['feedback_text_blocks']))
                distance = self.__calculate_distance_with_cohesion(x=vector_x, y=vector_y)
                threshold = self.__get_threshold(score_diff=abs(fwt.feedback.score - item['feedback']['feedback_score']))
                distances.append({"feedback_id": item['feedback']['feedback_id'], "distance": format(distance, '.4f'), "threshold": threshold, "consistency": self.__get_consistency(threshold=threshold, distance=abs(distance))})
            response.update({fwt.feedback.id: distances})
        return response
