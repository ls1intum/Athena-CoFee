import matplotlib.pyplot as plt
import pandas as pd
import glob
import os

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
            print('{} blocks without a cluster (Assignment = -1):'.format(len(clusters[i])))
        else:
            print('{} blocks in cluster {}:'.format(len(clusters[i]), i))
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


# Reads the exercise_id - textblock_id mappings from csv file.
# Returns a dictionary per default. If return_dict is set to false, returns a list of grouped up text blocks.
def read_mappings_from_csv(return_dict=True):
    all_mappings = pd.read_csv('exampleEmbeddings/dataset/textblock_exercise_submission_mapping.csv',
                          usecols=[0, 2], keep_default_na=False)
    if return_dict:
        mapping_list = list(filter(lambda x: x[1] != 'NULL', all_mappings.values.tolist()))
        mapping_dict = {}
        for (exercise, block) in mapping_list:
            mapping_dict[block] = exercise
        return mapping_dict
    else:
        exercises_set = set(all_mappings['exercise_id'].values.tolist())
        # List containing text blocks grouped by exercise. Elements: (exercise_id, [blocks])
        textblocks_by_exercise = []
        for exercise_id in exercises_set:
            id_filter = all_mappings['exercise_id'] == exercise_id
            exercise_mappings = all_mappings[id_filter]
            # Extract text blocks and remove NULL strings
            textblocks = list(filter(lambda x: x != 'NULL', exercise_mappings['textblock_id'].values.tolist()))
            textblocks_by_exercise.append((exercise_id, textblocks))
        return textblocks_by_exercise


# Reads all json embedding files and concatenates them to a list of tuples (textblock_id, vector)
def concat_embeddings_from_json():
    path = os.getcwd() + '/exampleEmbeddings/dataset/embeddings'
    embedding_files = glob.glob(path + "/*.json")
    all_embeddings = pd.concat((pd.json_normalize(pd.read_json(file)['embeddings']) for file in embedding_files))
    return all_embeddings.values.tolist()


# Returns the embeddings for given exercise_id. If id not given or invalid, returns embeddings for first exercise read.
def get_embeddings_for_exercise(exercise_id=-1):
    mapping_dict = read_mappings_from_csv()
    all_embeddings = concat_embeddings_from_json()
    if exercise_id == -1 or exercise_id not in set(mapping_dict.values()):
        exercise_id = list(mapping_dict.values())[0]
    filtered_embeddings = []
    for emb in all_embeddings:
        if mapping_dict[emb[0]] == exercise_id:
            filtered_embeddings.append(emb)
    # print(len(filtered_embeddings)) returns for given id:
    # id:  1211 - 1212  - 1213  - 1214
    # len: 5918 - 10324 - 10374 - 6972
    return filtered_embeddings


# Clustering and ELMo objects
clustering = Clustering()

# Get vector representations
embeddings = get_embeddings_for_exercise(1211)
(block_ids, vectors) = map(list, zip(*embeddings))
# embeddings = concat_embeddings_from_json()

# Parameters of HDBSCAN can be changed here
clustering.clusterer.min_cluster_size = 2
clustering.clusterer.min_samples = 2
clusters = clustering.cluster(vectors)[0]

# Print clusters
print('Number of clusters: {}'.format(len(set(clusters)) - 1))
print()
print_clusters(block_ids, clusters)

"""
clustering.visualize_tree(vectors, True)
plt.show()

# Export the condensed tree to a csv file
tree = clustering.clusterer.condensed_tree_.to_pandas()
tree.to_csv('condensed_tree.csv', index=False)
"""
