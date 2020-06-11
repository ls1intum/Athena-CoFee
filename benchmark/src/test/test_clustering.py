from unittest import TestCase

from benchmark.src.entities.text_block import TextBlock
from benchmark.src.networking.api_services import cluster, embed

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

embeddings_flowers = embed(TextBlock.from_sentences(sentences_flowers))
embeddings_software = embed(TextBlock.from_sentences(sentences_software))
embeddings_law = embed(TextBlock.from_sentences(sentences_law))


class TestClustering(TestCase):

    def test_cluster_same_sentences(self):
        embeddings_software_repeated = embed(TextBlock.from_sentences([sentences_software[0]] * 5))
        clusters = cluster(embeddings_software_repeated)
        print(clusters)
        self.assertEqual(1, len(clusters))

    def test_cluster_similar_sentences(self):
        clusters = cluster(embeddings_flowers)
        self.assertEqual(1, len(clusters))

        clusters = cluster(embeddings_software)
        self.assertEqual(1, len(clusters))

        clusters = cluster(embeddings_law)
        self.assertEqual(1, len(clusters))

    def test_cluster_different_topics(self):
        clusters = cluster(embeddings_flowers+embeddings_software+embeddings_law)
        # test: there are 3 different clusters
        self.assertEqual(3, len(clusters))
