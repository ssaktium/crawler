import time
from lib.crawler_api import SmartCrawler

if __name__ == "__main__":
	target_urls = [
		"https://mafra.go.kr/home/5108/subview.do",
		"https://www.koat.or.kr/board/business/list.do",
		"https://www.nongupez.go.kr/nsm/bizAply/wholeBiz/wholeBizMain",
		"https://www.greendaero.go.kr/svc/rfph/cpif/front/home.do",
		"https://bizinfo.go.kr/sii/siia/selectSIIA200View.do?pblancId=&hashCode=&rowsSel=6&rows=15&cpage=1&cat=&schJrsdCodeTy=&schWntyAt=&schAreaDetailCodes=6420000&schEndAt=N&orderGb=&sort=&schPblancDiv=01&condition=searchPblancNm&condition1=AND&preKeywords=&keyword="
	]
	
	target_keywords = ["청년", "지원금", "농업정책자금", "영농정착", "귀농"]
	target_exclude_keywords = []

	start_time = time.time()
	print("[START] 크롤링 파이프라인을 시작합니다...")

	crawler = SmartCrawler(
		urls=target_urls,
		keywords=target_keywords,
		exclude_keywords=target_exclude_keywords
	)
	crawler.run_crawler()

	end_time = time.time()
	elapsed_seconds = int(end_time - start_time)

	if elapsed_seconds < 60:
		time_str = f"{elapsed_seconds}초"
	elif elapsed_seconds < 3600:
		time_str = f"{elapsed_seconds // 60}분 {elapsed_seconds % 60}초"
	else:
		time_str = f"{elapsed_seconds // 3600}시간 {(elapsed_seconds % 3600) // 60}분 {elapsed_seconds % 60}초"

	print(f"\n[DONE] 모든 크롤링 작업이 완료되었습니다! (총 소요 시간: {time_str})")