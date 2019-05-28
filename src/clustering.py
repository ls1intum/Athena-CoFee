from typing import List, Tuple
from numpy import array
from joblib import Memory
import hdbscan

clusterer = hdbscan.HDBSCAN(algorithm='best', alpha=1.0, approx_min_span_tree=True,
    gen_min_span_tree=False, leaf_size=40, memory=Memory(cachedir=None),
    metric='braycurtis', min_cluster_size=2, min_samples=None, p=None)

def cluster(vectors: List[array]) -> Tuple[array, array]:
    clusterer.fit(vectors)
    return (clusterer.labels_, clusterer.probabilities_)