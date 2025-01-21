from review_analysis.crawling.base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os

class ImdbCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = "https://www.imdb.com/title/tt6751668/reviews/?ref_=tt_ururv_sm&spoilers=EXCLUDE"
        self.driver = None
        self.reviews = []

    def start_browser(self):
        """Start a visible Chrome browser."""
        self.logger.info("Starting the browser...")
        chrome_options = Options()
        # Do not use headless mode; browser window will be visible
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--start-maximized')  # Start browser maximized

        service = Service(ChromeDriverManager().install())  # Update with your actual ChromeDriver path
        self.browser = webdriver.Chrome(service=service, options=chrome_options)
        self.logger.info("Browser started successfully!")

    def scrape_reviews(self):
        """Scrape reviews by scrolling the page."""
        self.logger.info("Starting the scraping process...")
        self.start_browser()
        
        # Step 1: Open the base URL
        self.browser.get(self.base_url)
        self.logger.info(f"Opened URL: {self.base_url}")
        
        # Step 2: Click the "all" button to load all reviews
        try:
            all_button = self.browser.find_element(By.XPATH, "/html/body/div[2]/main/div/section/div/section/div/div[1]/section[1]/div[3]/div/span[2]/button")
            all_button.click()
            self.logger.info("Clicked the 'All Reviews' button.")
        except Exception as e:
            self.logger.error(f"Failed to find or click the 'All Reviews' button: {e}")
            self.browser.quit()
            return
        
        # Step 3: Scroll down to load all reviews
        self.logger.info("Scrolling to load all reviews...")
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load
            
            # Check if new content has been loaded
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  # If no more content is loaded
                self.logger.info("Reached the end of the page.")
                break
            last_height = new_height

        # Step 4: Find and extract review elements
        try:
            BOX_PATH = "/html/body/div[2]/main/div/section/div/section/div/div[1]/section[1]/article"
            review_elements = self.browser.find_elements(By.XPATH, BOX_PATH)#(By.CLASS_NAME, "sc-d59f276d-1 euAsTr user-review-item")
            self.logger.info(f"Found {len(review_elements)} reviews.")

            for i, review in enumerate(review_elements):

                try:
                    star_rating = review.find_element(By.XPATH, f"{BOX_PATH}[i+1]/div[1]/div[1]/div[1]/span/span[1]").text
                    content = review.find_element(By.CLASS_NAME, f"{BOX_PATH}[i+1]/div[1]/div[1]/div[3]/div/div/div").text
                    date = review.find_element(By.CLASS_NAME, f"{BOX_PATH}[i+1]/div[2]/ul/li[2]").text
                    
                    self.reviews.append({
                        "star_rating": star_rating,
                        "content": content,
                        "date": date
                    })
                except Exception as e:
                    self.logger.error(f"Failed to extract review data: {e}")
        except Exception as e:
            self.logger.error(f"Failed to find review elements: {e}")
        
        # Step 5: Quit the browser
        self.logger.info("Scraping completed. Quitting the browser.")
        self.browser.quit()

    def save_to_database(self):
        """Save the scraped reviews to a CSV file."""
        if not self.reviews:
            print("No reviews to save.")
            return

        output_path = os.path.join(self.output_dir, "reviews_imdb.csv")
        df = pd.DataFrame(self.reviews)
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"Reviews saved to {output_path}")
