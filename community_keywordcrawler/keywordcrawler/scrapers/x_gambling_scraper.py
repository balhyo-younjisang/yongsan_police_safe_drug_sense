import snscrape.modules.twitter as sntwitter
import re
import time
import random
import pymongo

# MongoDB 설정
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["safedrugsense_crawl_data"]
collection = db["x_gambling"]

# 도박 은어 키워드 목록
gambling_slang_keywords = [
    "총알", "칩", "머니", "자금", "탄환",
    "올인", "몰빵", "싹쓸이", "물타기", "역배",
    "블랙잭", "바카라", "룰렛", "슬롯", "포커",
    "따다", "먹다", "잭팟", "히트", "올킬",
    "물리다", "털리다", "쪽박", "깡통",
    "텔방", "놀이터", "토토", "사설", "메이저",
    "물주", "VIP", "고래", "주작",
    "총판", "총대", "업자", "운영자",
    "배당률", "역배당", "주사위값",
    "삽니다", "팔아요", "충전", "환전", "먹튀",
    "빅뱅", "대판", "쎄게 간다", "풀베팅",
    "한방"
]

# 검색 기간 설정
since = "2025-07-01"
until = "2025-07-15"

# 키워드당 최대 수집 트윗 수
max_results_per_keyword = 30

# 트윗 텍스트 정제 함수
def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

total_collected = 0

# 키워드별 트윗 수집 루프
for keyword in gambling_slang_keywords:
    query = f'"{keyword}" lang:ko since:{since} until:{until}'
    print(f"[INFO] Searching for keyword: {keyword}")

    try:
        count = 0
        for tweet in sntwitter.TwitterSearchScraper(query).get_items():
            if count >= max_results_per_keyword:
                break

            # 수집된 트윗을 MongoDB에 바로 저장
            tweet_data = {
                "site": "X",
                "url": tweet.url,
                "author": tweet.user.username,
                "date": tweet.date.isoformat(),
                "content": clean_text(tweet.content),
                "type": "gambling",
                "comments": None,
                "title": None
            }
            collection.insert_one(tweet_data)
            total_collected += 1
            count += 1

        # IP 차단 방지를 위한 랜덤 대기
        sleep_time = random.uniform(1.5, 4.0)
        print(f"[WAIT] Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

    except Exception as e:
        print(f"[ERROR] Error occurred while processing keyword: {keyword}")
        print(f"[DETAIL] {e}")
        print("[WAIT] Sleeping for 10 seconds before retry...")
        time.sleep(10)

# 수집 완료 후 출력
print(f"[DONE] Total tweets collected and saved to MongoDB: {total_collected}")

# MongoDB 연결 종료
client.close()

