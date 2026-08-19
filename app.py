import streamlit as st
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from news_fetcher import fetch_shipping_news, fetch_lng_news, fetch_oil_news
from config import CACHE_TTL_SECONDS, REFRESH_INTERVAL_MINUTES

st.set_page_config(page_title="해운·에너지 대시보드", page_icon=":ship:", layout="wide")

if "scheduler_started" not in st.session_state:
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: st.cache_data.clear(), trigger=IntervalTrigger(minutes=REFRESH_INTERVAL_MINUTES), id="auto_refresh")
    scheduler.start()
    st.session_state.scheduler_started = True

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_news():
    return fetch_shipping_news(), fetch_lng_news(), fetch_oil_news()

st.title("🚢 해운·에너지 뉴스 대시보드")
st.caption(f"📅 {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')} 기준 | ⏰ {REFRESH_INTERVAL_MINUTES}분 자동 갱신")

with st.spinner("📡 최신 데이터를 불러오는 중..."):
    shipping_news, lng_news, oil_news = load_news()

# ===== 디버깅용 (확인 후 삭제) =====
st.write("### 디버깅: 정렬 확인")
for a in shipping_news[:5]:
    st.write(f"{a['published']} → published_dt: {a.get('published_dt', 'MISSING')}")
# ===== 디버깅 끝 =====

tab1, tab2, tab3, tab4 = st.tabs(["📋 요약", "🚢 해운시황", "🛢️ 국제유가", "🔥 LNG"])

with tab1:
    st.subheader("📰 카테고리별 TOP 3")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🚢 해운시황**")
        for i, a in enumerate(shipping_news[:3], 1):
            st.markdown(f"{i}. [{a['title']}]({a['link']})")
    with col2:
        st.markdown("**🛢️ 국제유가**")
        for i, a in enumerate(oil_news[:3], 1):
            st.markdown(f"{i}. [{a['title']}]({a['link']})")
    with col3:
        st.markdown("**🔥 LNG**")
        for i, a in enumerate(lng_news[:3], 1):
            st.markdown(f"{i}. [{a['title']}]({a['link']})")

with tab2:
    st.header("📌 해운시황 주요 헤드라인")
    for i, a in enumerate(shipping_news[:5], 1):
        st.markdown(f"{i}. {a['title']} — *{a['source']}*")
    st.divider()
    st.header("📰 전체 뉴스")
    for a in shipping_news:
        st.markdown(f"#### [{a['title']}]({a['link']})")
        st.caption(f"📰 {a['source']} | 🕔 {a['published']}")
        st.divider()

with tab3:
    st.header("📌 국제유가 주요 헤드라인")
    for i, a in enumerate(oil_news[:5], 1):
        st.markdown(f"{i}. {a['title']} — *{a['source']}*")
    st.divider()
    st.header("📰 전체 뉴스")
    for a in oil_news:
        st.markdown(f"#### [{a['title']}]({a['link']})")
        st.caption(f"📰 {a['source']} | 🕔 {a['published']}")
        st.divider()

with tab4:
    st.header("📌 LNG 시장 주요 헤드라인")
    for i, a in enumerate(lng_news[:5], 1):
        st.markdown(f"{i}. {a['title']} — *{a['source']}*")
    st.divider()
    st.header("📰 전체 뉴스")
    for a in lng_news:
        st.markdown(f"#### [{a['title']}]({a['link']})")
        st.caption(f"📰 {a['source']} | 🕔 {a['published']}")
        st.divider()

with st.sidebar:
    st.header("⚙️ 설정")
    if st.button("🔄 수동 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.success("✅ 자동 갱신 활성화")
    st.caption(f"• 뉴스: {REFRESH_INTERVAL_MINUTES}분 간격")
