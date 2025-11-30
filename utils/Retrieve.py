from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import random


def get_html_undect(url, pause=2, max_scroll=10):

    driver = uc.Chrome(headless=False,use_subprocess=False)

    driver.get(url)
    time.sleep(1)
    driver.get(url)
    driver.save_screenshot("screen2.png")

    print(f"Scrapping: {url}")
    time.sleep(3)

    last_height = driver.execute_script("return document.body.scrollHeight")
    print(f"Scrapping {url}\n")
    for i in range (max_scroll):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)


        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        print(f"Scrolling...{i}/{max_scroll}")
        last_height = new_height
    print(f"Scapped {url}")
    html = driver.page_source
    driver.quit()

    return html


def get_html(html, pause = 2,  max = 10):
    chrome_opt = ChromeOptions()
    chrome_opt.add_argument('--no-sandbox')
    chrome_opt.add_argument('--headless=new')
    chrome_opt.add_argument('--disable-gpu')
    


    driver = webdriver.Chrome(options=chrome_opt)
    driver.get(html)
    time.sleep(2)
    driver.refresh()    
    time.sleep(2)
    driver.save_screenshot("screen.png")
    last_height = driver.execute_script("return document.body.scrollHeight")
    print(f"Scrapping {html}\n")
    time.sleep(10)
    print(f"Scapped {html}")
    full_html = driver.page_source
    print(full_html)
    try:
        driver.quit()
    except OSError:
        pass
    time.sleep(1)
    return full_html


def get_comment(html, comment_class, extract_class=None):
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
    return comments


