from fastapi import APIRouter, HTTPException, Response, status
from database.mongodb_connection import mongo_db

router = APIRouter(prefix="/review", tags=["review"])

@router.post("/preprocess/{site_name}")
def preprocess_reviews(site_name: str):
    raw_collection = mongo_db.raw_reviews
    preprocessed_collection = mongo_db.preprocessed_reviews

    raw_docs = list(raw_collection.find({"site": site_name}))

    if not raw_docs:
        raise HTTPException(
            status_code=404,
            detail=f"No raw reviews found for the site '{site_name}'"
        )

    if site_name.lower() == "imdb":
        from review_analysis.preprocessing.imdb_processor import ImdbProcessor
        processor = ImdbProcessor("", "")
    elif site_name.lower() == "naver":
        from review_analysis.preprocessing.naver_processor import NaverProcessor
        processor = NaverProcessor("", "")
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported site '{site_name}'"
        )
    existing_doc = preprocessed_collection.find_one({"site": site_name})
    if existing_doc:
        preprocessed_collection.delete_many({"site": site_name})
        
    processed_docs = []
    for doc in raw_docs:
        processed_entity = processor.preprocess_entity(doc)
        if processed_entity is not None:
            if isinstance(processed_entity, tuple):
                processed_entity = processed_entity[0]
            
            processed_docs.append(processed_entity)
        else:
            print("This review was excluded from preprocessing due to missing values or outliers.")
    
    if not processed_docs:
        return {
            "message": f"No new documents to process for site '{site_name}'.",
            "processed_count": 0
        }

    result = preprocessed_collection.insert_many(processed_docs)
    return {"message": f"Processed {len(result.inserted_ids)} reviews for site '{site_name}'."}
