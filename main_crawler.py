import os
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.theme import Theme

# 🚨 에러가 났던 import 부분을 파일 맨 위로 올려 들여쓰기 문제를 원천 차단했습니다.
from lib.db_manager import DBManager
from lib.crawler_api import run_crawling

# CLI UI 가독성 극대화를 위한 다크 테마 및 고대비 무채색 설정
custom_theme = Theme({
    "info": "bold cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "muted": "dim white"
})
console = Console(theme=custom_theme)

# 환경변수 및 설정 로드 블록
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, 'lib', 'ad.env')
CONFIG_PATH = os.path.join(BASE_DIR, 'lib', 'config.json')

load_dotenv(ENV_PATH)

def main():
    """ 
    크롤링 실행 제어 블록: 설정 파일을 읽고, 크롤링 루프를 실행하며, 
    Rich 콘솔을 통해 시스템 진행 상황을 시각적으로 로깅합니다. 
    """
    console.print("\n[info]🚀 크롤링 파이프라인 엔진 가동을 시작합니다.[/info]")
    
    if not os.path.exists(CONFIG_PATH):
        console.print("[error]❌ config.json 설정 파일을 찾을 수 없습니다.[/error]")
        return

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    db = DBManager()
    new_found, success, fail = 0, 0, 0

    console.print(f"[muted]타겟 URL {len(config['target_urls'])}곳 스캔 중...[/muted]")
    console.print("[info]🌐 셀레니움 엔진을 가동하여 데이터 수집을 시작합니다...[/info]")
    
    # crawler_api.py의 핵심 함수 호출 (config.json에서 읽어온 주소와 키워드 전달)
    real_results = run_crawling(config['target_urls'], config['keywords'])
    
    # 중복 제거 로직: 수집된 진짜 데이터를 반복문으로 DB 매니저에 전달
    for item in real_results:
        # db.insert_data는 내부적으로 Unique Key 제약을 통해 신규 데이터만 필터링합니다.
        is_new = db.insert_data(item['url'], item['kw'], item['title'])
        
        if is_new:
            new_found += 1
            success += 1
            console.print(f"[success]✅ 신규 데이터 적재:[/success] {item['title']}")
        else:
            console.print(f"[warning]⚠️ 중복 스킵:[/warning] {item['title']}")

    # 메타데이터 통계 동기화
    db.update_metadata(new_found, success, fail)
    console.print(f"\n[info]🎉 크롤링 완료. (신규 발견: {new_found}건, 실패: {fail}건)[/info]")
    console.print("[muted]db_metadata.json 업데이트가 완료되었습니다.[/muted]\n")

if __name__ == "__main__":
    main()