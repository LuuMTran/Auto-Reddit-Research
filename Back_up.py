from utils.crawler import *
from utils.bertopic_analysis import *
from utils.Semantic import *
from utils.text_to_list import *

# Back-Up if running out of ram


if __name__ == "__main__":
    paths = get_file_names("./data")
    dfs = []
    filenames = []
    time.sleep(1)
    for path in paths:
        dfs.append(pd.read_csv(path))
        filename = os.path.basename(path)
        filenames.append(filename)
    result = get_topic_probs(dfs=dfs, title=filenames)
