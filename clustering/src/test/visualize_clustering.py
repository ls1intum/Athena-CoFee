import matplotlib.pyplot as plt
import pandas as pd

from src.clustering import Clustering
from src.elmo import ELMo
# A Script to change the parameters of HDBSCAN and visualize the resulting clusters


# A method to help print the cluster assignments
def print_clusters(block_array: [str], cluster_array: [int]):
    clusters = []
    for i in set(cluster_array):
        clusters.append([])
    for i in range(len(block_array)):
        clusters[cluster_array[i]+1].append(block_array[i])
    for i in range(len(clusters)):
        if i == 0:
            print('Blocks without a cluster (Assignment = -1):')
        else:
            print('Blocks in cluster ' + str(i) + ':')
        for block in clusters[i]:
            print(block)
        print()
    print('-' * 100)


# Gets text blocks from given csv file and computes the vectors.
# If no argument entered, returns the default blocks and vectors.
def get_vectors(file=''):
    # A part of the section 1.2.1 Modeling from the book "Object-Oriented Software Engineering
    # Using UML, Patterns, and Java Third Edition" by Bernd Bruegge & Allen H. Dutoit
    text = """    The purpose of science is to describe and understand complex systems, such as a system of atoms, a society of human beings, or a solar system.
    Traditionally, a distinction is made between natural sciences and social sciences to distinguish between two major types of systems.
    The purpose of natural sciences is to understand nature and its subsystems.
    Natural sciences include, for example, biology, chemistry, physics, and paleontology.
    The purpose of the social sciences is to understand human beings.
    Social sciences include psychology and sociology.
    There is another type of system that we call an artificial system.
    Examples of artificial systems include the space shuttle, airline reservation systems, and stock trading systems.
    Herbert Simon coined the term sciences of the artificial to describe the sciences that deal with artificial systems [Simon, 1970].
    Whereas natural and social sciences have been around for centuries, the sciences of the artificial are recent.
    Computer science, for example, the science of understanding computer systems, is a child of the twentieth century.
    Many methods that have been successfully applied in the natural sciences and humanities can be applied to the sciences of the artificial as well.
    By looking at the other sciences, we can learn quite a bit.
    One of the basic methods of science is modeling.
    A model is an abstract representation of a system that enables us to answer questions about the system.
    Models are useful when dealing with systems that are too large, too small, too complicated, or too expensive to experience firsthand.
    Models also allow us to visualize and understand systems that either no longer exist or that are only claimed to exist."""

    try:
        # If no argument was entered, use default values instead
        if file == '':
            raise FileNotFoundError
        data = pd.read_csv(file, usecols=[1], names=['block'], keep_default_na=False)
        sentences = data['block'].values.tolist()
        # Remove strings shorter than 3 characters
        sentences = list(filter(lambda x: len(x) > 2, sentences))
        embeddings = elmo.embed_sentences(sentences)
        return sentences, embeddings
    # If file is not found, use default values instead
    except FileNotFoundError:
        # Read default values to skip embedding computation
        try:
            embedding_data = pd.read_csv('exampleEmbeddings/example_embeddings.csv')
            embeddings = embedding_data.values.tolist()
            sentence_data = pd.read_csv('exampleEmbeddings/example_sentences.csv')
            sentences = sentence_data.values.tolist()
            return sentences, embeddings
        # If files not found, compute embeddings again
        except FileNotFoundError:
            sentences = text.split("\n")
            embeddings = elmo.embed_sentences(sentences)
            return sentences, embeddings


# Clustering and ELMo objects
clustering = Clustering()
elmo = ELMo()

# Get vector representations
(blocks, vectors) = get_vectors()

# Parameters of HDBSCAN can be changed here
clustering.clusterer.min_cluster_size = 3
clustering.clusterer.min_samples = 2
clusters = clustering.cluster(vectors)[0]

# Print clusters
print('Clusters: ')
print(clusters)
print()
print_clusters(blocks, clusters)

# Visualize the modified clustering
clustering.visualize_tree(vectors, True)
plt.show()

# Export the condensed tree to a csv file
tree = clustering.clusterer.condensed_tree_.to_pandas()
tree.to_csv('condensed_tree.csv', index=False)
