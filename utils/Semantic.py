from utils.Retrieve import get_html, get_comment, get_html_undect
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
import torch
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
from FlagEmbedding import BGEM3FlagModel


def predict_sentiment(texts):
    MODEL = r"tabularisai/multilingual-sentiment-analysis"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    inputs = tokenizer(
        texts, return_tensors="pt", truncation=True, padding=True, max_length=512
    )
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_map = {
        0: "Very Negative",
        1: "Negative",
        2: "Neutral",
        3: "Positive",
        4: "Very Positive",
    }
    return [sentiment_map[p] for p in torch.argmax(probabilities, dim=-1).tolist()]


def sematic_search(comments, querys, threshold=0.6):
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
    df_querys = []
    comment_encode_dict = {}
    count = 0
    for query in querys:
        print(f"Starting Classify {query}")
        df = pd.DataFrame(
            columns=["Topic", "Comment", "Confidence"],
        )
        query_encode = model.encode(
            query, return_dense=True, return_sparse=True, return_colbert_vecs=True
        )
        for comment in comments:
            if comment_encode_dict.get(comment) is None:
                if count % 100 == 0:
                    print("Encoding comment...")
                    count+=1
                comment_encode = model.encode(
                    comment,
                    return_dense=True,
                    return_sparse=True,
                    return_colbert_vecs=True,
                )
                comment_encode_dict[comment] = comment_encode
            else:
                comment_encode = comment_encode_dict[comment]

            similarity = model.colbert_score(
                query_encode["colbert_vecs"], comment_encode["colbert_vecs"]
            )
            try:
                sim_val = float(similarity)
            except Exception:
                if hasattr(similarity, "item"):
                    sim_val = float(similarity.item())
                else:
                    sim_val = float(np.array(similarity).astype(float).tolist()[0])
            if sim_val >= threshold:
                df.loc[len(df)] = [query, comment, sim_val]
        df_querys.append(df)
    return df_querys


def output_csv(df_querys):
    import re

    for idx, df in enumerate(df_querys):
        # determine a safe filename: prefer the Topic value if available, otherwise use the index
        if df is None or df.empty:
            safe_name = f"topic_{idx}"
        else:
            try:
                topic = str(df["Topic"].iloc[0])
            except Exception:
                topic = f"topic_{idx}"
            # sanitize topic to allow only common filename characters
            safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", topic).strip("_")
            if not safe_name:
                safe_name = f"topic_{idx}"
            # limit length to a reasonable size
            safe_name = safe_name[:100]
        file_name = f"data/{safe_name}.csv"
        df.to_csv(file_name, index=False)


def preprocess_comment_from_crawler(df, comment_column="Comment"):
    commments = df[comment_column].tolist()
    return commments


def semantic_analysis(
    urls,
    semantic_querys,
    option="Chrome",
    pause=2,
    max=10,
    comment_class="apphub_CardTextContent",
    extractclass="date_posted",
    k=10,
):
    topic_model = SentenceTransformer("sentence-transformers/stsb-xlm-r-multilingual")
    comments = []
    for url in urls:
        try:
            if option == "Chrome":
                html_content = get_html(url, pause=pause, max=max)
            elif option == "Edge":
                html_content = get_html_undect(url, pause=pause, max_scroll=max)
            else:
                html_content = ""
        except Exception as e:
            print(f"Error: {e}")
            html_content = ""
        comments += get_comment(html_content, comment_class, extractclass)

    print(
        "\n-------------------------------------------------------------------------\n\n"
    )
    if not comments:
        print("No comments found.")
        return
    else:
        comment_embed = topic_model.encode(comments, convert_to_tensor=False)
        comment_embed_np = np.array(comment_embed).astype("float32")

        comments_on_topic = {}
        for query in semantic_querys:
            list_comment = single_semantic(
                query=query,
                comments=comments,
                comment_embed_np=comment_embed_np,
                topic_model=topic_model,
                k_choose=k,
            )
            comments_on_topic[query] = list_comment
        return comments_on_topic


def single_semantic(
    query,
    comments,
    comment_embed_np,
    topic_model=SentenceTransformer("all-MiniLM-L6-v2"),
    k_choose=10,
):
    query_embed = topic_model.encode(query, convert_to_tensor=True)
    index = faiss.IndexFlatL2(comment_embed_np.shape[1])
    index.add(comment_embed_np)
    # ensure query embedding is a numpy float32 array shaped (1, dim)
    if hasattr(query_embed, "cpu"):
        q_np = query_embed.cpu().numpy()
    else:
        q_np = np.array(query_embed)
    q_np = q_np.astype("float32").reshape(1, -1)
    # choose k not greater than number of indexed vectors
    k = min(k_choose, comment_embed_np.shape[0])
    distances, indices = index.search(q_np, k)
    comments_list = []
    for i in range(k):
        idx = int(indices[0][i])
        comments_list.append(comments[idx])
    return comments_list
