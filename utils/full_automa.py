from utils.crawler import *
from utils.bertopic_analysis import *
from utils.Semantic import *
from utils.text_to_list import *
import pandas as pd
import time
import os

def split_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]
def full_pipeline_start(n = 5):
    querys = read_txt_to_list(r"config/querys.txt")
    search_querys = read_txt_to_list(r"config/searchquery.txt")
    df = automatic_crawler(r"https://old.reddit.com", search_querys= search_querys)
    df.to_csv(r"./checkpoints/comment_data.csv", header=False)
    comments = preprocess_comment_from_crawler(df)
    output_csv(sematic_search(querys=querys,comments=comments))
    paths = get_file_names("./data")
    for path in paths:
        df = pd.read_csv(path)
        print(len(df))
    dfs = []
    filenames = []
    time.sleep(1)
    for path in paths:
        dfs.append(pd.read_csv(path))
        filename = os.path.basename(path)
        filenames.append(filename)
    result = get_topic_probs(dfs=dfs)

def multithread_crawler(url, query, out_queue):
    df_ = automatic_crawler(url=url, search_querys=query)
    out_queue.put(df_)   # return df through queue