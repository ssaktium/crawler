import os
import json
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)

CORS(app)

load_dotenv("lib/ad.env")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "my_super_secret_token")

SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", 5000))

JSON_FILE_PATH = "data/crawling_summary.json"
EXCEL_FILE_PATH = "data/crawling_results.xlsx"

@app.route('/api/summary', methods=['GET'])
def get_summary():
	auth_header = request.headers.get('Authorization')

	if auth_header != f"Bearer {SECRET_TOKEN}":
		return jsonify({"error": "Unauthorized"}), 401

	if os.path.exists(JSON_FILE_PATH):
		with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
			data = json.load(f)
		return jsonify(data), 200
	else:
		return jsonify({"error": "Data not found"}), 404

@app.route('/api/excel', methods=['GET'])
def get_excel():
	token = request.args.get('token')

	if token != SECRET_TOKEN:
		return "Unauthorized", 401

	if os.path.exists(EXCEL_FILE_PATH):
		return send_file(EXCEL_FILE_PATH, as_attachment=True)
	else:
		return "Excel file not found", 404

if __name__ == '__main__':
	print("[SYSTEM] API Service is securely running.")
	app.run(host=SERVER_HOST, port=SERVER_PORT)