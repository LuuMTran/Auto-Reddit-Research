from bertopic import BERTopic
import hdbscan
from sentence_transformers import SentenceTransformer
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer


def get_topic_probs(dfs, title):
    vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words="english")
    umap_model = UMAP(
        n_neighbors=5, n_components=8, min_dist=0.0, metric="cosine", random_state=42
    )
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    cluster_model = hdbscan.HDBSCAN(
        min_cluster_size=10, metric="euclidean", min_samples=5
    )
    topic_model = BERTopic(
        umap_model=umap_model,
        hdbscan_model=cluster_model,
        vectorizer_model=vectorizer_model,
        embedding_model=embedding_model,
    )

    results = []
    index = 0
    for df in dfs:
        docs = df["Comment"].astype(str).tolist()
        print(len(docs))
        topics, probs = topic_model.fit_transform(docs)
        print(len(topics))
        results.append((topics, probs))
        try:
            fig = topic_model.visualize_barchart(title=title[index])
            if fig is not None:
                fig.show()
        except Exception as e:
            print("Could not visualize barchart:", e)
        index += 1

    return results
