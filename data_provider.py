import os
import sys
from flask import Flask, jsonify, request # [✔] 수정: request 모듈 추가 임포트
from dotenv import load_dotenv

# 모듈 경로 강제 인식
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
	sys.path.append(current_dir)

from lib.utils import log_message

# 환경변수 로드
env_path = os.path.join(current_dir, 'lib', 'ad.env')
if os.path.exists(env_path):
	load_dotenv(dotenv_path=env_path)

# Flask 설정
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

class DataProvider:
	def __init__(self):
		self.data_dir = os.path.join(current_dir, 'data')
		log_message("DataProvider 및 웹 서버 연동 준비 완료", "SET")

	def get_latest_data(self):
		if not os.path.exists(self.data_dir):
			return {"status": "error", "message": "데이터 폴더가 없습니다."}
			
		files = os.listdir(self.data_dir)
		if not files:
			return {"status": "empty", "message": "수집된 데이터 파일이 없습니다."}
			
		sample_data = {
			"keyword": "테스트 키워드",
			"total_count": 3,
			"items": ["수집 데이터 1", "수집 데이터 2", "수집 데이터 3"]
		}
		
		return {"status": "success", "data": sample_data}

provider = DataProvider()

@app.route('/', methods=['GET'])
def health_check():
	return jsonify({"server_status": "running", "message": "서버가 정상 작동 중입니다."})

@app.route('/api/data', methods=['GET'])
def fetch_crawled_data():
	log_message("외부에서 데이터 요청이 들어왔습니다.", "INFO")
	
	# [✔] 수정: 보안 토큰(비밀번호) 검증 로직 추가
	expected_token = os.environ.get('SECRET_TOKEN')
	client_token = request.headers.get('Authorization')
	
	if client_token != expected_token:
		log_message("비정상적인 접근 시도 차단 (토큰 불일치)", "ERROR")
		return jsonify({"status": "error", "message": "다운로드 권한이 없습니다."}), 401

	result = provider.get_latest_data()
	return jsonify(result)

if __name__ == "__main__":
	# 환경 설정값 불러오기
	SERVER_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
	SERVER_PORT = int(os.environ.get('FLASK_PORT', 5000))
	SERVER_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

	print("-" * 60)
	log_message(f"웹 서버 구동 - HOST: {SERVER_HOST}, PORT: {SERVER_PORT}, DEBUG: {SERVER_DEBUG}", "RUN")
	log_message(f"로컬 접속 주소: http://127.0.0.1:{SERVER_PORT}", "INFO")
	print("-" * 60)
	
	app.run(host=SERVER_HOST, port=SERVER_PORT, debug=SERVER_DEBUG)