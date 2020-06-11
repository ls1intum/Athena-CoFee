

class Cluster:

    def __init__(self, id, block_ids, probabilities, distances):
        self.id = id
        self.block_ids = block_ids
        self.probabilities = probabilities
        self.distances = distances

    def contains_block(self, block_id):
        return block_id in self.block_ids

    def probability_of_block(self, block_id):
        if not self.contains_block(block_id):
            return 0.0
        else:
            index = self.block_ids.index(block_id)
            return self.probabilities[index]

    @staticmethod
    def clusters_from_network_response(response):
        clusters = []
        for id, cluster_data in response.items():
            block_ids = [block["id"] for block in cluster_data["blocks"]]
            clusters.append(Cluster(id, block_ids, cluster_data["probabilities"], cluster_data["distanceMatrix"]))
        return clusters

    def __str__(self):
        return "Cluster {} with blocks {}".format(self.id, self.block_ids)


