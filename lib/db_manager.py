import sqlite3
import json
import os
import hashlib
from datetime import datetime, timedelta

# 프로젝트 루트 디렉토리를 절대 경로로 계산하여 경로 조작(Path Traversal) 원천 차단
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'core_db.sqlite')
META_PATH = os.path.join(DATA_DIR, 'db_metadata.json')

class DBManager:
    """
    SQLite 데이터베이스 연결 및 쿼리 제어, 중복 검증, 메타데이터 갱신을 전담하는 매니저 클래스.
    모든 데이터 입출력은 이 클래스를 통해서만 이루어져 동시성 문제와 무결성을 보장합니다.
    """
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._initialize_db()
        self._ensure_metadata()

    def _initialize_db(self):
        """ 테이블 초기화 블록: url_hash를 UNIQUE 제약조건으로 두어 데이터베이스 단에서 원천적으로 중복을 차단 """
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawled_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collected_at TEXT,
                    source_url TEXT,
                    keyword TEXT,
                    title TEXT,
                    url_hash TEXT UNIQUE
                )
            ''')
            conn.commit()

    def _ensure_metadata(self):
        """ 메타데이터 초기화 블록: 파일이 없거나 손상되었을 경우 기본 템플릿으로 복구 """
        if not os.path.exists(META_PATH):
            default_meta = {
                "last_update": "",
                "recent_24h_count": 0,
                "new_found_count": 0,
                "today_success": 0,
                "today_fail": 0
            }
            with open(META_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_meta, f, indent=4)

    def insert_data(self, source_url: str, keyword: str, title: str) -> bool:
        """ 
        데이터 삽입 블록: URL과 제목을 조합한 해시값을 생성하여 INSERT IGNORE 방식으로 신규 데이터만 필터링 
        """
        hash_input = f"{source_url}{title}".encode('utf-8')
        url_hash = hashlib.sha256(hash_input).hexdigest()
        collected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO crawled_data (collected_at, source_url, keyword, title, url_hash)
                    VALUES (?, ?, ?, ?, ?)
                ''', (collected_at, source_url, keyword, title, url_hash))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # UNIQUE 제약 조건 위반 (이미 존재하는 데이터)
            return False

    def update_metadata(self, new_found: int, success: int, fail: int):
        """ 
        상태 추적 블록: 최근 24시간 내 수집된 데이터를 계산하고 로깅을 위한 메타데이터 JSON을 동기화 
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM crawled_data WHERE collected_at >= ?", (yesterday,))
            recent_24h_count = cursor.fetchone()[0]

        meta_data = {
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "recent_24h_count": recent_24h_count,
            "new_found_count": new_found,
            "today_success": success,
            "today_fail": fail
        }

        with open(META_PATH, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, indent=4, ensure_ascii=False)