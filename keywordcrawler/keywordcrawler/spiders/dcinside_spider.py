import scrapy
import re
import json
import copy

class DcinsideSpiderSpider(scrapy.Spider):
    name = "dcinside_spider"
    allowed_domains = ["dcinside.com", "gall.dcinside.com", "www.dcinside.com", "search.dcinside.com"]

    # drug_slang_keywords = [
    #     "스노우", "아이스", "백설탕", "밀크", "캔디", "크리스탈", "잔디", "해쉬", "블로우", "스피드",
    #     "트립", "머쉬룸", "러브 드럭", "돌", "하이", "킥", "블루스", "K-파우더", "에셋", "피트",
    #     "스톤드", "업", "다운", "롤링", "클라우드", "지니", "블랙 타르", "퍼프", "지그재그", "차",
    #     "대마", "풀", "뽕", "버섯", "K", "물", "사탕", "빨간약", "약", "약물파티", "펑크", "향정",
    #     "물약", "빨대", "뿅 됐다", "두루마리", "마약먹방", "약쟁이",
    #     "얼음", "눈", "물건", "작업물", "꽃", "그린", "고양이 사료", "젤리", "조명", "별",
    #     "파우더", "설탕", "밀가루", "분말", "고양이약", "케"
    # ]
    # start_urls = [f"https://search.dcinside.com/post/q/{drug_slang}" for drug_slang in drug_slang_keywords]
    start_urls = ['https://search.dcinside.com/post/q/.EC.8B.B1.EA.B8.80.EB.B2.99.EA.B8.80.20.ED.95.A8.EB.B6.80.EB.A1.9C.20.EC.95.94.ED.91.9C.EC.9D.84.20.EC.82.AC.EB.A9.B4.20.EC.95.88.EB.90.98.EB.8A.94.20.EC.9D.B4.EC.9C.A0.2E.2E.2E.2E.2E']

    def parse(self, response):
        for post in response.css("ul.sch_result_list li"):
            post_url = post.css('a::attr(href)').get()
            if post_url is not None:
                yield response.follow(post_url, self.parse_post)
    
    def parse_post(self, response):
        content = response.css("div.write_div *::text").getall()
        clean_content = " ".join(text.strip() for text in content if text.strip())

        comments = []
        
        for comment in response.css("li.ub-content"):
            try:
                author = comment.css('em::text').get()
                date = comment.css('span.date_time::text').get()
                content = comment.css('p.usertxt.ub-word::text').get()

                comments.append({
                    "author": author,
                    "date": date,
                    "content": content
                })
            except:
                continue

        yield {
            "site": "dcinside",
            "url": response.url,
            "title": response.css("span.title_subject::text").get(),
            "author": response.css("span.nickname::attr(title)").get(),
            "date": response.css("span.gall_date::text").get(),
            "content": clean_content,
            "comments": comments
        }      