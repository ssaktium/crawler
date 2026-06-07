import os
import sys

# 모듈 경로 강제 인식
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
	sys.path.append(current_dir)

try:
	from lib.crawler_api import SmartCrawler
	from lib.utils import log_message
except ImportError as e:
	print(f"[✖] 모듈 로드 실패: {e}")
	sys.exit(1)

def main():
	print("-" * 60)
	log_message("크롤링 프로젝트를 실행합니다.", "RUN")
	print("-" * 60)
	
	# [⚙] 크롤링할 타겟 주소 리스트
	target_urls = [
		"https://mafra.go.kr/home/5108/subview.do",
		"https://www.koat.or.kr/board/business/list.do"
	]
	
	# [⚙] 포함할 키워드와 제외할 키워드 설정
	search_keywords = ["청년", "지원금", "농업정책자금", "영농정착", "귀농"]
	exclude_keywords = ["여성"]
	
	crawler = SmartCrawler()
	
	try:
		# [▶] 리스트 형태의 데이터들을 엔진으로 전달
		crawler.run(target_urls, search_keywords, exclude_keywords)
		
		log_message("모든 크롤링 작업이 성공적으로 완료되었습니다.", "SUCCESS")
	except KeyboardInterrupt:
		print()
		log_message("사용자에 의해 작업이 강제 종료되었습니다.", "ERROR")
	except Exception as e:
		print()
		log_message(f"시스템 오류 발생: {e}", "ERROR")

if __name__ == "__main__":
	main()