import matplotlib.pyplot as plt
import pandas as pd

from src.clustering import Clustering

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


# Gets the default blocks and vectors from the csv files.
def get_vectors():
    embedding_data = pd.read_csv('exampleEmbeddings/example_embeddings.csv')
    embeddings = embedding_data.values.tolist()
    sentence_data = pd.read_csv('exampleEmbeddings/example_sentences.csv')
    sentences = sentence_data.values.tolist()
    return sentences, embeddings


# Clustering and ELMo objects
clustering = Clustering()

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
