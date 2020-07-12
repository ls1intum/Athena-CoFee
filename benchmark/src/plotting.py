import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE

from benchmark.src.entities.text_block import TextBlock

tsne = TSNE(n_components=2, random_state=0)


def reduce_dimensions(vectors):
    return tsne.fit_transform(vectors)


def plot_embeddings(textblocks: [TextBlock], persist_labels=False):
    textblocks = [textblock for textblock in textblocks if int(textblock.cluster.id) >= -1]
    vectors = [textblock.embedding for textblock in textblocks]
    texts = [textblock.original_text for textblock in textblocks]
    clusters = [int(textblock.cluster.id) for textblock in textblocks]
    # clusters = [int(textblock.ground_truth_cluster) for textblock in textblocks]
    probabilities = [textblock.probability_in_cluster for textblock in textblocks]
    vectors = reduce_dimensions(vectors)

    color_palette = sns.color_palette('deep', max(clusters) + 1)
    cluster_colors = [color_palette[x] if x >= 0
                      else (0.5, 0.5, 0.5)
                      for x in clusters]
    cluster_member_colors = [sns.desaturate(x, p) for x, p in
                             zip(cluster_colors, probabilities)]

    x = vectors[:, 0]
    y = vectors[:, 1]
    labels = texts
    colors = cluster_member_colors

    norm = plt.Normalize(1, 4)
    fig, ax = plt.subplots()
    sc = plt.scatter(x, y, c=colors, s=100, norm=norm)
    # plt.xlim(-200, 250)
    # plt.xlim(-200, 250)

    if persist_labels :
        for i in range(len(x)):
            annotation = ax.annotate("", xy=(x[i], y[i]), xytext=(20, 20), textcoords="offset points",
                                     bbox=dict(boxstyle="round", fc="w"),
                                     arrowprops=dict(arrowstyle="->"))
            annotation.set_text(texts[i])
            annotation.get_bbox_patch().set_alpha(0.4)
            annotation.set_visible(True)
    else:
        annotation = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                                 bbox=dict(boxstyle="round", fc="w"),
                                 arrowprops=dict(arrowstyle="->"))
        annotation.set_visible(False)

        def update_annot(ind):
            pos = sc.get_offsets()[ind["ind"][0]]
            annotation.xy = pos
            text = "{}".format(" ".join([labels[n] for n in ind["ind"]]))
            annotation.set_text(text)
            annotation.get_bbox_patch().set_alpha(0.4)

        def hover(event):
            vis = annotation.get_visible()
            if event.inaxes == ax:
                cont, ind = sc.contains(event)
                if cont:
                    update_annot(ind)
                    annotation.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annotation.set_visible(False)
                        fig.canvas.draw_idle()
        fig.canvas.mpl_connect("motion_notify_event", hover)
