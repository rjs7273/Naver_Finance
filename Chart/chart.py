import requests
import json
import pandas as pd
import os

# 저장 경로 설정
SAVE_PATH = "./data/"
STOCK_CODE = "005930"  # 삼성전자 종목 코드

# 요청할 데이터 유형 (일/주/월/분기/년)
TIME_FRAMES = {
    "day": "일봉",
    "week": "주봉",
    "month": "월봉",
    "quarter": "분기봉",
    "year": "년봉"
}

# 네이버 증권 API 기본 URL
BASE_URL = "https://api.stock.naver.com/chart/domestic/item/{}/{}"

# HTTP 요청 헤더
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": f"https://m.stock.naver.com/fchart/domestic/stock/{STOCK_CODE}",
    "Origin": "https://m.stock.naver.com"
}

# 저장 폴더 생성
os.makedirs(SAVE_PATH, exist_ok=True)

def fetch_chart_data(time_frame):
    """ 네이버 증권에서 지정된 기간의 데이터를 가져와 JSON 및 CSV로 저장 """
    url = BASE_URL.format(STOCK_CODE, time_frame)
    params = {
        "startDateTime": "202406010000",  # 시작 날짜 (예: 2024년 6월 1일)
        "endDateTime": "202503181031"  # 종료 날짜 (예: 2025년 3월 18일)
    }

    response = requests.get(url, params=params, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()

        # 파일명 설정
        file_name = f"{STOCK_CODE}_chart_{time_frame}"
        json_file_path = os.path.join(SAVE_PATH, f"{file_name}.json")
        csv_file_path = os.path.join(SAVE_PATH, f"{file_name}.csv")

        # JSON 파일 저장
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"✅ JSON 데이터 저장 완료: {json_file_path}")

        # DataFrame 변환 및 CSV 저장
        df = pd.DataFrame(data)
        df.rename(columns={
            "localDate": "날짜",
            "openPrice": "시가",
            "highPrice": "고가",
            "lowPrice": "저가",
            "closePrice": "종가",
            "accumulatedTradingVolume": "거래량",
            "foreignRetentionRate": "외국인 보유율"
        }, inplace=True)

        # 날짜 형식 변환
        df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")

        df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")
        print(f"✅ CSV 데이터 저장 완료: {csv_file_path}")

        return data
    else:
        print(f"❌ {TIME_FRAMES[time_frame]} 데이터 요청 실패! 상태 코드: {response.status_code}")
        return None

# 모든 기간 데이터 가져오기
for time_frame in TIME_FRAMES.keys():
    fetch_chart_data(time_frame)
