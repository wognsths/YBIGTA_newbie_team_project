import os
import subprocess
import sys
import glob
from argparse import ArgumentParser
from typing import Dict, Type
# from review_analysis.preprocessing.base_processor import BaseDataProcessor
# from review_analysis.preprocessing.example_processorㅡ import ExampleProcessor
# from review_analysis.preprocessing.imdb_processor import ImdbProcessor
from base_processor import BaseDataProcessor
from imdb_processor import ImdbProcessor


# 모든 preprocessing 클래스를 예시 형식으로 적어주세요. 
# key는 "reviews_사이트이름"으로, value는 해당 처리를 위한 클래스
PREPROCESS_CLASSES: Dict[str, Type[BaseDataProcessor]] = {
    # "reviews_example": ExampleProcessor,
    "reviews_imdb": ImdbProcessor
    # key는 크롤링한 csv파일 이름으로 적어주세요! ex. reviews_naver.csv -> reviews_naver
}
# print(f"Selected processor: {PREPROCESS_CLASSES.keys()}")

REVIEW_COLLECTIONS = glob.glob(os.path.join("..","..","database", "reviews_*.csv"))
# print("Discovered files:", REVIEW_COLLECTIONS)

def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-o', '--output_dir', type=str, required=False, default = "../../database", help="Output file dir. Example: ../../database")
    parser.add_argument('-c', '--preprocessor', type=str, required=False, choices=PREPROCESS_CLASSES.keys(),
                        help=f"Which processor to use. Choices: {', '.join(PREPROCESS_CLASSES.keys())}")
    parser.add_argument('-a', '--all', action='store_true',
                        help="Run all data preprocessors. Default to False.")    
    return parser

def install_requirements():
    requirements_file = "../../requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found.")
        return
    
    try:
        # pip install -r requirements.txt 실행
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":

    parser = create_parser()
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.all: 
        for csv_file in REVIEW_COLLECTIONS:
            base_name = os.path.splitext(os.path.basename(csv_file))[0]
            if base_name in PREPROCESS_CLASSES:
                preprocessor_class = PREPROCESS_CLASSES[base_name]
                preprocessor = preprocessor_class(csv_file, args.output_dir)
                preprocessor.preprocess()
                preprocessor.feature_engineering()
                preprocessor.save_to_database()