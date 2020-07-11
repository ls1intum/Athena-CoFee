from abc import ABC, abstractmethod
from logging import getLogger

import sklearn


class SimilarityMeasure(ABC):
    @abstractmethod
    def output_results(self):
        pass


class PrecisionRecallSimilarity(SimilarityMeasure):
    __logger = getLogger(__name__)

    def __init__(self, text_blocks):
        self.text_blocks = text_blocks
        self.false_negatives = 0
        self.false_positives = 0
        self.true_negatives = 0
        self.true_positives = 0

        for text_block in text_blocks:
            for other in text_blocks:
                if text_block.similar(other) and text_block.ground_truth_similar(other):
                    self.true_positives += 1
                if not (text_block.similar(other)) and not (text_block.ground_truth_similar(other)):
                    self.true_negatives += 1
                if text_block.similar(other) and not (text_block.ground_truth_similar(other)):
                    self.false_positives += 1
                if not (text_block.similar(other)) and text_block.ground_truth_similar(other):
                    self.false_negatives += 1

        self.precision = self.true_positives / (1.0 * (self.true_positives + self.false_positives))
        self.recall = self.true_positives / (1.0 * (self.true_positives + self.false_negatives))
        self.f1_score = 2 * ((self.precision * self.recall) / (self.precision + self.recall))

    def output_results(self):
        self.__logger.info('The achieved precision is {}'.format(self.precision))
        self.__logger.info('The achieved recall is {}'.format(self.recall))
        self.__logger.info('The achieved F1_score is {}'.format(self.f1_score))


class AdjustedRandIndexSimilarity(SimilarityMeasure):
    __logger = getLogger(__name__)

    def __init__(self, text_blocks):
        self.text_blocks = text_blocks
        labels_true = [text_block.ground_truth_cluster for text_block in self.text_blocks]
        labels_pred = [text_block.computed_cluster.id for text_block in self.text_blocks]
        self.ARI = sklearn.metrics.adjusted_rand_score(labels_true, labels_pred)

    def output_results(self):
        self.__logger.info('The achieved Adjusted Rand Index is {}'.format(self.ARI))


class L1Similarity(SimilarityMeasure):
    __logger = getLogger(__name__)

    def __init__(self, text_blocks):
        for text_block in text_blocks:
            text_block.compute_grade_from_cluster(text_blocks)
        self.text_blocks = [text_block for text_block in text_blocks if text_block.computed_cluster.id != -1]
        self.l1_loss = sum(
            [abs((text_block.grade_from_cluster - text_block.ground_truth_grade)) for text_block in text_blocks]) / \
                       len(text_blocks)

    def output_results(self):
        self.__logger.info('The L1 loss for the model is {}'.format(self.l1_loss))
        max_over_graded = max(self.text_blocks,
                              key=lambda text_block: text_block.grade_from_cluster - text_block.ground_truth_grade)
        self.__logger.info(
            "The most over-graded sentence is \"{}\". \n Assigned:{} but ground truth: {}".format(
                max_over_graded.original_text,
                max_over_graded.grade_from_cluster,
                max_over_graded.ground_truth_grade))
        max_under_graded = max(self.text_blocks,
                               key=lambda text_block: text_block.ground_truth_grade - text_block.grade_from_cluster)
        self.__logger.info(
            "The most under-graded sentence is \"{}\". \n Assigned:{} but ground truth: {}".format(
                max_under_graded.original_text,
                max_under_graded.grade_from_cluster,
                max_under_graded.ground_truth_grade))


class QWKSimilarity(SimilarityMeasure):
    __logger = getLogger(__name__)

    def __init__(self, text_blocks):
        for text_block in text_blocks:
            text_block.compute_grade_from_cluster(text_blocks)
        self.text_blocks = [text_block for text_block in text_blocks if text_block.computed_cluster.id != -1]

        ground_truth_grades = [text_block.ground_truth_grade for text_block in text_blocks]
        predicted_grades = [text_block.grade_from_cluster for text_block in text_blocks]

        avg_ground_truth_grades = sum(ground_truth_grades) / len(ground_truth_grades)
        avg_predicted_grades = sum(predicted_grades) / len(predicted_grades)

        var_ground_truth_grades = sum(
            [(ground_truth_grades[i] - avg_ground_truth_grades) ** 2 for i in range(len(ground_truth_grades))]) / len(
            ground_truth_grades)
        var_predicted_grades = sum(
            [(predicted_grades[i] - avg_predicted_grades) ** 2 for i in range(len(predicted_grades))]) / len(
            predicted_grades)

        cov = sum(
            [(predicted_grades[i] - avg_predicted_grades)*(ground_truth_grades[i] - avg_ground_truth_grades) for i in
             range(len(predicted_grades))]) / len(predicted_grades)

        self.QWK = (2 * cov) / (var_predicted_grades + var_ground_truth_grades + (
                    avg_ground_truth_grades - avg_predicted_grades) ** 2)

    def output_results(self):
        self.__logger.info('The QWK for the model is {}'.format(self.QWK))