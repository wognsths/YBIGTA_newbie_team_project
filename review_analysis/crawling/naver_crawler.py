from bs4 import BeautifulSoup


from review_analysis.crawling.utils.logger import setup_logger
from review_analysis.crawling.base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import pandas as pd

import time
import os


class NaverCrawler(BaseCrawler):
    '''
    네이버 영화 리뷰 크롤러

    기능
    - 네이버 검색을 통해 특정 영화 리뷰를 크롤링
    - 실관람객(viewer) / 네티즌(netizen) 리뷰 수집
    - 추천순(like) / 최신순(latest) 정렬 기준 적용 가능
    - 스크롤을 내려 모든 리뷰를 로드한 후 HTML을 파싱하여 데이터 추출
    - 크롤링한 데이터를 중복 제거 후 CSV로 저장
    '''
    def __init__(self, output_dir: str):
        '''
        NaverCrawler의 초기화 메서드

        Args:
        - output_dir (str): 크롤링한 데이터를 저장할 디렉토리

        Attributes:
        - base_url (str): 네이버 영화 리뷰 페이지 URL
        - logger (Logger): 크롤링 로그 기록을 위한 Logger 객체
        '''
        super().__init__(output_dir)
        self.base_url = 'https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bkEw&pkid=68&os=5664043&qvt=0&query=%EC%98%81%ED%99%94%20%EA%B8%B0%EC%83%9D%EC%B6%A9%20%EA%B4%80%EB%9E%8C%ED%8F%89'

        self.logger = setup_logger(log_file='review_analysis/crawling/utils/imdb.log')


        # 크롤링할 리뷰 유형과 정렬 기준 조합
        self.review_combinations = [
            ("viewer", "like"),
            ("viewer", "latest"),
            ("netizen", "like"),
            ("netizen", "latest")
        ]

        self.start_browser()

    def start_browser(self):

        '''크롬 브라우저 실행 및 네이버 영화 페이지 로드'''

        self.logger.info("Starting the browser...")
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

        self.logger.info("Browser started successfully!")

    def scrape_reviews(self):
        '''
        Args
        - 크롤링 대상: 실관람객(viewer) / 네티즌(netizen) 리뷰
        - 정렬: 추천 순(like) / 최신 순(latest)
        - 데이터: 작성일, 별점, 댓글, 추천/비추천 수

        Description
        - 페이지를 불러오고 필수 버튼을 클릭한 후, 스크롤을 내려 모든 리뷰를 로드
          BeautifulSoup으로 HTML을 파싱하여 데이터를 추출
        '''
        
        all_reviews_result = []

        for review_type, sort_type in self.review_combinations:
            self.logger.info("==========================================================")
            self.logger.info(f"[{review_type.upper()} / {sort_type.upper()}] 크롤링 시작")
            self.logger.info("==========================================================")



            if review_type == "viewer" and sort_type == "like":
                self.driver.get(self.base_url)
                self.driver.implicitly_wait(2)
                time.sleep(1)

                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[2]/div[2]/button').click() # 스포일러 방지 버튼 
                except Exception as e:

                    self.logger.info(f"[ERROR] Failed to click spoiler include button: {e}")

                scrollable_div = self.driver.find_element(
                    By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[4]'
                )
            elif review_type == "viewer" and sort_type == "latest":
                self.driver.get(self.base_url)
                self.driver.implicitly_wait(2)
                time.sleep(1)

                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[2]/div[1]/div/ul/li[2]/a/span').click() # 최신순 버튼

                    time.sleep(2)
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[2]/div[2]/button').click() # 스포일러 방지 버튼 
                except Exception as e:
                    self.logger.info(f"[ERROR] Failed to click buttons: {e}")

                scrollable_div = self.driver.find_element(
                    By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[4]/div[4]'
                )
            elif review_type == "netizen" and sort_type == "like":
                self.driver.get(self.base_url)
                self.driver.implicitly_wait(2)
                time.sleep(1)

                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[1]/div/div/ul/li[2]/a/span').click() # 네티즌 버튼

                    time.sleep(2)
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[5]/div[2]/div[2]/button').click() # 스포일러 방지 버튼
                except Exception as e:
                    self.logger.info(f"[ERROR] Failed to click buttons: {e}")

                scrollable_div = self.driver.find_element(
                    By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[5]/div[4]'
                )
            elif review_type == "netizen" and sort_type == "latest":
                self.driver.get(self.base_url)
                self.driver.implicitly_wait(2)
                time.sleep(1)

                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[1]/div/div/ul/li[2]/a/span').click() # 네티즌 버튼

                    time.sleep(2)
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[5]/div[2]/div[1]/div/ul/li[2]/a/span').click() # 최신순 버튼
                    time.sleep(2)
                    self.driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[3]/div[2]/div/div/div[5]/div[2]/div[2]/button').click() # 스포일러 방지 버튼
                except Exception as e:
                    self.logger.info(f"[ERROR] Failed to click buttons: {e}")

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

            # BeautifulSoup으로 페이지 HTML 파싱
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            data_rows = soup.find_all("li", class_="area_card _item")

            self.logger.info(f"총 {len(data_rows)}개의 리뷰 발견")


            # 리뷰 데이터 추출

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

        self.logger.info("\n\n===== 4가지 케이스 크롤링 완료 =====")
        self.logger.info(f"총 리뷰 수: {len(all_reviews_result)}")

        print("\n\n===== 4가지 케이스 크롤링 완료 =====")
        print(f"총 리뷰 수: {len(all_reviews_result)}")


        self.df = pd.DataFrame(all_reviews_result)

    def save_to_database(self):
        '''중복되는 데이터 제거 후 csv 저장'''

        output_path = os.path.join(self.output_dir, "reviews_naver.csv")
        self.df = self.df.drop_duplicates(subset = ["comment"])
        self.df.to_csv(output_path, index = False, encoding="utf-8-sig")
        self.logger.info(f"중복 제거 후 총 리뷰 수: {self.df.shape[0]}")
        self.logger.info(f"리뷰가 다음 경로에 저장되었습니다.: {output_path}")

