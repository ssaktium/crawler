import os
import json
import sqlite3
import openpyxl
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import FileResponse
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, 'lib', 'ad.env')
load_dotenv(ENV_PATH)

API_SECRET_KEY = os.getenv("API_SECRET_KEY")
DATA_DIR = os.path.join(BASE_DIR, 'data')
META_PATH = os.path.join(DATA_DIR, 'db_metadata.json')
DB_PATH = os.path.join(DATA_DIR, 'core_db.sqlite')
EXPORT_DIR = os.path.join(DATA_DIR, 'export')

app = FastAPI(title="Lightweight Data Provider API")

def verify_token(authorization: str = Header(None)):
	if not authorization or authorization != f"Bearer {API_SECRET_KEY}":
		raise HTTPException(status_code=401, detail="Unauthorized")
	return True

@app.get("/api/status", dependencies=[Depends(verify_token)])
def get_system_status():
	""" 시스템 상태 및 메타데이터를 반환합니다. """
	if not os.path.exists(META_PATH):
		raise HTTPException(status_code=404, detail="Metadata not found")
	with open(META_PATH, 'r', encoding='utf-8') as f:
		data = json.load(f)
	return {"status": "success", "data": data}

@app.get("/api/export/excel")
def export_excel_data(token: str = None):
	""" 
	데이터 동시성 충돌을 막기 위해 API 호출 시점에 DB를 읽어 엑셀로 추출합니다.
	주소창 접속을 위해 파라미터(token)로 보안을 검증합니다.
	"""
	if token != API_SECRET_KEY:
		raise HTTPException(status_code=401, detail="Unauthorized")

	os.makedirs(EXPORT_DIR, exist_ok=True)
	if not os.path.exists(DB_PATH):
		raise HTTPException(status_code=404, detail="Database not found")

	with sqlite3.connect(DB_PATH) as conn:
		cursor = conn.cursor()
		cursor.execute("""
			SELECT collected_at, status, keyword, title, found_text, source_url, has_attachment, link_feature 
			FROM crawled_data ORDER BY id DESC
		""")
		rows = cursor.fetchall()

	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "수집데이터"
	ws.append(["검색 일시", "수집 상태", "발견된 키워드", "전체 제목", "발견된 텍스트", "해당 주소", "첨부파일 유무", "링크 특이사항"])

	for row in rows:
		ws.append(row)

	file_name = f"crawled_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
	file_path = os.path.join(EXPORT_DIR, file_name)
	wb.save(file_path)

	return FileResponse(
		path=file_path, filename=file_name, 
		media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	)