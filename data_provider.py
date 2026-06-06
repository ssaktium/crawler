import os
import json
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
# 외부 도메인에서 데이터를 호출할 수 있도록 CORS 전면 허용
CORS(app)

# crawling/ad.env 파일에서 비밀번호(Token)를 불러옵니다.
load_dotenv("crawling/ad.env")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "my_super_secret_token")

# 크롤러가 생성해둔 파일의 상대 경로
JSON_FILE_PATH = "crawling_summary.json"
EXCEL_FILE_PATH = "crawling_results.xlsx"

@app.route('/api/summary', methods=['GET'])
def get_summary():
	"""외부 웹서버가 요약 통계(JSON)를 가져갈 때 사용하는 주소"""
	auth_header = request.headers.get('Authorization')
	
	# 토큰 보안 검사
	if auth_header != f"Bearer {SECRET_TOKEN}":
		return jsonify({"error": "Unauthorized - 권한이 없습니다."}), 401

	# 파일이 존재하면 JSON 내용 그대로 전송
	if os.path.exists(JSON_FILE_PATH):
		with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
			data = json.load(f)
		return jsonify(data), 200
	else:
		return jsonify({"error": "Data not found"}), 404

@app.route('/api/excel', methods=['GET'])
def get_excel():
	"""외부 웹서버가 엑셀 파일을 통째로 다운로드해 갈 때 사용하는 주소"""
	# 다운로드는 브라우저 URL로 직접 접근하므로 파라미터(?token=...)를 확인합니다.
	token = request.args.get('token')
	
	if token != SECRET_TOKEN:
		return "Unauthorized - 권한이 없습니다.", 401

	if os.path.exists(EXCEL_FILE_PATH):
		return send_file(EXCEL_FILE_PATH, as_attachment=True)
	else:
		return "Excel file not found", 404

if __name__ == '__main__':
	# 내 리눅스 컴퓨터의 5000번 포트를 열고 외부의 호출을 24시간 대기합니다.
	print("📡 [데이터 API 서버 가동] 공유기 포트포워딩(5000번)을 통한 외부 요청을 기다립니다...")
	app.run(host='0.0.0.0', port=5000)