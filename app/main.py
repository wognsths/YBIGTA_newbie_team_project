import os
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import httpx
from contextlib import asynccontextmanager

from app.user.user_router import user
from app.review.review_router import router as review_router
from app.config import PORT

static_path = os.path.join(os.path.dirname(__file__), "static")

# 백그라운드 태스크로 전처리 API 호출을 위한 함수
async def run_preprocessing():
    # 서버가 완전히 기동될 시간을 주기 위해 잠시 대기 (예: 2초)
    await asyncio.sleep(5)
    async with httpx.AsyncClient() as client:
        for site in ["naver", "imdb"]:
            url = f"http://127.0.0.1:{PORT}/review/preprocess/{site}"
            try:
                response = await client.post(url)
                print(f"Preprocessing {site}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error preprocessing {site}: {repr(e)}")

# Lifespan 컨텍스트 매니저를 사용하여 서버 시작과 종료 사이에 백그라운드 태스크 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 전에(아직 요청을 받을 준비가 되기 전) 초기화 작업이 있다면 여기서 수행
    # 백그라운드 태스크를 생성합니다.
    task = asyncio.create_task(run_preprocessing())
    yield  # 이 시점부터 서버가 외부 요청을 수락합니다.
    # 서버 종료 시까지 백그라운드 태스크가 완료될 때까지 기다립니다.
    await task

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory=static_path), name="static")
app.include_router(user)
app.include_router(review_router)

if __name__=="__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)