import os
import json
from fastapi import FastAPI, Depends, HTTPException, Header
from dotenv import load_dotenv

# 보안 환경변수 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, 'lib', 'ad.env')
load_dotenv(ENV_PATH)

API_SECRET_KEY = os.getenv("API_SECRET_KEY")
META_PATH = os.path.join(BASE_DIR, 'data', 'db_metadata.json')

app = FastAPI(title="Lightweight Data Provider API")

def verify_token(authorization: str = Header(None)):
    """ 보안 블록: 외부 웹서버 호출 시 헤더의 Bearer 토큰 무결성 검증 """
    if not authorization or authorization != f"Bearer {API_SECRET_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized - 보안 토큰이 유효하지 않습니다.")
    return True

@app.get("/api/status", dependencies=[Depends(verify_token)])
def get_system_status():
    """ 
    데이터 제공 블록: 크롤러가 갱신한 최신 메타데이터 JSON을 읽어 반환.
    파일 접근 시 Race Condition 최소화를 위해 읽기 전용으로 빠르게 반환합니다.
    """
    if not os.path.exists(META_PATH):
        raise HTTPException(status_code=404, detail="Metadata not found")
        
    with open(META_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    return {"status": "success", "data": data}