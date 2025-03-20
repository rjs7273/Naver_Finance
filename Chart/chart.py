import requests
import json
import pandas as pd
import os
from datetime import datetime

# 저장 경로 설정
BASE_SAVE_PATH = "./data/"
JSON_SAVE_PATH = os.path.join(BASE_SAVE_PATH, "json")
CSV_SAVE_PATH = os.path.join(BASE_SAVE_PATH, "csv")

# 종목 코드 및 시장 구분 (국내: domestic, 해외: foreign)
STOCKS = {
    "005930": {"name": "삼성전자", "market": "domestic"},
    "000660": {"name": "SK하이닉스", "market": "domestic"},
    "NVDA.O": {"name": "엔비디아", "market": "foreign"},
    "TSLA.O": {"name": "테슬라", "market": "foreign"},
}

# 요청할 데이터 유형
TIME_FRAMES = ["day", "week", "month", "quarter", "year"]

# 데이터 요청 기간 설정 (사용자가 조정 가능)
START_DATE = "202309230000"  # 2023년 9월 23일
END_DATE = datetime.now().strftime("%Y%m%d%H%M")  # 현재 시간 기준

# 네이버 증권 API 기본 URL
BASE_URL = "https://api.stock.naver.com/chart/{}/item/{}/{}"

# 저장 폴더 생성
for tf in TIME_FRAMES:
    os.makedirs(os.path.join(JSON_SAVE_PATH, tf), exist_ok=True)
    os.makedirs(os.path.join(CSV_SAVE_PATH, tf), exist_ok=True)

def fetch_chart_data(stock_code, market, time_frame):
    """ 네이버 증권에서 지정된 기간의 데이터를 가져와 JSON 및 CSV로 저장 """
    url = BASE_URL.format(market, stock_code, time_frame)
    params = {"startDateTime": START_DATE, "endDateTime": END_DATE}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": f"https://m.stock.naver.com/fchart/{market}/stock/{stock_code}",
        "Origin": "https://m.stock.naver.com"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # 파일 저장 경로 설정
        file_name = f"{stock_code}_{time_frame}"
        json_file_path = os.path.join(JSON_SAVE_PATH, time_frame, f"{file_name}.json")
        csv_file_path = os.path.join(CSV_SAVE_PATH, time_frame, f"{file_name}.csv")

        # JSON 저장
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"✅ JSON 데이터 저장 완료: {json_file_path}")

        # DataFrame 변환 및 CSV 저장
        df = pd.DataFrame(data)
        if not df.empty:
            df.rename(columns={
                "localDate": "날짜",
                "openPrice": "시가",
                "highPrice": "고가",
                "lowPrice": "저가",
                "closePrice": "종가",
                "accumulatedTradingVolume": "거래량",
                "foreignRetentionRate": "외국인 보유율"
            }, inplace=True)

            df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")

            df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")
            print(f"✅ CSV 데이터 저장 완료: {csv_file_path}")

        return data
    else:
        print(f"❌ {STOCKS[stock_code]['name']}({stock_code}) {time_frame} 데이터 요청 실패! 상태 코드: {response.status_code}")
        return None

# 모든 종목에 대해 데이터 가져오기
for stock_code, info in STOCKS.items():
    for time_frame in TIME_FRAMES:
        fetch_chart_data(stock_code, info["market"], time_frame)
