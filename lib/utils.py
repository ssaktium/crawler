import time

def calculate_time_diff(start_time: float, end_time: float) -> str:
	""" 소요 시간을 계산하여 시, 분, 초 포맷으로 반환합니다. """
	elapsed = end_time - start_time
	hours = int(elapsed // 3600)
	minutes = int((elapsed % 3600) // 60)
	seconds = int(elapsed % 60)
	
	if hours > 0:
		return f"{hours}시간 {minutes}분 {seconds}초"
	elif minutes > 0:
		return f"{minutes}분 {seconds}초"
	else:
		return f"{seconds}초"