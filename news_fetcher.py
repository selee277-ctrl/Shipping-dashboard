import feedparser
import urllib.parse
from datetime import datetime
from time import mktime
from difflib import SequenceMatcher
from deep_translator import GoogleTranslator

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

def fetch_google_news_en(query, num_results=10):
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"
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

def _translate_title(title):
    """영문 제목을 한국어로 번역"""
    try:
        # 출처 부분 분리 (- TradeWinds 등)
        parts = title.rsplit(" - ", 1)
        main_title = parts[0]
        source = parts[1] if len(parts) > 1 else ""

        translated = GoogleTranslator(source='en', target='ko').translate(main_title)

        if source:
            return f"{translated} - {source}"
        return translated
    except:
        return title

def _is_similar(title1, title2, threshold=0.45):
    """두 제목이 유사한지 판단"""
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
        if a["title"] in seen_titles:
            continue
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

# 공통 제외 키워드 (주식 관련)
STOCK_EXCLUDE = ["주가", "주식", "특징주", "테마주", "매수", "매도",
                 "배당", "고배당", "시가총액", "코스피", "코스닥", "종목"]

def fetch_shipping_news():
    queries = ["해운", "해운시황", "BDI", "해운 물동량", "벌크선", "해운 선사", "벙커링", "케이프사이즈", "capesize", "수에즈운하", "파나마운하"]
    all_articles = []
    for q in queries:
        all_articles.extend(fetch_google_news(q, num_results=5))

    exclude = STOCK_EXCLUDE + ["컨테이너", "컨테이너선", "컨테이너 운임", "SCFI", "CCFI", "KCCI",
                                "샴푸", "화장품", "문화유산", "선사시대", "국악", "동아리",
                                "머릿결", "옥천", "가락"]
    all_articles = _filter_articles(all_articles, exclude_keywords=exclude)

    return _deduplicate(all_articles)

def fetch_tradewinds_news():
    queries = ["site:tradewindsnews.com shipping", "site:tradewindsnews.com tanker", "site:tradewindsnews.com bulker"]
    all_articles = []
    for q in queries:
        all_articles.extend(fetch_google_news_en(q, num_results=10))

    # 중복 제거 후 번역
    unique_articles = _deduplicate(all_articles, max_count=15)

    # 제목 번역
    for a in unique_articles:
        a["title_kr"] = _translate_title(a["title"])

    return unique_articles

def fetch_lng_news():
    queries = ["LNG", "LNG 가격", "천연가스", "LNG선", "LNG 수입"]
    all_articles = []
    for q in queries:
        all_articles.extend(fetch_google_news(q, num_results=5))

    all_articles = _filter_articles(all_articles, exclude_keywords=STOCK_EXCLUDE)

    return _deduplicate(all_articles)

def fetch_oil_news():
    queries = ["국제유가", "유가", "WTI", "브렌트유", "OPEC", "원유"]
    all_articles = []
    for q in queries:
        all_articles.extend(fetch_google_news(q, num_results=5))

    all_articles = _filter_articles(all_articles, exclude_keywords=STOCK_EXCLUDE)

    return _deduplicate(all_articles)
