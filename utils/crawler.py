from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def get_comment1(html, comment_class="py-0 xs:mx-xs mx-2xs max-w-full scalable-text", topic_class=r"text-neutral-content-strong m-0 font-semibold text-18 xs:text-24  mb-xs px-md xs:px-0 xs:mb-md  overflow-hidden", extract_class=None):
    soup = BeautifulSoup(html or "", "html.parser")
    comment_parent = soup.find_all(class_ = comment_class)
    if not comment_parent:
        return []
    # remove any subelements matching extract_class before extracting text (only if provided)
    comments = []
    for parent in comment_parent:
        if extract_class:
            for elem in parent.find_all(class_ = extract_class):
                elem.decompose()
        comments.append(parent.get_text(strip=True))
    topic = soup.find("h1").text.strip()
    return topic, comments


def get_comment(driver, comment_selector="div.usertext-body div.md", topic_selector="div.top-matter p.title > a.title", extract_class=None):
    comment_list = []
    comments = driver.find_elements(
        By.CSS_SELECTOR,
        comment_selector
    )
    for c in comments:
        comment_list.append(c.text)
    title_element = driver.find_element(
        By.CSS_SELECTOR,
        "div.top-matter p.title > a.title"
    )
    topic = title_element.text
    return topic, comment_list



def store_comment (df, comments, topic):
    for comment in comments:
        df.loc[len(df)] = [topic, comment]
    print(f"Number of comments: {len(df)}")

    

def automatic_crawler(url, search_querys, first_n = 10, num_iter = 5):
    df = pd.DataFrame(columns=["Topic", "Comment"])
    driver = uc.Chrome(headless=False,use_subprocess=False, version_main=142)
    url_visit = set()
    def getpost(driver,url):
        driver.get(url)
        time.sleep(1)
        search_box = driver.find_element(By.CSS_SELECTOR, "input[name='q']")
        search_box.clear()
        search_box.send_keys(search_query)
        time.sleep(1)
        search_box.send_keys(Keys.ENTER)
        time.sleep(2)
        posts = driver.find_elements(
            By.CSS_SELECTOR,
            "div.listing.search-result-listing a.search-title.may-blank"
        )
        return posts
        
    for search_query in search_querys:
        posts = getpost(driver, url)
        while len(posts) == 0:
            driver.quit()
            driver = uc.Chrome(headless=False,use_subprocess=False, version_main=142)
            driver.get(url)
            posts = getpost(driver, url)
            
        
        href_list = []

        for p in posts:
            href = p.get_attribute("href")
            if href:
                href_list.append(href)
        href_list.pop(0)
        href_list.pop(0)
        href_list.pop(0)
        href_list = href_list[:first_n]
        for href in href_list:
            if href not in url_visit:
                driver.get(href)
                for i in range (num_iter):
                    try:
                        btns = driver.find_elements(By.CSS_SELECTOR, "span.morecomments > a.button")
                        btn = btns[-1]
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(2)
                    except:
                        print("No more 'load more comments' buttons.")
                        break
                source = driver.page_source
                try:
                    topic, comments = get_comment(driver)
                    store_comment(df=df, topic=topic,comments=comments)
                    url_visit.add(href)
                except:
                    print("Error")
            else:
                continue
    return df

