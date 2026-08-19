import feedparser
import urllib.parse
from datetime import datetime
from time import mktime
from difflib import SequenceMatcher

def fetch_google_news(query, num_results=10):
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:num_results]:
        pub_parsed = entry.get("published_parsed")
        if pub_parsed:
            pub_dt_str = datetime.fromtimestamp(mktime(pub_parsed)).strftime("%Y%m%d%H%M%S")
        else:
            pub_dt_str = "00000000000000"

        articles.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "sort_key": pub_dt_str,
            "source": entry.get("source", {}).get("title", ""),
        })
    return articles

def _is_similar(title1, title2, threshold=0.45):
    """두 제목이 유사한지 판단"""
    # 출처 부분 제거 (- 뒤의 언론사명)
    t1 = title1.split(" - ")[0].strip()
    t2 = title2.split(" - ")[0].strip()
    return SequenceMatcher(None, t1, t2).ratio() > threshold

def _filter_articles(articles, exclude_keywords=None):
    """제외 키워드가 제목에 포함된 기사를 필터링"""
    if not exclude_keywords:
        return articles
    filtered = []
    for a in articles:
        title = a["title"]
        if not any(kw in title for kw in exclude_keywords):
            filtered.append(a)
    return filtered

def _deduplicate(articles, max_count=15):
    seen_titles = []
    unique = []
    for a in articles:
        # 완전 동일 제목 제거
        if a["title"] in [t for t in seen_titles]:
            continue
        # 유사 제목 제거
        is_dup = False
        for existing_title in seen_titles:
            if _is_similar(a["title"], existing_title):
                is_dup = True
                break
        if not is_dup:
            seen_titles.append(a["title"])
            unique.append(a)
    unique.sort(key=lambda x: x["sort_key"], reverse=True)
    return unique[:max_count]

def fetch_shipping_news():
    queries = ["해운", "해운시황", "BDI", "해운 물동량", "벌크선"]
    all_articles = []
    for q in queries:
        all_articles.extend(fetch_google_news(q, num_results=5))

    exclude = ["주가", "주식", "특징주", "테마주", "급등", "급락", "매수", "매도",
               "배당", "고배당", "시가총액", "코스피", "코스닥", "종목",
               "컨테이너", "컨테이너선", "컨테이너 운임", "SCFI", "CCFI", "KCCI"]
    all_articles = _filter_articles(all_articles, exclude_keywords=exclude)

    return _deduplicate(all_articles)

def fetch_lng_news():
    queries = ["LNG", "LNG 가격", "천연가스", "LNG선", "LNG 수입"]
    all_articles = []
    for q in queries:
        all_articles.extend(fetch_google_news(q, num_results=5))
    return _deduplicate(all_articles)

def fetch_oil_news():
    queries = ["국제유가", "유가", "WTI", "브렌트유", "OPEC", "원유"]
    all_articles = []
    for q in queries:
        all_articles.extend(fetch_google_news(q, num_results=5))
    return _deduplicate(all_articles)
