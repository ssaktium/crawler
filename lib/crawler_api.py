import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

def run_crawling(target_urls: list, keywords: list) -> list:
    """
    실제 타겟 URL을 순회하며 셀레니움을 통해 키워드와 일치하는 데이터를 수집하여 반환합니다.
    """
    # 1. 크롬 브라우저 스텔스 및 경량화 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 자동화 봇 감지를 피하기 위한 스텔스 모드 적용
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 봇 감지 무력화를 위한 자바스크립트 변수 조작
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
    })

    extracted_data = []

    try:
        # 2. 타겟 URL 순회
        for url in target_urls:
            try:
                driver.get(url)
                # 느린 와이파이 및 시스템 환경을 고려한 15초 넉넉한 대기
                time.sleep(15)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 화면에 보이지 않는 동작 코드(script, style) 제거
                for script_or_style in soup(["script", "style"]):
                    script_or_style.extract()

                # 3. 키워드 기반 데이터 추출 로직
                for keyword in keywords:
                    matched_nodes = soup.find_all(string=re.compile(keyword))
                    
                    for node in matched_nodes:
                        block_tag = node.parent
                        
                        # 의미 있는 문장이 포함된 상위 부모 태그 추적
                        while block_tag.name not in ['a', 'td', 'li', 'p', 'div', 'tr'] and block_tag.parent:
                            block_tag = block_tag.parent
                            
                        # 문자열 여백 및 줄바꿈 정리
                        title = " ".join(block_tag.get_text(separator=' ', strip=True).split())
                        
                        # 실제 클릭 가능한 링크(a 태그) 주소 추출
                        a_tag = block_tag if block_tag.name == 'a' else block_tag.find_parent('a')
                        specific_url = url  # 기본값: 현재 목록 주소
                        
                        if a_tag and a_tag.get('href'):
                            href = a_tag.get('href').strip()
                            if not href.startswith(('javascript:', '#')):
                                specific_url = urljoin(url, href)
                                
                        extracted_data.append({
                            "url": specific_url,
                            "kw": keyword,
                            "title": title
                        })
            except Exception as e:
                # 특정 사이트 접속 에러 발생 시 프로그램 종료 없이 다음 사이트로 패스
                continue
                
    finally:
        # 4. 자원 낭비(좀비 프로세스) 방지를 위한 브라우저 강제 종료
        if driver:
            driver.quit()

    return extracted_data