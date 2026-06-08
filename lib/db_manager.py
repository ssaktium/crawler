import sqlite3
import json
import os
import hashlib
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'core_db.sqlite')
META_PATH = os.path.join(DATA_DIR, 'db_metadata.json')

class DBManager:
	""" SQLite 데이터베이스 연결 및 쿼리 제어, 중복 검증 전담 클래스 """
	def __init__(self):
		os.makedirs(DATA_DIR, exist_ok=True)
		self._initialize_db()
		self._ensure_metadata()

	def _initialize_db(self):
		with sqlite3.connect(DB_PATH) as conn:
			cursor = conn.cursor()
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS crawled_data (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					collected_at TEXT,
					status TEXT,
					keyword TEXT,
					title TEXT,
					found_text TEXT,
					source_url TEXT,
					has_attachment TEXT,
					link_feature TEXT,
					url_hash TEXT UNIQUE
				)
			''')
			conn.commit()

	def _ensure_metadata(self):
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

	def is_exist(self, title: str) -> bool:
		""" 기존 데이터베이스에 존재하는 텍스트인지 판별하여 즉시 스킵을 돕습니다. """
		with sqlite3.connect(DB_PATH) as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT 1 FROM crawled_data WHERE title = ?", (title,))
			return cursor.fetchone() is not None

	def insert_data(self, status: str, keyword: str, title: str, found_text: str, source_url: str, has_attachment: str, link_feature: str) -> bool:
		""" 고유 키(Unique Key)를 통해 신규 데이터만 DB에 적재합니다. """
		hash_input = f"{title}".encode('utf-8')
		url_hash = hashlib.sha256(hash_input).hexdigest()
		collected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		try:
			with sqlite3.connect(DB_PATH) as conn:
				cursor = conn.cursor()
				cursor.execute('''
					INSERT INTO crawled_data (collected_at, status, keyword, title, found_text, source_url, has_attachment, link_feature, url_hash)
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
				''', (collected_at, status, keyword, title, found_text, source_url, has_attachment, link_feature, url_hash))
				conn.commit()
				return True
		except sqlite3.IntegrityError:
			return False

	def update_metadata(self, new_found: int, success: int, fail: int):
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