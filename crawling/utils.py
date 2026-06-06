def format_execution_time(seconds: float) -> str:
	seconds = int(seconds)
	if seconds == 0:
		return "0초"
	
	hours = seconds // 3600
	minutes = (seconds % 3600) // 60
	secs = seconds % 60
	
	if hours > 0:
		return f"{hours}시간 {minutes}분 {secs}초"
	elif minutes > 0:
		return f"{minutes}분 {secs}초"
	else:
		return f"{secs}초"