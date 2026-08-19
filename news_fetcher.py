import feedparser
import urllib.parse
from datetime import datetime
from time import mktime

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

def _deduplicate(articles, max_count=15):
    seen = set()
    unique = []
    for a in articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique.append(a)
    unique.sort(key=lambda x: x["sort_key"], reverse=True)
    return unique[:max_count]

def fetch_shipping_news():
    queries = ["해운", "해운시황", "컨테이너 운임", "BDI", "해운 물동량", "벌크선"]
    all_articles = []
    for q in queries:
        all_articles.extend(fetch_google_news(q, num_results=5))
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
