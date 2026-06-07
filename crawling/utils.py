import os
from datetime import datetime

def get_current_timestamp():
	"""현재 시간을 포맷팅하여 반환합니다."""
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_directory(directory_path):
	"""지정된 경로에 폴더가 없으면 생성합니다."""
	if not os.path.exists(directory_path):
		os.makedirs(directory_path)
		log_message(f"새 디렉토리를 생성했습니다: {directory_path}", "INFO")

def log_message(message, level="INFO"):
	"""단색 기호를 적용한 중앙 통제식 로그 출력 유틸리티입니다."""
	time_str = get_current_timestamp()
	
	# 레벨에 따른 단색 아이콘 매핑
	icons = {
		"INFO": "[ℹ]",
		"ERROR": "[✖]",
		"SUCCESS": "[✔]",
		"RUN": "[▶]",
		"SET": "[⚙]"
	}
	icon = icons.get(level, "[ℹ]")
	
	print(f"[{time_str}] {icon} {message}")