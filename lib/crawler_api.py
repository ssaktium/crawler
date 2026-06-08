import os
import time
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup

class CrawlerAPI:
	def __init__(self, target_urls, search_keywords):
		# 메인 파일에서 넘어온 주소와 키워드를 엔진 내부에 장착합니다.
		self.target_urls = target_urls
		self.search_keywords = search_keywords
		self.results = []

	def run(self):
		print("========================================")
		print(f"🚀 크롤링 엔진 가동 시작! (대상: {len(self.target_urls)}곳)")
		print("========================================")

		if not self.target_urls:
			print("❌ 에러: 수집할 URL이 없습니다. main_crawler.py를 확인해주세요.")
			return

		# 1. 크롤링 파이프라인 (웹 탐색)
		for url in self.target_urls:
			print(f"\n⏳ [접속 대기중] 서버 차단 방지를 위해 3초 타이머가 돕니다...")
			time.sleep(3) # 멈춰있던 타이머 기능 부활!
			print(f"🌐 접속 시도: {url}")
			self._fetch_data(url)

		# 2. 데이터 저장 파이프라인 (엑셀/JSON 생성)
		if self.results:
			self._save_data()
			print(f"\n✅ 작업이 성공적으로 완료되었습니다! 총 {len(self.results)}개의 데이터를 저장했습니다.")
		else:
			print("\n⚠️ 탐색 완료! 하지만 사이트에서 요청하신 키워드를 찾지 못해 파일을 생성하지 않았습니다.")

	def _fetch_data(self, url):
		try:
			# 사람이 접속한 것처럼 속이기 위한 User-Agent 헤더 추가
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
			response = requests.get(url, headers=headers, timeout=10)
			response.raise_for_status()
			
			# 웹 페이지에서 눈에 보이는 텍스트만 깔끔하게 발라내기
			soup = BeautifulSoup(response.text, 'html.parser')
			text_content = soup.get_text(separator=' ', strip=True)
			
			# 다음 단계인 분석(키워드 찾기)으로 텍스트 넘기기
			self._parse_data(url, text_content)
			
		except requests.exceptions.RequestException as e:
			print(f"❌ 접속 실패 ({url}): {e}")

	def _parse_data(self, url, text_content):
		found_any = False
		# 사용자가 입력한 키워드가 본문에 있는지 하나씩 검사
		for keyword in self.search_keywords:
			if keyword in text_content:
				print(f"  💡 핵심 키워드 발견!: '{keyword}'")
				self.results.append({
					"Target_URL": url,
					"Keyword": keyword,
					"Scraped_Time": time.strftime("%Y-%m-%d %H:%M:%S")
				})
				found_any = True
				
		if not found_any:
			print("  - 앗, 이 사이트에는 요청하신 키워드가 없습니다.")

	def _save_data(self):
		# 안전하게 data 폴더 생성 (이미 있으면 무사 통과)
		os.makedirs('data', exist_ok=True)
		
		# 엑셀 파일 저장 (.xlsx)
		excel_path = 'data/crawling_results.xlsx'
		df = pd.DataFrame(self.results)
		df.to_excel(excel_path, index=False)
		
		# JSON 파일 저장 (.json)
		json_path = 'data/crawling_summary.json'
		with open(json_path, 'w', encoding='utf-8') as f:
			json.dump(self.results, f, ensure_ascii=False, indent=4)
		
		print(f"\n💾 엑셀 저장 완료: {excel_path}")
		print(f"💾 JSON 저장 완료: {json_path}")