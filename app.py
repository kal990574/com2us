import streamlit as st

st.set_page_config(
    page_title="수상한 AI 연구실",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- st.navigation으로 카테고리별 페이지 관리 ---
pg = st.navigation(
    {
        "연구실 로비": [
            st.Page("pages/home.py", title="🏠 수상한 AI 연구실"),
        ],
        "🔬 수상한 실험실": [
            st.Page("pages/wanted_poster.py", title="🔍 수배전단 생성기"),
            st.Page("pages/parallel_universe.py", title="🌀 평행우주 연구소"),
            st.Page("pages/profiling.py", title="🧠 심리 프로파일링"),
            st.Page("pages/mystery_quiz.py", title="❓ 추리 퀴즈"),
        ],
        "📂 봉인된 실험 기록": [
            st.Page("pages/tarot.py", title="🔮 타로마스터"),
            st.Page("pages/face_reader.py", title="👁 관상카페"),
            st.Page("pages/past_life.py", title="⏳ 전생스토리"),
            st.Page("pages/news_comics.py", title="📰 뉴스웹툰"),
        ],
    }
)

pg.run()
