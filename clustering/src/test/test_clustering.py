from unittest import TestCase
import numpy as np
import pandas as pd
from collections import Counter

from src.clustering import Clustering

# needed for compatibility with nltk, which assumes an old numpy version
np.int = int
np.bool = bool

# Reference values for the used sentences

# sentences_flowers = ["A second flower blossomed and remained.",
#                         "I have red and yellow flowers.",
#                         "flowers and roses are beautiful.",
#                         "She picked the flower up and smelled it."]
# sentences_software = ["this is the clustering component of the text assessment software engineering project",
#                          "In software engineering, a software design pattern is a general, reusable solution to a commonly occurring problem within a given context in software design.",
#                          "Patterns in software engineering is a lecture at TUM",
#                          "Software engineering is defined as a process of analyzing user requirements and then designing, building, and testing software"]
# sentences_law = ["the congress decided against this law",
#                     "I want to study law and become a lawyer",
#                     "you can't break the law like this",
#                     "Breaking the law is usually punished with jail"]


class TestClustering(TestCase):
    clustering = Clustering()
    # Read the precomputed embeddings here
    embeddings_flowers = pd.read_csv('src/test/exampleEmbeddings/flower_embeddings.csv').values.tolist()
    embeddings_software = pd.read_csv('src/test/exampleEmbeddings/software_embeddings.csv').values.tolist()
    embeddings_law = pd.read_csv('src/test/exampleEmbeddings/law_embeddings.csv').values.tolist()
    embeddings_same = pd.read_csv('src/test/exampleEmbeddings/same_sentence_embeddings.csv').values.tolist()
    embeddings_oose = pd.read_csv('src/test/exampleEmbeddings/example_embeddings.csv').values.tolist()

    def test_cluster_same_sentences(self):
        clusters = self.clustering.cluster(self.embeddings_same)[0]
        self.assertEqual(len(set(clusters)), 1)

    def test_cluster_similar_sentences(self):
        clusters = self.clustering.cluster(self.embeddings_flowers)[0]
        self.assertEqual(len(set(clusters)), 1)

        clusters = self.clustering.cluster(self.embeddings_software)[0]
        self.assertEqual(len(set(clusters)), 1)

        clusters = self.clustering.cluster(self.embeddings_law)[0]
        self.assertEqual(len(set(clusters)), 1)

    def test_cluster_different_topics(self):
        embeddings = self.embeddings_flowers + self.embeddings_software + self.embeddings_law
        clusters = self.clustering.cluster(embeddings)[0]
        clusters_flowers, clusters_software, clusters_law = np.split(clusters, [4, 8])
        print("Clusters: ", clusters)
        self.assertEqual(len(set(clusters)), 3)
        # test: all sentences with the same topic are in the same cluster
        self.assertEqual(len(set(clusters_flowers)), 1)
        self.assertEqual(len(set(clusters_software)), 1)
        self.assertEqual(len(set(clusters_law)), 1)

    # tests the function label_to_tree_id
    def test_tree_id(self):
        embeddings = self.embeddings_flowers + self.embeddings_software + self.embeddings_law + self.embeddings_oose
        clusters = self.clustering.cluster(embeddings)[0]
        self.assertEqual(len(set(clusters)), 3)
        counter = Counter(clusters)
        tree = self.clustering.clusterer.condensed_tree_.to_pandas()
        self.assertEqual(self.clustering.label_to_tree_id(-1), -1)
        # test: child_size of the node found == number of blocks in the cluster
        self.assertEqual(tree[tree.child == self.clustering.label_to_tree_id(0)]['child_size'].values.tolist()[0],
                         counter[0])
        self.assertEqual(tree[tree.child == self.clustering.label_to_tree_id(1)]['child_size'].values.tolist()[0],
                         counter[1])
        self.assertEqual(tree[tree.child == self.clustering.label_to_tree_id(2)]['child_size'].values.tolist()[0],
                         counter[2])

