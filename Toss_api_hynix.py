import requests
import time
import csv
from datetime import datetime

# 요청할 URL
url = "https://wts-cert-api.tossinvest.com/api/v3/comments"

# 요청 헤더 (쿠키와 XSRF 토큰은 본인의 것으로 변경 필요)
headers = {
    "x-xsrf-token": "cbdf01bd-3e7d-4d8b-8a41-f04d152fa54c",  # 본인 값으로 변경
    "cookie": "SESSION=MmJiZTkzMjktNzZkZS00MjRlLWJjZTktODM5YTIyMmI3YmJm; ...",  # 본인 쿠키 값 사용
    "content-type": "application/json",
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

# 수집할 날짜 범위 (YYYY-MM-DD)
start_date = "2025-03-15"  # 시작 날짜
end_date = "2025-03-18"    # 종료 날짜

# CSV 파일명
csv_filename = "sk_hynix_comments.csv"

# 초기 데이터 (첫 페이지 요청) - SK하이닉스로 변경
data = {
    "subjectId": "KR7000660001",  # 삼성전자 → SK하이닉스 변경
    "subjectType": "STOCK",
    "commentSortType": "RECENT"  # 최신순 정렬
}

# 전체 댓글 저장 리스트
all_comments = []
previous_count = 0  # 이전 수집된 댓글 개수 저장

# 날짜를 비교하는 함수
def is_within_date_range(comment_date):
    comment_datetime = datetime.strptime(comment_date[:10], "%Y-%m-%d")  # "YYYY-MM-DDTHH:MM:SS" 형식이므로 앞부분만 사용
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    return start_datetime <= comment_datetime <= end_datetime

# 페이지네이션 반복
while True:
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        print(f"❌ 요청 실패: {response.status_code}, {response.text}")
        break

    json_data = response.json()
    comments = json_data.get("result", {}).get("comments", {}).get("body", [])
    has_next = json_data.get("result", {}).get("comments", {}).get("hasNext", False)

    # 날짜 필터링 후 댓글 저장
    for comment in comments:
        comment_date = comment["updatedAt"]
        if is_within_date_range(comment_date):
            all_comments.append([
                comment["id"], 
                comment["message"], 
                comment["updatedAt"], 
                comment["author"]["nickname"]
            ])

    # 현재 수집된 댓글 개수 확인
    current_count = len(all_comments)

    print(f"✅ 수집된 댓글 개수: {current_count}")

    # 더 이상 새로운 댓글이 추가되지 않으면 종료
    if current_count == previous_count:
        print("\n🚀 새로운 댓글이 없으므로 수집을 종료합니다.")
        break

    # 다음 페이지 요청을 위한 commentId 업데이트
    if comments:
        last_comment_id = comments[-1]["id"]  # 가장 마지막 댓글의 ID 사용
        data["commentId"] = last_comment_id  # 다음 요청 시 마지막 댓글 ID 기준으로 요청

    # 현재 댓글 개수를 이전 댓글 개수로 저장
    previous_count = current_count

    # API 요청 간격 조정 (짧은 시간 내 과도한 요청 방지)
    time.sleep(1)

# CSV 파일로 저장
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Comment ID", "Message", "Updated At", "Nickname"])  # CSV 헤더
    writer.writerows(all_comments)

print(f"\n🎉 총 {len(all_comments)}개의 댓글이 {csv_filename} 파일에 저장됨!")
