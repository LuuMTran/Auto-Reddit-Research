from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import random
import pygame 
import sys
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


def create_app(driver,df):
    
    html_visit = set()
    pygame.init()
    WIDTH, HEIGHT = 500, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Capture comments")
    WHITE = (255, 255, 255)
    BLUE = (0, 102, 204)
    LIGHT_BLUE = (0, 153, 255)
    GREEN = (0, 200, 0)

    # Button settings
    button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 - 25, 150, 50)
    button_color = BLUE
    bg_color = WHITE

    # Font
    font = pygame.font.Font(None, 36)
    def draw_button(text, rect, color):
        pygame.draw.rect(screen, color, rect, border_radius=8)
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # df.to_csv("comment_data.csv", index=False)
                pygame.quit()
                return df
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if button_rect.collidepoint(event.pos):
                        bg_color = GREEN  # Change background color on click
                        source = driver.page_source
                        current_url = driver.current_url
                        if(current_url not in html_visit):
                            try:
                                topic, comments = get_comment1(source)
                                store_comment(df=df, topic=topic,comments=comments)
                                html_visit.add(current_url)
                            except:
                                print("Error")
                        else:
                            print("Page visited")

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if button_rect.collidepoint(event.pos):
                        bg_color = WHITE  # Reset background after release

        # Change button color on hover
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            button_color = LIGHT_BLUE
        else:
            button_color = BLUE

        # Draw everything
        screen.fill(bg_color)
        draw_button("Capture", button_rect, button_color)
        pygame.display.flip()

def store_comment (df, comments, topic):    
    for comment in comments:
        df.loc[len(df)] = [topic, comment]
    print(f"Number of comments: {len(df)}")

def crawler(url):
    driver = uc.Chrome(headless=False,use_subprocess=False)
    driver.get(url)
    time.sleep(1)
    driver.get(url)
    df = pd.DataFrame(columns=["Topic", "Comment"])
    return create_app(driver=driver, df= df)
    

def automatic_crawler(url, search_querys, first_n = 10, num_iter = 5):
    df = pd.DataFrame(columns=["Topic", "Comment"])
    driver = uc.Chrome(headless=False,use_subprocess=False)
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
            driver = uc.Chrome(headless=False,use_subprocess=False)
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

