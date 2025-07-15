import snscrape.modules.twitter as sntwitter  # 트위터 크롤링 모듈
import re  # 텍스트 정제용
import time  # 대기 시간 제어
import random  # 랜덤 대기 시간 설정
import json  # 결과 저장용

# 마약 은어 키워드 목록
drug_slang_keywords = [
    "스노우", "아이스", "백설탕", "밀크", "캔디", "크리스탈", "잔디", "해쉬", "블로우", "스피드",
    "트립", "머쉬룸", "러브 드럭", "돌", "하이", "킥", "블루스", "K-파우더", "에셋", "피트",
    "스톤드", "업", "다운", "롤링", "클라우드", "지니", "블랙 타르", "퍼프", "지그재그",
    "대마", "풀", "뽕", "버섯", "사탕", "빨간약", "약", "약물파티", "펑크", "향정",
    "물약", "빨대", "뿅 됐다", "두루마리", "마약먹방", "약쟁이",
    "얼음", "눈", "물건", "작업물", "꽃", "그린", "고양이 사료", "젤리", "조명",
    "파우더", "설탕", "밀가루", "분말", "고양이약", "케"
]

results = []

# 검색 기간 설정
since = "2025-07-01"
until = "2025-07-15"

# 키워드당 최대 수집 트윗 수
max_results_per_keyword = 30

# 트윗 텍스트 정제 함수 (불필요한 공백 제거)
def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# 키워드별 트윗 수집 루프
for keyword in drug_slang_keywords:
    query = f'"{keyword}" lang:ko since:{since} until:{until}'
    print(f"[INFO] Searching for keyword: {keyword}")

    try:
        count = 0
        for tweet in sntwitter.TwitterSearchScraper(query).get_items():
            if count >= max_results_per_keyword:
                break

            # 수집된 트윗을 구조화하여 저장
            results.append({
                "site": "X",
                "url": tweet.url,
                "author": tweet.user.username,
                "date": tweet.date.isoformat(),
                "content": clean_text(tweet.content),
                "type": "drug",
                "comments": None,
                "title": None
            })

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
print(f"[DONE] Total tweets collected: {len(results)}")

# JSON 파일로 저장
with open("x_drug.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
    print("[SAVE] Results saved to x_drug.json")
