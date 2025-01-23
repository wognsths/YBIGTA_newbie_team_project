from review_analysis.crawling.base_crawler import BaseCrawler
from review_analysis.crawling.utils.logger import setup_logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from typing import Dict, List
import pandas as pd
import time
import os
import sys

class ImdbCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        """
        IMDB 리뷰 크롤러 클래스 초기화

        Args:
            output_dir (str): 크롤링한 데이터를 저장할 디렉토리 경로
        """
        super().__init__(output_dir)
        self.base_url = "https://www.imdb.com/title/tt6751668/reviews/?ref_=tt_ururv_sm&spoilers=EXCLUDE&sort=user_rating%2Cdesc"
        self.driver = None
        self.reviews: List[Dict[str, str]] = []
        self.logger = setup_logger(log_file='./utils/imdb.log')  # Logger 설정

    def start_browser(self):
        """
        크롬 브라우저를 실행하는 함수
        """
        self.logger.info("브라우저를 실행합니다…")
        chrome_options = Options()
        chrome_options.add_argument('—disable-blink-features=AutomationControlled')
        chrome_options.add_argument('—start-maximized')  # 브라우저 최대화로 시작

        service = Service(ChromeDriverManager().install())  # ChromeDriver 설치 및 서비스 실행
        self.browser = webdriver.Chrome(service=service, options=chrome_options)
        self.logger.info("브라우저 실행 성공!")

    def scrape_reviews(self):
        """
        IMDB 리뷰를 크롤링하는 함수
        """
        self.logger.info("크롤링 프로세스를 시작합니다…")
        self.start_browser()

        # Step 1: 기본 URL 열기
        self.browser.get(self.base_url)
        self.logger.info(f"URL 열기 성공: {self.base_url}")
        time.sleep(3)

        # Step 2: 'All Reviews' 버튼 클릭
        try:
            all_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/main/div/section/div/section/div/div[1]/section[1]/div[3]/div/span[2]/button')
            all_button.send_keys(Keys.ENTER)
            self.logger.info("'All Reviews' 버튼 클릭 성공.")
        except Exception as e:
            self.logger.error(f"'All Reviews' 버튼 클릭 실패: {e}")
            return

        # Step 3: 스크롤 다운하여 모든 리뷰 로드
        self.logger.info("스크롤 다운하여 리뷰를 로드합니다…")
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        while True:
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 콘텐츠 로드를 기다림

            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  # 더 이상 콘텐츠가 로드되지 않음
                self.logger.info("페이지 끝에 도달했습니다.")
                break
            last_height = new_height

        # Step 4: 리뷰 요소 추출 및 데이터 수집
        try:
            BOX_PATH = "/html/body/div[2]/main/div/section/div/section/div/div[1]/section[1]/article"
            review_elements = self.browser.find_elements(By.XPATH, '//article[@class="sc-d59f276d-1 euAsTr user-review-item"]')
            self.logger.info(f"총 {len(review_elements)}개의 리뷰를 찾았습니다.")

            for i, review in enumerate(review_elements):
                try:
                    star_rating = review.find_element(By.XPATH, f"{BOX_PATH}[{i+1}]/div[1]/div[1]/div[1]/span/span[1]").text
                    title = review.find_element(By.XPATH, f"{BOX_PATH}[{i+1}]/div[1]/div[1]/div[2]/div/a/h3").text
                    content = review.find_element(By.XPATH, f"{BOX_PATH}[{i+1}]/div[1]/div[1]/div[3]/div/div/div").text
                    date = review.find_element(By.XPATH, f"{BOX_PATH}[{i+1}]/div[2]/ul/li[2]").text

                    self.reviews.append({
                        "star_rating": star_rating,
                        "title": title,
                        "content": content,
                        "date": date
                    })
                except Exception as e:
                    self.logger.error(f"리뷰 데이터를 추출하지 못했습니다: {e}")
        except Exception as e:
            self.logger.error(f"리뷰 요소를 찾지 못했습니다: {e}")

        # Step 5: 브라우저 종료
        self.logger.info("크롤링 완료. 브라우저를 종료합니다.")
        self.browser.quit()

    def save_to_database(self):
        """
        크롤링한 리뷰 데이터를 CSV 파일로 저장
        """
        if not self.reviews:
            print("저장할 리뷰가 없습니다.")
            return

        output_path = os.path.join(self.output_dir, "reviews_imdb.csv")
        df = pd.DataFrame(self.reviews)
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"리뷰 데이터를 {output_path}에 저장했습니다.")
