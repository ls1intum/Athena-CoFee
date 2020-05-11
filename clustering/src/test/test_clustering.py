from unittest import TestCase
import numpy as np
import matplotlib.pyplot as plt

from src.clustering import Clustering
from src.elmo import ELMo

sentences_flowers = ["A second flower blossomed and remained.",
                     "I have red and yellow  flowers",
                     "flowers and roses are beautiful",
                     "She picked the flower up and smelled it"]
sentences_software = ["this is the clustering component of the text assessment software engineering project",
                      "In software engineering, a software design pattern is a general, reusable solution to a commonly occurring problem within a given context in software design.",
                      "Patterns in software engineering is a lecture at TUM",
                      "Software engineering is defined as a process of analyzing user requirements and then designing, building, and testing software"]
sentences_law = ["the congress decided against this law",
                 "I want to study law and become lawyer",
                 "you can't brake the law like this",
                 "Law breaking is usually punished with jail"]


class TestClustering(TestCase):
    clustering = Clustering()
    elmo = ELMo()

    embeddings_flowers = elmo.embed_sentences(sentences_flowers)
    embeddings_software = elmo.embed_sentences(sentences_software)
    embeddings_law = elmo.embed_sentences(sentences_law)
    embeddings = embeddings_flowers+embeddings_software+embeddings_law

    def test_cluster_same_sentences(self):
        embeddings_same = self.elmo.embed_sentences([sentences_software[0]] * 10)
        clusters = self.clustering.cluster(embeddings_same)[0]
        self.assertEqual(len(set(clusters)), 1)

    def test_cluster_similar_sentences(self):
        clusters = self.clustering.cluster(self.embeddings_flowers)[0]
        self.assertEqual(len(set(clusters)), 1)

        clusters = self.clustering.cluster(self.embeddings_software)[0]
        self.assertEqual(len(set(clusters)), 1)

        clusters = self.clustering.cluster(self.embeddings_law)[0]
        self.assertEqual(len(set(clusters)), 1)

    def test_visualize_tree_structure(self):
        self.clustering.visualize_tree(self.embeddings, show_clusters=False)
        plt.show()

    def test_visualize_clusters(self):
        self.clustering.visualize_tree(self.embeddings, show_clusters=True)
        plt.show()

    def test_cluster_different_topics(self):
        clusters = self.clustering.cluster(self.embeddings)[0]
        clusters_flowers, clusters_software, clusters_law = np.split(clusters, [sentences_flowers.__len__(), sentences_flowers.__len__() + sentences_software.__len__()])
        # test: there are 3 different clusters
        self.assertEqual(len(set(clusters)), 3)
        # test: all sentences with the same topic are in the same cluster
        self.assertEqual(len(set(clusters_flowers)), 1)
        self.assertEqual(len(set(clusters_software)), 1)
        self.assertEqual(len(set(clusters_law)), 1)
