import matplotlib.pyplot as plt
import pandas as pd
from glob import glob
from os import getcwd
import statistics
from math import isinf
import json

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
            print('[BLOCK]: ' + block)
        print()
    print('#' * 100)


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
    path = getcwd() + '/exampleEmbeddings/dataset/textblock_exercise_submission_mapping.csv'
    all_mappings = pd.read_csv(path, usecols=[0, 2], keep_default_na=False)
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
    path = getcwd() + '/exampleEmbeddings/dataset/embeddings'
    embedding_files = glob(path + "/*.json")
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


# Takes a list of block ids and maps them to their actual text, by reading the mapping from csv
def map_id_to_text(ids: [str]):
    path = getcwd() + '/exampleEmbeddings/dataset/tb_id_text.csv'
    mapping_df = pd.read_csv(path, sep=';')
    mapping_list = mapping_df.values.tolist()
    mapping_dict = {}
    for elem in mapping_list:
        mapping_dict[elem[0]] = elem[1]
    texts = list(map(lambda x: mapping_dict[x], ids))
    return texts


# Reads previous clustering results and prints them for comparison
def print_old_clustering_results():
    old_clustering = 'clustering-2020-05-18_10_16_03.269799.json'
    path = getcwd() + '/exampleEmbeddings/dataset/clusterings/' + old_clustering
    df = pd.json_normalize(pd.read_json(path)['clusters'])
    old_cluster_list = df['blocks'].values.tolist()
    print('Old clustering results for the same data: ' + old_clustering)
    print('Number of clusters: {}'.format(len(old_cluster_list) - 1))
    print('Number of blocks without a cluster: {}'.format(len(old_cluster_list[0])))
    clustered_blocks = 0
    for x in old_cluster_list:
        clustered_blocks += len(x)
    clustered_blocks -= len(old_cluster_list[0])
    print('Number of blocks in clusters: {}'.format(clustered_blocks))
    print('-'*100)
    for i in range(len(old_cluster_list)):
        if i != 0:
            print('Number of blocks in cluster {}: {}'.format(i, len(old_cluster_list[i])))


# Finds clusters that share the parent cluster with the given one
def find_sibling_clusters(tree, cluster_id):
    # 6965 for the default setup
    parent = ((tree[tree.child == cluster_id])['parent'].values.tolist())[0]

    # [6968] for the default setup
    siblings = (tree[(tree.parent == parent) & (tree.child_size > 1)])['child'].values.tolist()
    siblings.remove(cluster_id)
    return siblings


# Finds clusters that share the cluster two levels above in the tree, with the given one
def find_cousin_clusters(tree, cluster_id):
    # 6965 for the default setup
    parent = ((tree[tree.child == cluster_id])['parent'].values.tolist())[0]

    # 6959 for the default setup
    grandparent = ((tree[tree.child == parent])['parent'].values.tolist())[0]

    # [6965, 6966] for the default setup
    aunts = (tree[(tree.parent == grandparent) & (tree.child_size > 1)])['child'].values.tolist()

    # [6968] for the default setup - same as the siblings here
    cousins = []
    for aunt in aunts:
        children = (tree[(tree.parent == aunt) & (tree.child_size > 1)])['child'].values.tolist()
        cousins.extend(children)
    cousins.remove(cluster_id)
    return cousins


# Exports clustering results in JSON format
def export_json_files(cluster_obj, labels, tree, exercise_id, vectors):
    data = {'labels': [], 'distances': [], 'tree': []}
    matrix = cluster_obj.distances_within_cluster(vectors=vectors)
    data['labels'] = [int(labels[i]) for i in range(len(labels))]

    # Following loop removes duplicates in matrix
    for i in range(len(matrix)):
        for j in range(i):
            matrix[i][j] = 0

    for row in matrix:
        data['distances'].append(list([float(row[i]) for i in range(len(row))]))
    for row in tree.values.tolist():
        if isinf(float(row[2])):
            row[2] = -1
        data['tree'].append({
            'parent': int(row[0]),
            'child': int(row[1]),
            'lambda_val': float(row[2]),
            'child_size': int(row[3])
        })
    with open("results_{}.json".format(exercise_id), 'w') as outfile:
        json.dump({'data': data}, outfile)


