import os
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from review_analysis.preprocessing.base_processor import BaseDataProcessor
import re
import nltk
from nltk.corpus import stopwords 

class ImdbProcessor(BaseDataProcessor):
    """
    IMDB 리뷰 데이터를 전처리 및 피처 엔지니어링하는 클래스.
    """
    def __init__(self, input_path: str, output_dir: str):
        """
        클래스 초기화 메서드

        Args:
            input_path (str): 입력 파일 경로
            output_dir (str): 출력 디렉터리 경로
        """
        super().__init__(input_path, output_dir)
        self.data = None

    def preprocess(self):
        """
        데이터 전처리를 수행하는 메서드
        - 결측치 처리
        - 이상치 처리
        - 날짜 포맷 통일
        - 텍스트 데이터 전처리
        """
        # 데이터 로드
        self.data = pd.read_csv(self.input_path)

        # 결측치 처리
        self.data.dropna(subset=['star_rating', 'title', 'content', 'date'], inplace=True)

        # 이상치 처리
        self.data = self.data[(self.data['star_rating'] >= 1) & (self.data['star_rating'] <= 10)]  # 평점 범위 제한
        self.data = self.data[self.data['content'].str.len() > 5]  # 너무 짧은 리뷰 제거

        # 날짜 포맷 통일
        self.data['date'] = pd.to_datetime(self.data['date'], format='%b %d, %Y')

        # 텍스트 데이터 전처리
        self.data['content'] = self.data['content'].apply(self.preprocess_text)

    def preprocess_text(self, text):
        """
        리뷰 텍스트 데이터를 전처리하는 메서드
        - 소문자로 변환
        - 특수문자 제거
        - 불용어 제거

        Args:
            text (str): 전처리할 텍스트 데이터

        Returns:
            str: 전처리된 텍스트 데이터
        """
        # 텍스트 소문자 변환
        text = text.lower()

        # 알파벳 이외의 문자 제거 (공백과 단어는 유지)
        text = re.sub(r'[^a-z\s]', '', text)

        # NLTK 불용어 다운로드 (최초 실행 시)
        nltk.download('stopwords')
        
        # 영어 불용어 가져오기
        stop_words = set(stopwords.words('english'))
        
        # 사용자 정의 불용어 추가
        additional_stopwords = [
            "good", "bad", "awesome", "excellent", "horrible", "amazing", "worst", "best", "fine", "terrible", 
            "movie", "film", "acting", "director", "scene", "plot", "story", "character", "performance", "soundtrack",
            "love", "hate", "enjoy", "dislike", "recommend", "feel", "think", "watch", 
            "better", "worse", "more", "less", "similar", "well",
            "like", "as", "so", "too", "even", "just", "really", "great", 
            "parasite",
            "one",
            "action", "drama", "comedy", "genre", "moviegoer"
        ]

        stop_words.update(additional_stopwords)  # 추가된 불용어를 기본 불용어에 병합

        # 불용어 제거
        text = " ".join([word for word in text.split() if word not in stop_words])

        return text

    def feature_engineering(self):
        """
        피처 엔지니어링을 수행하는 메서드
        - 요일 정보를 새로운 컬럼으로 추가
        - TF-IDF 벡터화를 통해 텍스트 데이터를 수치 데이터로 변환
        """
        # 날짜로부터 요일 정보 추출 후 새로운 컬럼 추가
        self.data['day_of_week'] = self.data['date'].dt.day_name()

        # TF-IDF를 사용하여 텍스트 데이터 벡터화
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(self.data['content'])

        # TF-IDF 결과를 DataFrame으로 저장
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
        
        # TF-IDF 데이터를 원본 데이터와 병합 (데이터가 클 경우 별도로 저장 가능)
        self.data = pd.concat([self.data.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)

    def save_to_database(self):
        """
        전처리된 데이터를 CSV 파일로 저장하는 메서드
        """
        # 처리된 데이터를 CSV 파일로 저장
        output_file = os.path.join(self.output_dir, f'preprocessed_reviews_imdb.csv')
        self.data.to_csv(output_file, index=False)
        print(f"Processed data saved to {output_file}")