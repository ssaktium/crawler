import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

class SmartCrawler:
	def __init__(self, target_urls, target_keywords, target_exclude_keywords, db_manager, console):
		self.target_urls = target_urls
		self.target_keywords = list(dict.fromkeys(target_keywords))
		self.target_exclude_keywords = target_exclude_keywords
		self.db = db_manager
		self.console = console
		self.driver = None
		self.setup_browser()

	def setup_browser(self):
		self.console.print("[muted]🌐 탐색 엔진 스텔스 모드 셋팅 중...[/muted]")
		chrome_options = Options()
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--disable-dev-shm-usage')
		chrome_options.add_argument('--disable-blink-features=AutomationControlled')
		chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
		chrome_options.add_experimental_option('useAutomationExtension', False)
		
		service = Service(ChromeDriverManager().install())
		self.driver = webdriver.Chrome(service=service, options=chrome_options)
		self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
			"source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
		})
		self.console.print("[success]✅ 503 방화벽 우회 스텔스 모드 장착 완료![/success]")

	def has_excluded_keyword(self, text: str) -> bool:
		for ex_kw in self.target_exclude_keywords:
			if ex_kw in text:
				return True
		return False

	def check_attached_files(self) -> str:
		try:
			html = self.driver.page_source
			text_html = BeautifulSoup(html, 'html.parser').get_text().lower()
			for ext in ['.hwp', '.hwpx', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip']:
				if ext in text_html:
					return "있음 (HWP/PDF 등)"
			return "없음"
		except:
			return "확인불가"

	def run(self):
		new_success, new_fail = 0, 0
		
		try:
			for url in self.target_urls:
				self.console.print(f"\n[info]🌍 사이트 접속 중: {url}[/info]")
				try:
					self.driver.get(url)
					self.console.print("[muted]⏳ 저사양 환경 렌더링을 위해 15초간 대기합니다...[/muted]")
					time.sleep(15)
					
					main_window = self.driver.current_window_handle
					
					for keyword in self.target_keywords:
						self.console.print(f"\n[info]🔎 [현재 검색어: {keyword}] ➡ 정밀 분석 시작[/info]")
						
						soup = BeautifulSoup(self.driver.page_source, 'html.parser')
						matched_elements = soup.find_all(string=re.compile(keyword))
						
						found_items = []
						for element in matched_elements:
							parent = element.parent
							text = parent.get_text(strip=True)
							
							if not text or len(text) < 3 or self.db.is_exist(text) or self.has_excluded_keyword(text):
								continue
								
							a_tag = parent if parent.name == 'a' else parent.find_parent('a')
							near_url, link_feature = url, "정상"
							
							if a_tag and a_tag.get('href'):
								href = a_tag.get('href').strip()
								if "javascript:" in href or href.startswith("fn_") or "return false" in href:
									link_feature = f"[스크립트 이벤트] {href}"
								elif href == "#":
									link_feature = "[가짜링크 #]"
								else:
									near_url = href if href.startswith("http") else urljoin(url, href)
							
							found_items.append({"title": text, "element": parent, "near_url": near_url, "link_feature": link_feature, "keyword": keyword})
						
						if found_items:
							self.console.print(f"\t[success]🎯 새로운 데이터 {len(found_items)}개 발견! 상세 검증 시작...[/success]")
						
						for item in found_items:
							self.console.print(f"\t[muted]⏳ [{item['title'][:15]}...] 렌더링 대기 (15초)...[/muted]")
							success, specific_url, file_status = False, url, "확인불가"
							
							try:
								self.driver.execute_script("arguments[0].setAttribute('target', '_blank'); arguments[0].click();", item['element'])
								time.sleep(15) 
								
								if len(self.driver.window_handles) > 1:
									for handle in self.driver.window_handles:
										if handle != main_window:
											self.driver.switch_to.window(handle)
											specific_url, file_status, success = self.driver.current_url, self.check_attached_files(), True
											self.driver.close()
											break
									self.driver.switch_to.window(main_window)
								else:
									if self.driver.current_url != url:
										specific_url, file_status, success = self.driver.current_url, self.check_attached_files(), True
										self.driver.get(url)
										time.sleep(15)
							except Exception:
								pass
							finally:
								if len(self.driver.window_handles) > 1:
									for handle in self.driver.window_handles:
										if handle != main_window:
											self.driver.switch_to.window(handle)
											self.driver.close()
									self.driver.switch_to.window(main_window)
							
							if success:
								if self.db.insert_data("성공", item['keyword'], item['title'], item['title'], specific_url, file_status, item['link_feature']):
									new_success += 1
									self.console.print("\t\t[success]✅ [성공] 상세 주소 원본 100% 획득 완료![/success]")
							else:
								if self.db.insert_data("실패", item['keyword'], item['title'], item['title'], item['near_url'], file_status, item['link_feature']):
									new_fail += 1
									self.console.print("\t\t[error]❌ [실패] 추적 불가. 목록 주소로 대체 저장합니다.[/error]")
				except Exception as e:
					self.console.print(f"\t[error]❌ 접속 에러 발생 (건너뜁니다): {str(e)}[/error]")
		finally:
			if self.driver:
				self.console.print("\n[muted]🧹 브라우저 메모리 정리 중...[/muted]")
				self.driver.quit()
				
		return new_success, new_fail