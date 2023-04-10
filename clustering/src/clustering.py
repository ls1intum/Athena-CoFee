from .entities import ElmoVector
from joblib import Memory
from numpy import array
from sklearn.metrics import pairwise_distances
from typing import List, Tuple
import hdbscan


class Clustering:

    clusterer = hdbscan.HDBSCAN(algorithm='best', alpha=1.0, approx_min_span_tree=True,
                                gen_min_span_tree=False, leaf_size=40, memory=Memory(location=None),
                                metric='braycurtis', min_cluster_size=2, min_samples=None, p=None)

    def cluster(self, vectors: List[ElmoVector]) -> Tuple[array, array]:
        self.clusterer.fit(vectors)
        return (self.clusterer.labels_, self.clusterer.probabilities_)

    def distances_within_cluster(self, vectors: List[ElmoVector]) -> array:
        """
        Returns
        -------
        D : array [n_samples_a, n_samples_a] or [n_samples_a, n_samples_b]
            A distance matrix D such that D_{i, j} is the distance between the
            ith and jth vectors of the given matrix X, if Y is None.
            If Y is not None, then D_{i, j} is the distance between the ith array
            from X and the jth array from Y.
        """
        return pairwise_distances(vectors, metric='cosine')

    # Gets the id in the tree structure for given cluster label
    def label_to_tree_id(self, cluster_label):
        if cluster_label == -1:
            return -1
        points = []
        labels = self.clusterer.labels_
        for i in range(len(labels)):
            if labels[i] == cluster_label:
                points.append(i)
        return self.trace_ancestor(points)

    # For a given set of leaves in the given tree structure, finds and returns the first common ancestor
    def trace_ancestor(self, leaves):
        parents = []
        tree = self.clusterer.condensed_tree_.to_pandas()
        leaf_tree = tree[tree['child'].isin(leaves)]
        for parent in set(leaf_tree['parent'].values.tolist()):
            parents.append(parent)
        while len(parents) != 1:
            current_parent = max(parents)
            cell = tree[tree.child == current_parent]
            new_parent = (cell['parent'].values.tolist())[0]
            parents.remove(current_parent)
            if new_parent not in parents:
                parents.append(new_parent)
        return parents[0]
