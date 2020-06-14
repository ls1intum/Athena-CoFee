class SimilarityMeasure:

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
        self.f1_score = 2 * ((self.precision*self.recall) / (self.precision+self.recall))


