from unittest import TestCase

from src.elmo import ELMo


class TestELMo(TestCase):

    def test_embed_sentences_number_of_vectors(self):
        elmo = ELMo()
        sentences = ["roses are red",
                    "this is the clustering component",
                    "In software engineering, a software design pattern is a general, reusable solution to a commonly occurring problem within a given context in software design.",
                    "Rather, it is a description or template for how to solve a problem that can be used in many different situations."]
        embeddings = elmo.embed_sentences(sentences)
        self.assertEqual(embeddings.__len__(), sentences.__len__())

    def test_embed_sentences_equal_length_of_vectors(self):
        elmo = ELMo()
        sentences = ["roses are red",
                     "this is the clustering component",
                     "In software engineering, a software design pattern is a general, reusable solution to a commonly occurring problem within a given context in software design.",
                     "Rather, it is a description or template for how to solve a problem that can be used in many different situations."]
        embeddings = elmo.embed_sentences(sentences)
        self.assertTrue(embeddings[0].__len__() == embeddings[1].__len__())
        self.assertTrue(embeddings[1].__len__() == embeddings[2].__len__())
        self.assertTrue(embeddings[2].__len__() == embeddings[3].__len__())

    def test_distance_same_sentence(self):
        elmo = ELMo()
        self.assertAlmostEqual(elmo.distance(("roses are red", "roses are red")), 0, 3)
        self.assertAlmostEqual(elmo.distance(("this is the clustering component", "this is the clustering component")), 0, 3)
        self.assertAlmostEqual(elmo.distance(("pattern", "pattern")), 0, 3)
        self.assertAlmostEqual(elmo.distance(("Do you want to get something to eat before the movie?", "Do you want to get something to eat before the movie?")), 0, 3)

    def test_distance_permutation(self):
        elmo = ELMo()
        self.assertAlmostEqual(elmo.distance(("The Unified Modeling Language (UML) is a general-purpose, developmental, modeling language in the field of software engineering that is intended to provide a standard way to visualize the design of a system",
                                              "UML offers a way to visualize a system's architectural blueprints in a diagram")),
                               elmo.distance(("UML offers a way to visualize a system's architectural blueprints in a diagram",
                                              "The Unified Modeling Language (UML) is a general-purpose, developmental, modeling language in the field of software engineering that is intended to provide a standard way to visualize the design of a system")), 1)
        self.assertAlmostEqual(
            elmo.distance(("In software engineering, a software design pattern is a general, reusable solution to a commonly occurring problem within a given context in software design.",
                           "Rather, it is a description or template for how to solve a problem that can be used in many different situations.")),
            elmo.distance(("Rather, it is a description or template for how to solve a problem that can be used in many different situations.",
                           "In software engineering, a software design pattern is a general, reusable solution to a commonly occurring problem within a given context in software design.")), 1)

