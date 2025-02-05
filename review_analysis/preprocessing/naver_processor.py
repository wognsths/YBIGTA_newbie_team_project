from review_analysis.preprocessing.base_processor import BaseDataProcessor
import pandas as pd
import numpy as np
import re

from tqdm import tqdm
# from sentence_transformers import SentenceTransformer, util
import datetime

# from sklearn.metrics.pairwise import cosine_similarity

import os

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class NaverProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        if input_path != "": 
            self.df = pd.read_csv(input_path)
        self.embeddings = []

    def preprocess(self):
        '''
        데이터 전처리 함수
            리뷰 데이터셋을 전처리하여 모델 학습 및 분석에 적합한 형식으로 변환

        주요 처리 과정:
            1. 별점(star_rating) 전처리:
            - 문자열에서 숫자만 추출하여 정수형(int)으로 변환

            2. 작성일자(writing_date) 전처리:
            - 날짜 데이터를 datetime 형식으로 변환한 후, 날짜(date) 추출

            3. 텍스트(comment) 전처리:
            - 리뷰 텍스트에서 불필요한 특수문자를 제거
            - 관람 등급(15세, 19세) 등의 숫자 데이터는 유의미하다고 판단하여 유지

            4. 결측치(null) 처리:
            - 빈 문자열("")을 NaN 값으로 변환한 후, NaN 값을 포함하는 행을 제거

            5. 이상치(outlier) 처리:
            - 리뷰 글자 수가 평균 + (2.5 * 표준편차)를 초과하는 경우 이상치로 간주
            - 긴 리뷰의 경우, 가장 긴 문장만 남김김

        출력:
            - 전처리된 데이터프레임(self.df)
        '''

        # 별점 전처리: 문자열에서 숫자만 추출 후 정수형 변환
        self.df["star_rating"] = self.df["star_rating"].apply(lambda x: int(x[12:]))

        # 작성일자 전처리: 날짜형 테이터 변환
        self.df['writing_date'] = pd.to_datetime(self.df['writing_date']).dt.date

        # 텍스트 데이터 전처리: 불용어 제거, 숫자 데이터는 관람 등급(15세, 19세) 등의 언급이 많아 보존
        self.df['comment'] = self.df['comment'].str.replace(r"[^0-9ㄱ-ㅎㅏ-ㅣ가-힣 ]", "", regex=True)

        # 결측치 처리: null값 제거
        before = self.df.shape[0]
        self.df.replace({'comment': {'': np.nan}}, inplace=True)
        self.df.dropna(inplace=True)
        after = self.df.shape[0]

        print(f"결측치 처리 후 데이터: {before} => {after}")

        # 이상치 처리: 리뷰 글자 수가 지나치게 긴 경우 가장 긴 문장으로 한정
        review_length = self.df["comment"].apply(lambda x: len(x))
        outlier_length = review_length.mean() + 2.5 * review_length.std()

        def get_longest_sentence(text):
            # 텍스트에서 가장 긴 문장 추출
            if pd.isna(text):
                return text
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            longest_sentence = max(sentences, key=len, default="")  
            
            return longest_sentence
        
        self.df["comment"] = self.df["comment"].apply(lambda x: get_longest_sentence(x) if len(str(x)) > outlier_length else x)

    def feature_engineering(self):
        '''
        파생 변수 생성: 날짜에 대한 요일 값

        리뷰 데이터에 대한 Feature Engineering 수행
            리뷰 데이터를 임베딩하여 벡터화하고, 특정 키워드(카테고리)에 대한 유사도를 계산하여
            각 리뷰가 어느 카테고리에 가까운지를 판별함

        주요 과정:
            2. 학습된 Sentence Transformer 모델을 사용하여 리뷰 데이터를 임베딩(512차원 벡터)으로 변환
            3. 사전 정의된 카테고리(예: Masterpiece, Social Commentary 등)와 관련된 문장을 벡터화
            4. 각 리뷰와 카테고리 벡터 간 코사인 유사도를 계산하여 해당 리뷰가 어느 카테고리에 속하는지 분석
            5. 최종적으로 임베딩 벡터(512차원) 및 카테고리별 유사도를 원본 데이터프레임(self.df)에 추가

        출력:
            - 원본 데이터(self.df)에 512차원 리뷰 임베딩 및 카테고리별 유사도 점수 추가
        '''
        # 요일 값 변수 추가
        self.df["weekday"] = pd.to_datetime(self.df["writing_date"]).apply(lambda x: x.weekday())

        # Sentence Transformer 모델 로드
        model_name = 'sentence-transformers/distiluse-base-multilingual-cased-v2'
        model = SentenceTransformer(model_name)

        batch_size = 8
        reviews = self.df["comment"].tolist()

        # 리뷰 데이터 임베딩 벡터화 (512차원)   
        all_embeddings = []
        print("텍스트 임베딩 진행 중...")
        for i in tqdm(range(0, len(reviews), batch_size)):
            batch = reviews[i:i + batch_size]
            batch_embeddings = model.encode(batch, convert_to_numpy=True)
            all_embeddings.append(batch_embeddings)

            self.embeddings = np.vstack(all_embeddings)

         # 512차원 벡터를 데이터프레임으로 변환 (열 이름: x0 ~ x511)
        df_embeddings = pd.DataFrame(self.embeddings, columns=[f"x{i}" for i in range(512)])

        # 카테고리별 대표 문장 정의
        Masterpiece = np.array([
            "완벽 또 완벽 어느 곳에서 바라보아도 완벽하다",
            "그 해 최고의 영화였다",
            "작품은 한국 영화 역대 세손가락 안에 들정도로 모든게 좋았다",
            "Masterpiece! One of the greatest films ever.",
            "A cinematic marvel with outstanding storytelling.",
        ])

        Social_commentary = np.array([
            "이야기가 너무나도 현실적이어서 깊게 쓰라리다",
            "한국에 서민들이라면 나또는 친구 지인들이 반지하서 사는분들이 꼭한분이 있었다 그래서 더 몰입되었고 충격이었다",
            "한국 계층사회의 수직성과 단절성을 신랄하게 표현해낸 한국영화",
            "가난한 집과 부유한 집의 차이와 인간이 무언가를 갖고 싶어하는 욕망이 비춰지면서 현대사회의 부정적인 현상이 잘 드러났다",
            "The film brilliantly highlights social inequality.",
            "A deep metaphorical take on capitalism.",
            "focusing on society and it's negative aspects. This movie kept me awake for many hours at night and will always remind me of so many things like to be thankful for what you have and how to approach others",
            "It shows not only a society problem but also a suggestion of solution."
        ])

        Suspense_Thrill = np.array([
            "너무 재밌음 또 봐도 처음 봤을 때 그 스릴 긴장감 그대로 느껴짐",
            "Thrilling scenes there were",
            "And slowly it turns into a intense thriller",
        ])

        Overrated = np.array([
            "해외에서 상받고 사회고발적인거 때문에 과평가된 느낌",
            "이게 왜 오스카를 받았는지 모르겠다",
            "it's extremely overrated",
            "It was an OK movie. I don't understand how you can give an Oscar to a movie that's just kind of meh"
        ])

        Uncomfortable = np.array([
            "아 온가족이 같이 보는 영화에 배드신은 좀 찍지 마라",
            "보는 내내 불쾌한 영화",
            "후반부는 너무 징그럽고 끔직함 이걸 왜 15세로 해뒀는지 모르겠는 영화",
            "영화 등급 잘못나온듯 청소년이 보기에 적절하지 않습니다",
            "Very violent for no reason",
            "I felt a little bored in parts and I felt uncomfortable."
        ])

        Acting_performance = np.array([
            "이정은 조여정 배우들의 연기또한 훌륭했다",
            "연기파 배우들 역시",
            "wonderful acting by the whole team members."  
        ])
        
        # 카테고리 문장들을 임베딩 벡터로 변환
        def compute_embedding(sentences):
            embeddings = model.encode(sentences)
            return embeddings

        masterpiece_embedding = compute_embedding(Masterpiece)
        social_commentary_embedding = compute_embedding(Social_commentary)
        suspense_thrill_embedding = compute_embedding(Suspense_Thrill)
        overrated_embedding = compute_embedding(Overrated)
        uncomfortable_embedding = compute_embedding(Uncomfortable)
        acting_performance_embedding = compute_embedding(Acting_performance)

        embedding_dict = {"Masterpiece": masterpiece_embedding,
                          "Social_Commentary": social_commentary_embedding,
                          "Suspense_Thrill": suspense_thrill_embedding,
                          "Overrated": overrated_embedding,
                          "Uncomfortable_Controversial": uncomfortable_embedding,
                          "Acting_Performance": acting_performance_embedding}
        
        def classify_review(embedded_review, embedding_dict):
            '''
            개별 리뷰 임베딩을 카테고리 임베딩과 비교하여 가장 유사한 카테고리를 찾는 함수
                Args:
                    embedded_review (numpy.array): 512차원 리뷰 임베딩 벡터
                    embedding_dict (dict): 카테고리별 문장 임베딩 벡터 딕셔너리

                Returns:
                    dict: 각 카테고리별 최대 코사인 유사도 값
            '''
            d = {}
            for keywords in embedding_dict.keys():
                m = 0
                for vec in embedding_dict[keywords]:
                    sim_score = cosine_similarity(embedded_review.reshape(1, -1), vec.reshape(1, -1))[0][0]
                    if sim_score >= m:
                        m = sim_score
                d[keywords] = m

            return d
        
        # 각 리뷰 임베딩을 카테고리에 매핑하여 유사도 계산
        print("코사인 유사도 계산 중...")
        results = []
        for embedded_review in self.embeddings:
            d = classify_review(embedded_review, embedding_dict)
            results.append(d)
            
        self.df_results = pd.DataFrame(results)

         # 카테고리 유사도 결과를 데이터프레임으로 변환
        results = []
        for embedded_review in self.embeddings:
            d = classify_review(embedded_review, embedding_dict)
            results.append(d)
            
        df_results = pd.DataFrame(results)

        # 원본 데이터프레임(self.df)에 512차원 임베딩 & 카테고리 유사도 정보 추가
        self.df = pd.concat([self.df, df_results, df_embeddings], axis=1)

    def save_to_database(self):
        output_path = os.path.join(self.output_dir, "preprocessed_reviews_naver.csv")
        self.df.to_csv(output_path, index = False, encoding="utf-8-sig")
        
        # 저장 완료 메시지 출력
        print(f"데이터가 성공적으로 저장되었습니다: {output_path}")

    def preprocess_entity(self, entity: dict) -> dict:
        """
        단일 네이버 리뷰 entity에 대한 전처리를 수행하는 메서드.
        아래 처리를 수행합니다.
        
          1. 별점 전처리:
             - 문자열에서 12번째 인덱스 이후의 숫자만 추출하여 정수형(int)으로 변환
          2. 작성일자 전처리:
             - 작성일자(writing_date)를 datetime 형식으로 변환한 후, 날짜(date)만 추출
          3. 텍스트(comment) 전처리:
             - 리뷰 텍스트에서 불필요한 특수문자 제거 (숫자와 한글은 보존)
          4. 결측치(null) 처리:
             - 필수 필드(별점, 작성일자, comment)가 없거나, comment가 빈 문자열이면 전처리 대상에서 제외
          5. 이상치(outlier) 처리:
             - bulk 전처리에서는 리뷰 길이가 (평균 + 2.5 * 표준편차)를 초과하면 가장 긴 문장만 남기지만,
               단일 entity의 경우 표본이 1이므로(표준편차=0) 조건에 해당하지 않습니다.
               (코드상 포함되어 있어 추후 여러 entity를 함께 처리할 때 활용 가능)

        Args:
            entity (dict): 전처리할 단일 리뷰 entity. 예:
                           {
                             "star_rating": "별점 : 8",
                             "writing_date": "2020-02-28",
                             "comment": "이 영화는 정말 훌륭했습니다! 다만...",
                             ... 기타 필드 ...
                           }

        Returns:
            dict: 전처리된 리뷰 entity. 필수 조건 미달 시 None 반환.
        """
        required_fields = ["comment"]
        # 결측치 처리: 필수 필드가 없거나 빈 문자열이면 전처리하지 않음
        for field in required_fields:
            if field not in entity or not entity[field].strip():
                return None

        processed_entity = entity.copy()

        # 1.1. 별점 전처리: 12번째 인덱스 이후의 부분을 정수형으로 변환
        try:
            processed_entity["star_rating"] = int(processed_entity["star_rating"][12:])
        except Exception as e:
            return None
        
        # 1.2. 추천 수 전처리: 문자형 -> 정수형
        try:
            processed_entity["upvote"] = int(processed_entity["upvote"])
            processed_entity["downvote"] = int(processed_entity["downvote"])
        except Exception as e:
            return None

        # 2. 작성일자 전처리: datetime 형식으로 변환한 후, 날짜(date)만 추출
        try:
            dt_str = processed_entity["writing_date"].strip() if "writing_date" in entity else None
            processed_entity["writing_date"] = datetime.datetime.strptime(dt_str, '%Y.%m.%d. %H:%M') if dt_str else None
        except:
            processed_entity["writing_date"] = None

        # 3. 텍스트 데이터 전처리: 불필요한 특수문자 제거 (숫자 및 한글 보존)
        try:
            processed_entity["comment"] = re.sub(r"[^0-9ㄱ-ㅎㅏ-ㅣ가-힣 ]", "", processed_entity["comment"])
        except:
            pass
        
        return processed_entity

