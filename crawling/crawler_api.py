import os
import time
from lib.utils import log_message, ensure_directory

class SmartCrawler:
	def __init__(self):
		log_message("SmartCrawler 엔진 초기화 중...", "SET")
		
		# 프로젝트 최상위 경로 및 data 폴더 경로 설정
		self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		self.data_dir = os.path.join(self.base_dir, 'data')
		
		# utils의 폴더 생성 함수 호출
		ensure_directory(self.data_dir)

	# [⚙] main_crawler.py에서 넘겨준 리스트 3개를 파라미터로 받습니다.
	def run(self, target_urls, search_keywords, exclude_keywords):
		log_message("크롤링 프로세스 시작...", "RUN")
		time.sleep(1) 
		
		# [▶] 타겟 주소 리스트를 하나씩 꺼내어 순회합니다.
		for url in target_urls:
			log_message(f"대상 웹사이트 접속 준비: {url}", "INFO")
			
			self._fetch_data(url, search_keywords, exclude_keywords)
			self._parse_data()
			self._save_data()

	def _fetch_data(self, url, search_keywords, exclude_keywords):
		log_message("├─ [1/3] 웹 페이지 데이터 수집 중...", "RUN")
		log_message(f"│  ├─ 검색(포함) 조건: {', '.join(search_keywords)}", "INFO")
		log_message(f"│  └─ 필터(제외) 조건: {', '.join(exclude_keywords)}", "INFO")
		
		# [ℹ] 실제 requests나 selenium으로 접속 및 데이터 수집하는 로직 작성 부분
		pass

	def _parse_data(self):
		log_message("├─ [2/3] 데이터 분석 및 정보 추출 중...", "RUN")
		# [ℹ] 수집된 HTML에서 데이터를 파싱하고 키워드를 필터링하는 로직 작성 부분
		pass

	def _save_data(self):
		log_message("└─ [3/3] 추출된 데이터를 저장 중...", "RUN")
		# [ℹ] 정제된 데이터를 엑셀이나 DB 등에 저장하는 로직 작성 부분
		pass