# Calculates statistical values for a given exercise
def calculate_statistics(exercise_id):
    tree = pd.read_csv('exampleEmbeddings/condensed_tree_{}.csv'.format(exercise_id))
    tree_list = tree.values.tolist()
    lambda_list = []
    for i in range(len(tree_list)):
        if i > 0:
            elem = tree_list[i]
            prev_elem = tree_list[i - 1]
            if not (elem[2] == prev_elem[2] and elem[0] == prev_elem[0]):
                if not isinf(elem[2]):
                    lambda_list.append(elem[2])
        else:
            lambda_list.append(tree_list[i][2])

    median = statistics.median(lambda_list)
    mean = statistics.mean(lambda_list)
    stdev = statistics.stdev(lambda_list)
    max_value = max(lambda_list)
    outlier_size = len(list(filter(lambda x: median * 2 < x <= max_value, lambda_list)))

    outliers_removed = list(filter(lambda x: x < median * 2, lambda_list))
    modified_mean = statistics.mean(outliers_removed)
    modified_stdev = statistics.stdev(outliers_removed)
    return {'median': median, 'modified_mean': modified_mean, 'modified_stdev': modified_stdev}


# Calculates the lambda threshold for the tree traversal
def compute_lambda_threshold():
    # exercise_id:  1211 - 1212  - 1213  - 1214
    # blocks:       5918 - 10324 - 10374 - 6972
    stats_1211 = calculate_statistics(1211)
    stats_1212 = calculate_statistics(1212)
    stats_1213 = calculate_statistics(1213)
    stats_1214 = calculate_statistics(1214)

    median = statistics.mean([stats_1211['median'], stats_1212['median'], stats_1213['median'], stats_1214['median']])
    modified_mean = statistics.mean([stats_1211['modified_mean'], stats_1212['modified_mean'],
                                     stats_1213['modified_mean'], stats_1214['modified_mean']])
    modified_stdev = statistics.mean([stats_1211['modified_stdev'], stats_1212['modified_stdev'],
                                      stats_1213['modified_stdev'], stats_1214['modified_stdev']])

    print('Median:                          {}'.format(median))
    print('Modified standard deviation:     {}'.format(modified_stdev))
    print('Modified mean:                   {}'.format(modified_mean))
    print('Threshold (1 / modified mean):   {}'.format(1 / modified_mean))
    print('2 * threshold:                   {}'.format(2 * (1 / modified_mean)))
    print('3 * threshold:                   {}'.format(3 * (1 / modified_mean)))
    print('"Modified" = outlier points in (median * 2, Infinity) removed')

# Performs the analysis. Optional flags can be set for additional behaviour:
#   - visualise: Plots the condensed tree of the clustering
#   - print_old_results: Prints the old clustering results for the same data set
#   - export_condensed_tree: Saves the condensed tree to a csv file
#   - export_json: Saves the labels, tree and distance matrix to JSON
def perform_analysis(exercise_id, cluster_obj, visualise=False, print_old_results=False, export_condensed_tree=False,
                     export_json=False):
    embeddings = get_embeddings_for_exercise(exercise_id)
    (block_ids, vectors) = map(list, zip(*embeddings))
    blocks = map_id_to_text(block_ids)
    clusters = cluster_obj.cluster(vectors)[0]

    print('Number of clusters: {}'.format(len(set(clusters)) - 1))
    no_noise = filter(lambda x: x != -1, clusters)
    # Cluster 522 has the most points with the default setup.
    biggest_cluster = statistics.mode(no_noise)
    biggest_cluster_size = len(list(filter(lambda x: x == biggest_cluster, clusters)))
    print('Biggest cluster is {} with size {}.'.format(biggest_cluster, biggest_cluster_size))

    tree = cluster_obj.clusterer.condensed_tree_.to_pandas()
    labels = cluster_obj.clusterer.labels_
    # Tree id of the biggest cluster is 6967 for the default setup
    current_cluster = cluster_obj.label_to_tree_id(biggest_cluster)
    merge_candidates = find_sibling_clusters(tree=tree, cluster_id=current_cluster)
    print(merge_candidates)

    print_clusters(blocks, clusters)

    if print_old_results:
        print_old_clustering_results()

    if visualise:
        clustering.clusterer.condensed_tree_.plot(select_clusters=True)
        plt.show()

    if export_condensed_tree:
        tree.to_csv('condensed_tree_{}.csv'.format(exercise_id), index=False)

    if export_json:
        export_json_files(cluster_obj=cluster_obj, labels=labels, tree=tree, exercise_id=exercise_id, vectors=vectors)


# Parameters of HDBSCAN can be changed here
clustering = Clustering()
clustering.clusterer.min_cluster_size = 2
clustering.clusterer.min_samples = 2

compute_lambda_threshold()
perform_analysis(exercise_id=1211, cluster_obj=clustering)

