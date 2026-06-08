import os
import json
import time
from dotenv import load_dotenv
from rich.console import Console
from rich.theme import Theme

from lib.db_manager import DBManager
from lib.crawler_api import SmartCrawler
from lib.utils import calculate_time_diff

# CLI UI 가독성 극대화를 위한 다크 테마 설정
custom_theme = Theme({
	"info": "bold cyan",
	"success": "bold green",
	"warning": "bold yellow",
	"error": "bold red",
	"muted": "dim white"
})
console = Console(theme=custom_theme)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, 'lib', 'ad.env')
CONFIG_PATH = os.path.join(BASE_DIR, 'lib', 'config.json')

load_dotenv(ENV_PATH)

def main():
	""" 크롤링 엔진 가동 및 진행 상황을 Rich로 시각화합니다. """
	start_time = time.time()
	console.print("\n[info]🚀 경량 크롤링 파이프라인 엔진 가동을 시작합니다.[/info]")
	
	if not os.path.exists(CONFIG_PATH):
		console.print("[error]❌ lib/config.json 설정 파일을 찾을 수 없습니다.[/error]")
		return

	with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
		config = json.load(f)

	db = DBManager()
	crawler = SmartCrawler(
		target_urls=config.get('target_urls', []),
		target_keywords=config.get('keywords', []),
		target_exclude_keywords=config.get('exclude_keywords', []),
		db_manager=db,
		console=console
	)
	
	try:
		new_success, new_fail = crawler.run()
	except Exception as e:
		console.print(f"[error]❌ 치명적 에러 발생: {str(e)}[/error]")
		new_success, new_fail = 0, 0

	db.update_metadata(new_success + new_fail, new_success, new_fail)
	duration = calculate_time_diff(start_time, time.time())
	
	console.print("\n" + "="*65)
	console.print(f"[info]🎉 크롤링 완료. (신규 획득: {new_success}건, 대체 보존: {new_fail}건)[/info]")
	console.print(f"[muted] ⌛ 총 소요 시간: {duration}[/muted]")
	console.print("[muted]내장 DB 업데이트가 완료되었습니다.[/muted]")
	console.print("="*65 + "\n")

if __name__ == "__main__":
	main()