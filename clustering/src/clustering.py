from typing import List, Tuple
from numpy import array
from joblib import Memory
import hdbscan
from sklearn.metrics import pairwise_distances
from .entities import ElmoVector

class Clustering:

    clusterer = hdbscan.HDBSCAN(algorithm='best', alpha=1.0, approx_min_span_tree=True,
                                gen_min_span_tree=False, leaf_size=40, memory=Memory(cachedir=None),
                                metric='braycurtis', min_cluster_size=2, min_samples=None, p=None)

    def cluster(self, vectors: List[ElmoVector]) -> Tuple[array, array]:
        self.clusterer.fit(vectors)
        return (self.clusterer.labels_, self.clusterer.probabilities_)

    def visualize_tree(self, vectors: List[ElmoVector], show_clusters: bool):
        self.clusterer.fit(vectors)
        self.clusterer.condensed_tree_.plot(select_clusters=show_clusters)

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
