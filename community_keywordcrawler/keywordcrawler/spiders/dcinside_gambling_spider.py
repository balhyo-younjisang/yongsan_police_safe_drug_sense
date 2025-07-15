import time
import scrapy
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By

gambling_slang_keywords = [
    "총알", "칩", "머니", "자금", "탄환",
    "올인", "몰빵", "싹쓸이", "물타기", "역배",
    "블랙잭", "바카라", "룰렛", "슬롯", "포커",
    "따다", "먹다", "잭팟", "히트", "올킬",
    "물리다", "털리다", "쪽박", "깡통",
    "텔방", "놀이터", "토토", "사설", "메이저", "메이저사이트",
    "물주", "VIP", "고래",
    "조진다", "조지다", "조작판", "짜고친다", "구라판", "주작",
    "총판", "총대", "업자", "운영자",
    "배당률", "역배당", "주사위값",
    "삽니다", "팔아요", "충전", "환전", "먹튀",
    "빅뱅", "대판", "쎄게 간다", "풀베팅",
    "한방"
]

class DcinsideGamblingSpiderSpider(scrapy.Spider):
    name = "dcinside_gambling_spider"
    allowed_domains = ["dcinside.com", "gall.dcinside.com", "www.dcinside.com", "search.dcinside.com"]
    start_urls = [f"https://search.dcinside.com/post/q/{gambling_slang}" for gambling_slang in gambling_slang_keywords]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--lang=ko-KR")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0")

        self.driver = webdriver.Chrome(options=chrome_options)

        # 수집 카운터 초기화
        self.keyword_post_counter = {}
        self.max_posts_per_keyword = round(20000 / len(gambling_slang_keywords))

    def closed(self, reason):
        self.driver.quit()

    def parse(self, response):
        # 현재 검색 중인 키워드 추출
        keyword = response.url.split("/q/")[-1]
        self.keyword_post_counter.setdefault(keyword, 0)
        
        for post in response.css("ul.sch_result_list li"):
            if self.keyword_post_counter[keyword] >= self.max_posts_per_keyword:
                print(f"[INFO] Reached limit for keyword: {keyword}")
                break

            post_url = post.css('a::attr(href)').get()
            if post_url:
                self.keyword_post_counter[keyword] += 1
                yield response.follow(post_url, self.parse_post)

    def parse_post(self, response):
        url = response.url
        self.driver.get(url)
        time.sleep(10)

        sel = scrapy.Selector(text=self.driver.page_source)

        # 본문
        content_raw = sel.css("div.write_div *::text").getall()
        content_cleaned = " ".join(t.strip() for t in content_raw if t.strip())

        # 기본 정보
        title = sel.css("span.title_subject::text").get()
        author = sel.css("span.nickname::attr(title)").get()
        date = sel.css("span.gall_date::text").get()

        # 댓글
        all_comments = []
        page = 1
        while True:
            time.sleep(1.5)

            comment_items = self.driver.find_elements(By.CSS_SELECTOR, "ul.cmt_list > li")
            for c in comment_items:
                try:
                    nickname = c.find_element(By.CSS_SELECTOR, "span.gall_writer").get_attribute("data-nick")
                    date_text = c.find_element(By.CSS_SELECTOR, "span.date_time").text
                    comment_text = c.find_element(By.CSS_SELECTOR, "p.usertxt").text.strip()

                    all_comments.append({
                        "author": nickname,
                        "date": date_text,
                        "text": comment_text
                    })
                except Exception:
                    continue

            # 다음 페이지 클릭 (없으면 break)
            try:
                next_btn = self.driver.find_element(By.CSS_SELECTOR, "div.cmt_paging > a.btn_next")
                if "disabled" in next_btn.get_attribute("class"):
                    break
                next_btn.click()
                page += 1
            except:
                break

        yield {
            "site": "dcinside",
            "url": url,
            "title": title,
            "author": author,
            "date": date,
            "content": content_cleaned,
            "comments": all_comments,
            "type": "gambling"
        }