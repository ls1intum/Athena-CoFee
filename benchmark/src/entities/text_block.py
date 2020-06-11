from benchmark.src.data.data_cleaner import clean_data


class TextBlock:
    __last_id = 0

    def __init__(self, text, id=None, ground_truth_cluster=None, ground_truth_grade=None):
        self.text = text
        self.ground_truth_cluster = ground_truth_cluster
        self.ground_truth_grade = ground_truth_grade
        self.cluster = None
        self.grade_from_cluster = None
        self.probability_in_cluster = None
        if id is None:
            TextBlock.__last_id = TextBlock.__last_id + 1
            self.id = TextBlock.__last_id
        else:
            self.id = id
            TextBlock.__last_id = id

    def __str__(self):
        self.text.__str__()

    def json_rep(self):
        return {
            'id': self.id,
            'text': self.text
        }

    def extract_cluster(self, clusters: list):
        self.cluster = [cluster for cluster in clusters if cluster.contains_block(self.id)][0]
        self.probability_in_cluster = self.cluster.probability_of_block(self.id)

    def similar(self, other):
        return self.cluster.id == other.cluster.id

    def ground_truth_similar(self, other):
        return self.ground_truth_cluster == other.ground_truth_cluster

    def clean_text(self):
        self.text = clean_data(self.text)

    def compute_grade_from_cluster(self, text_blocks):
        if self.cluster is None:
            raise Exception("cluster for text block {} not defined".format(self.id))
        cluster_grades = [block.ground_truth_grade for block in text_blocks if block.cluster == self.cluster]
        self.grade_from_cluster = sum(cluster_grades) / float(len(cluster_grades))

    @staticmethod
    def from_sentences(sentences):
        return [TextBlock(sentence) for sentence in sentences]
