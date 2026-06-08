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

	def run(self, target_urls, search_keywords, exclude_keywords):
		log_message("크롤링 프로세스 시작...", "RUN")
		time.sleep(1) 
		
		# 넘겨받은 타겟 주소 리스트를 하나씩 꺼내어 순회합니다.
		for url in target_urls:
			log_message(f"대상 웹사이트 접속 준비: {url}", "INFO")
			
			# [✔] 수정: 이전 단계의 결과물을 다음 단계로 전달하도록 파이프라인 연결
			raw_html = self._fetch_data(url, search_keywords, exclude_keywords)
			
			if raw_html:
				parsed_items = self._parse_data(raw_html)
				if parsed_items:
					self._save_data(parsed_items)
			
			log_message(f"대상 웹사이트 처리 완료: {url}", "SUCCESS")

	def _fetch_data(self, url, search_keywords, exclude_keywords):
		log_message("├─ [1/3] 웹 페이지 데이터 수집 중...", "RUN")
		log_message(f"│  ├─ 검색(포함) 조건: {', '.join(search_keywords)}", "INFO")
		log_message(f"│  └─ 필터(제외) 조건: {', '.join(exclude_keywords)}", "INFO")
		
		# (여기에 실제 requests 또는 selenium HTML 추출 로직이 들어갑니다)
		sample_html = "<html>테스트 페이지 데이터</html>" 
		return sample_html # [✔] 수정: 수집된 원본 데이터 반환

	def _parse_data(self, raw_html):
		log_message("├─ [2/3] 데이터 분석 및 정보 추출 중...", "RUN")
		
		# (여기에 BeautifulSoup 등을 이용한 파싱 로직이 들어갑니다)
		sample_parsed_data = ["추출된 정보1", "추출된 정보2"]
		return sample_parsed_data # [✔] 수정: 분석이 완료된 정제 데이터 반환

	def _save_data(self, parsed_items):
		log_message("└─ [3/3] 추출된 데이터를 저장 중...", "RUN")
		# (여기에 엑셀이나 JSON으로 저장하는 로직이 들어갑니다)
		log_message(f"   └─ 총 {len(parsed_items)}개의 아이템 저장 완료", "INFO")