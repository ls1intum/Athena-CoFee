from abc import ABC, abstractmethod
from logging import getLogger


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


class GradeBasedSimilarity(SimilarityMeasure):
    __logger = getLogger(__name__)

    def __init__(self, text_blocks):
        for text_block in text_blocks:
            text_block.compute_grade_from_cluster(text_blocks)
        self.l2_loss = sum(
            [pow((text_block.grade_from_cluster - text_block.ground_truth_grade), 2) for text_block in text_blocks])

    def output_results(self):
        self.__logger.info('The L2 loss for the model is {}'.format(self.l2_loss))
