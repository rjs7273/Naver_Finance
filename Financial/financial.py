import requests
import json
import os
import pandas as pd

# 저장 경로 설정
BASE_SAVE_PATH = os.path.join(os.getcwd(), "data")
JSON_SAVE_PATH = os.path.join(BASE_SAVE_PATH, "json")
CSV_SAVE_PATH = os.path.join(BASE_SAVE_PATH, "csv")

# 폴더 생성
os.makedirs(JSON_SAVE_PATH, exist_ok=True)
os.makedirs(CSV_SAVE_PATH, exist_ok=True)

# 대상 종목 및 API 엔드포인트
STOCKS = {
    "005930": {"name": "삼성전자", "url": "https://m.stock.naver.com/api/stock/005930/finance/annual"},
    "000660": {"name": "SK하이닉스", "url": "https://m.stock.naver.com/api/stock/000660/finance/annual"},
    "NVDA.O": {"name": "NVIDIA", "url": "https://api.stock.naver.com/stock/NVDA.O/finance/annual"},
    "TSLA.O": {"name": "Tesla", "url": "https://api.stock.naver.com/stock/TSLA.O/finance/annual"},
}

# API 요청 헤더
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://m.stock.naver.com"
}

def fetch_financial_data(stock_code, url):
    """ 지정된 종목의 연간 재무 데이터를 가져온다. """
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ {STOCKS[stock_code]['name']}({stock_code}) 데이터 요청 실패! 상태 코드: {response.status_code}")
        return None

def save_financial_data(stock_code, data):
    """ JSON 및 CSV 형식으로 저장한다. """
    json_path = os.path.join(JSON_SAVE_PATH, f"{stock_code}_financial_annual.json")
    csv_path = os.path.join(CSV_SAVE_PATH, f"{stock_code}_financial_annual.csv")

    # JSON 저장
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"✅ JSON 저장 완료: {json_path}")

    # CSV 저장 (데이터 가공)
    if "financeInfo" in data and "rowList" in data["financeInfo"]:
        years = [col["key"] for col in data["financeInfo"]["trTitleList"]]
        rows = []

        for row in data["financeInfo"]["rowList"]:
            row_data = {"항목": row["title"]}
            for year in years:
                row_data[year] = row["columns"].get(year, {}).get("value", "-")
            rows.append(row_data)

        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"✅ CSV 저장 완료: {csv_path}")

# 모든 종목에 대해 데이터 요청 및 저장 실행
for stock_code, info in STOCKS.items():
    data = fetch_financial_data(stock_code, info["url"])
    if data:
        save_financial_data(stock_code, data)
