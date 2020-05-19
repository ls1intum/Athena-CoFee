class TextBlock:
    __last_id = 0

    def __init__(self, text, id=None, ground_truth_cluster=None):
        self.text = text
        self.ground_truth_cluster = ground_truth_cluster
        self.cluster = None
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

    def similar(self, other):
        return self.cluster.id == other.cluster.id

    def ground_truth_similar(self, other):
        return self.ground_truth_cluster == other.ground_truth_cluster

    @staticmethod
    def from_sentences(sentences):
        return [TextBlock(sentence) for sentence in sentences]
