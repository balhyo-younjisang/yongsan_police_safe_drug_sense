import time
import scrapy
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By

drug_slang_keywords = [
    "스노우", "아이스", "백설탕", "밀크", "캔디", "크리스탈", "잔디", "해쉬", "블로우", "스피드",
    "트립", "머쉬룸", "러브 드럭", "돌", "하이", "킥", "블루스", "K-파우더", "에셋", "피트",
    "스톤드", "업", "다운", "롤링", "클라우드", "지니", "블랙 타르", "퍼프", "지그재그", "차",
    "대마", "풀", "뽕", "버섯", "K", "물", "사탕", "빨간약", "약", "약물파티", "펑크", "향정",
    "물약", "빨대", "두루마리", "마약먹방", "약쟁이",
    "얼음", "눈", "물건", "작업물", "꽃", "그린", "고양이 사료", "젤리", "조명", "별",
    "파우더", "설탕", "밀가루", "분말", "고양이약", "케"
]

class DcinsideSpiderSpider(scrapy.Spider):
    name = "dcinside_drug_spider"
    allowed_domains = ["dcinside.com", "gall.dcinside.com", "www.dcinside.com", "search.dcinside.com"]
    start_urls = [f"https://search.dcinside.com/post/q/{drug_slang}" for drug_slang in drug_slang_keywords]
    
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
        self.max_posts_per_keyword = round(20000 / len(drug_slang_keywords))

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
            "type": "drug"
        }