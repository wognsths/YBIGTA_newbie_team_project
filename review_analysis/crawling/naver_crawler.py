from bs4 import BeautifulSoup

from review_analysis.crawling.base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import pandas as pd

import time

class NaverCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bkEw&pkid=68&os=5664043&qvt=0&query=%EC%98%81%ED%99%94%20%EA%B8%B0%EC%83%9D%EC%B6%A9%20%EA%B4%80%EB%9E%8C%ED%8F%89'
        

        self.review_combinations = [
            ("viewer", "like"),
            ("viewer", "latest"),
            ("netizen", "like"),
            ("netizen", "latest")
        ]

        self.start_browser()

    def start_browser(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("excludeSwitches",["enable-logging"])

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(2)

        try:
            self.driver.maximize_window()
        except:
            pass

    def scrape_reviews(self):
        all_reviews_result = []

        for review_type, sort_type in self.review_combinations:
            print("==========================================================")
            print(f"[{review_type.upper()} / {sort_type.upper()}] 크롤링 시작")
            print("==========================================================")

            if review_type == "viewer" and sort_type == "like":
                self.driver.get(self.base_url)
                self.driver.implicitly_wait(2)
                time.sleep(1)

                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[2]/div[2]/button').click() # 스포일러 방지 버튼 
                except Exception as e:
                    print(f"[ERROR] Failed to click spoiler include button: {e}")

                scrollable_div = self.driver.find_element(
                    By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[4]'
                )
            elif review_type == "viewer" and sort_type == "latest":
                self.driver.get(self.base_url)
                self.driver.implicitly_wait(2)
                time.sleep(1)

                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[2]/div[1]/div/ul/li[2]/a/span').click() # 최신순 버튼
                    time.sleep(1)
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[2]/div[2]/button').click() # 스포일러 방지 버튼 
                except Exception as e:
                    print(f"[ERROR] Failed to click buttons: {e}")
                scrollable_div = self.driver.find_element(
                    By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[4]'
                )
            elif review_type == "netizen" and sort_type == "like":
                self.driver.get(self.base_url)
                self.driver.implicitly_wait(2)
                time.sleep(1)

                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[1]/div/div/ul/li[2]/a/span').click() # 네티즌 버튼
                    time.sleep(1)
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[5]/div[2]/div[2]/button').click() # 스포일러 방지 버튼
                except Exception as e:
                    print(f"[ERROR] Failed to click buttons: {e}")
                scrollable_div = self.driver.find_element(
                    By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[5]/div[4]'
                )
            elif review_type == "netizen" and sort_type == "latest":
                self.driver.get(self.base_url)
                self.driver.implicitly_wait(2)
                time.sleep(1)

                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[1]/div/div/ul/li[2]/a/span').click() # 네티즌 버튼
                    time.sleep(1)
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[5]/div[2]/div[1]/div/ul/li[2]/a/span').click() # 최신순 버튼
                    time.sleep(1)
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[5]/div[2]/div[2]/button').click() # 스포일러 방지 버튼
                except Exception as e:
                    print(f"[ERROR] Failed to click buttons: {e}")
                scrollable_div = self.driver.find_element(
                    By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[5]/div[4]'
                )
            
            time.sleep(2)

            prev_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

            time.sleep(2)
            while True:
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scrollable_div)
                time.sleep(2)
                curr_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                if curr_height == prev_height:
                    break
                prev_height = curr_height

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            data_rows = soup.find_all("li", class_="area_card _item")

            print(f"총 {len(data_rows)}개의 리뷰 발견")

            combo_reviews = []
            for row in data_rows:
                date_tag = row.find("dd", class_="this_text_normal")
                writing_date = date_tag.text.strip() if date_tag else "N/A"

                comment_tag = row.find("span", class_="desc _text")
                comment = comment_tag.text.strip() if comment_tag else "N/A"

                vote_tags = row.find_all("span", class_="this_text_number _count_num")
                upvote = vote_tags[0].text.strip() if len(vote_tags) > 0 else "0"
                downvote = vote_tags[1].text.strip() if len(vote_tags) > 1 else "0"

                star_rating_tag = row.find("div", class_="area_text_box")
                star_rating = star_rating_tag.text.strip() if star_rating_tag else "N/A"

                combo_reviews.append({
                    "review_type": review_type,
                    "sort_type": sort_type,
                    "writing_date": writing_date,
                    "star_rating": star_rating,
                    "comment": comment,
                    "upvote": upvote,
                    "downvote": downvote
                })

            all_reviews_result.extend(combo_reviews)

        print("\n\n===== 4가지 케이스 크롤링 완료 =====")
        print(f"총 리뷰 수: {len(all_reviews_result)}")

        self.df = pd.DataFrame(all_reviews_result)

    def save_to_database(self):
        self.df = self.df.drop_duplicates(subset = ["comment"])
        self.df.to_csv(".\\database\\Movie.csv", index = False)
        print(f"중복 제거 후 총 리뷰 수: {self.df.shape[0]}")
