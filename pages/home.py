import datetime
import hashlib
import streamlit as st
from utils.ui_components import apply_common_styles

apply_common_styles()

# ========== hero section ==========
st.markdown(
    "<div class='hero-section hero-particles'>"
    "<div class='hero-stars sparkle'>⚙ 🔍 ⚙ 🔍 ⚙ 🔍 ⚙</div>"
    "<div class='hero-title float-anim'>🔬 수상한 AI 연구실</div>"
    "<div class='hero-subtitle'>AI가 만든 수상한 실험들, 당신도 피험자가 되어보세요</div>"
    "<div class='hero-stars sparkle'>⚙ 🔍 ⚙ 🔍 ⚙ 🔍 ⚙</div>"
    "</div>",
    unsafe_allow_html=True,
)

# ========== daily message ==========
daily_messages = [
    "오늘의 실험은 특별히 위험합니다... 라고 쓰여 있지만 사실 재미있어요 🧪",
    "수상한 AI 연구실에 새로운 실험체가 도착했습니다. 바로 당신! 🔬",
    "연구 일지 #427: 피험자들이 결과를 공유하면 바이럴 확률 300% 증가 📊",
    "긴급 보고: 오늘 들어온 피험자의 프로파일이 특이합니다... 🕵️",
    "실험 주의사항: 결과가 너무 정확하면 소름이 돋을 수 있습니다 ⚡",
    "연구소 공지: 오늘 평행우주 관측 장비가 업그레이드되었습니다 🌀",
    "수배전단 프린터가 과열되었습니다. 인기 폭발 중! 🔥",
    "추리 퀴즈 정답률이 23%... 당신은 맞출 수 있을까요? 🤔",
    "비밀 메모 발견: '이 연구실의 AI는 사람 마음을 너무 잘 읽는다...' 📝",
    "오늘의 실험 추천: 친구와 함께하면 2배 더 수상해집니다 👀",
    "연구원 후기: '프로파일링 결과가 너무 맞아서 무서웠다' — 익명 🫣",
    "평행우주 보고서: 다른 차원의 당신은 지금 뭘 하고 있을까요? 🌌",
]
today = datetime.date.today()
msg_idx = int(hashlib.md5(str(today).encode()).hexdigest(), 16) % len(daily_messages)
daily_msg = daily_messages[msg_idx]

st.markdown(
    f"<div style='text-align:center; padding:15px 20px; margin:10px 0 20px; "
    f"background:linear-gradient(90deg, rgba(200,149,108,0.15), rgba(232,193,112,0.1), rgba(200,149,108,0.15)); "
    f"border-radius:12px; border:1px solid rgba(232,193,112,0.2);'>"
    f"<span style='color:#E8C170; font-size:1.1rem;'>📋 오늘의 연구 일지</span><br>"
    f"<span style='color:#F5E6C8; font-size:1.15rem;'>{daily_msg}</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ========== stats section ==========
st.markdown("")
stat_cols = st.columns(4)
stats = [
    ("4가지", "수상한 실험"),
    ("GPT-4o-mini", "텍스트 + 비전"),
    ("DALL-E 3", "이미지 생성"),
    ("100%", "무료 체험"),
]
for col, (num, label) in zip(stat_cols, stats):
    with col:
        st.markdown(
            f"<div class='stat-card'>"
            f"<div class='stat-number'>{num}</div>"
            f"<div class='stat-label'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("")
st.markdown("---")

# ========== main experiments ==========
st.markdown("<div class='category-header'>🔬 수상한 실험실</div>", unsafe_allow_html=True)

cols = st.columns(2)

with cols[0]:
    st.markdown(
        "<div class='feature-card'>"
        "<div class='emoji'>🔍</div>"
        "<div class='title'>수배전단 생성기</div>"
        "<div class='desc'>사진 한 장이면 AI가 당신의 수배전단을 만들어드려요. "
        "죄목, 현상금, 위험등급까지!</div>"
        "<div class='tag'>Vision + GPT + DALL-E</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("🔍 수배전단 만들기", key="btn_wanted", use_container_width=True):
        st.switch_page("pages/wanted_poster.py")

with cols[1]:
    st.markdown(
        "<div class='feature-card'>"
        "<div class='emoji'>🌀</div>"
        "<div class='title'>평행우주 연구소</div>"
        "<div class='desc'>다른 선택을 했다면? AI가 평행우주 속 "
        "당신의 직업, 연봉, 일상을 알려드려요</div>"
        "<div class='tag'>GPT + DALL-E</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("🌀 평행우주 탐색", key="btn_parallel", use_container_width=True):
        st.switch_page("pages/parallel_universe.py")

cols2 = st.columns(2)

with cols2[0]:
    st.markdown(
        "<div class='feature-card'>"
        "<div class='emoji'>🧠</div>"
        "<div class='title'>심리 프로파일링</div>"
        "<div class='desc'>극한선택 퀴즈로 FBI식 심리 보고서를 받아보세요. "
        "위험등급부터 약점까지!</div>"
        "<div class='tag'>GPT + DALL-E</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("🧠 프로파일링 받기", key="btn_profiling", use_container_width=True):
        st.switch_page("pages/profiling.py")

with cols2[1]:
    st.markdown(
        "<div class='feature-card'>"
        "<div class='emoji'>🕵️</div>"
        "<div class='title'>추리 퀴즈</div>"
        "<div class='desc'>AI가 출제하는 미스터리 사건! "
        "단서를 모아 범인을 찾아보세요</div>"
        "<div class='tag'>GPT + DALL-E</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("🕵️ 추리 시작", key="btn_quiz", use_container_width=True):
        st.switch_page("pages/mystery_quiz.py")

st.markdown("")
st.markdown("---")

# ========== legacy section ==========
st.markdown("<div class='category-header'>📂 봉인된 실험 기록</div>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#8B7355; font-size:1em;'>"
    "이전에 진행되었던 실험들입니다. 아직 체험해볼 수 있어요!</p>",
    unsafe_allow_html=True,
)

legacy_cols = st.columns(4)
legacy_items = [
    ("🔮", "타로마스터", "pages/tarot.py", "btn_tarot"),
    ("👁️", "관상카페", "pages/face_reader.py", "btn_face"),
    ("🌀", "전생스토리", "pages/past_life.py", "btn_past"),
    ("📰", "뉴스웹툰", "pages/news_comics.py", "btn_news"),
]
for col, (icon, name, page, key) in zip(legacy_cols, legacy_items):
    with col:
        st.markdown(
            f"<div style='text-align:center; padding:15px; "
            f"background:linear-gradient(145deg, rgba(61,43,26,0.5), rgba(43,30,20,0.4)); "
            f"border:1px solid rgba(200,149,108,0.15); border-radius:12px;'>"
            f"<div style='font-size:2.5em;'>{icon}</div>"
            f"<div style='color:#A08060; font-size:1.1em; margin-top:8px;'>{name}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.button(f"{icon} {name}", key=key, use_container_width=True):
            st.switch_page(page)

st.markdown("")
st.markdown("---")

# ========== how to use ==========
st.markdown("<h3 style='text-align:center; margin-bottom:20px;'>✨ 이용 방법</h3>", unsafe_allow_html=True)

step_cols = st.columns(4)
steps = [
    ("1", "🎯 실험 선택", "원하는 실험을 골라주세요"),
    ("2", "📝 정보 입력", "사진, 퀴즈, 난이도 등 입력"),
    ("3", "🤖 AI 분석", "GPT가 분석하고 DALL-E가 그려요"),
    ("4", "🎉 결과 확인", "수상한 결과를 친구와 공유!"),
]
for col, (num, title, desc) in zip(step_cols, steps):
    with col:
        st.markdown(
            f"<div class='step-item'>"
            f"<div class='step-num'>{num}</div>"
            f"<div style='color:#E8C170; font-weight:bold; margin-bottom:5px;'>{title}</div>"
            f"<div class='step-text'>{desc}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("")
st.markdown("---")

# ========== tech stack ==========
st.markdown("<h3 style='text-align:center; margin-bottom:20px;'>🛠️ 사용 기술</h3>", unsafe_allow_html=True)

tech_cols = st.columns(3)
techs = [
    ("🧠", "OpenAI GPT-4o-mini", "자연어 이해와 창의적 텍스트 생성"),
    ("🎨", "DALL-E 3", "고품질 AI 이미지 생성"),
    ("🌐", "Streamlit", "인터랙티브 웹 애플리케이션"),
]
for col, (icon, name, desc) in zip(tech_cols, techs):
    with col:
        st.markdown(
            f"<div style='text-align:center; padding:15px;'>"
            f"<div style='font-size:2.5em;'>{icon}</div>"
            f"<div style='color:#E8C170; font-weight:bold; margin:8px 0;'>{name}</div>"
            f"<div style='color:#A08060; font-size:0.95em;'>{desc}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("")
st.markdown("---")

# ========== footer ==========
st.markdown(
    "<p style='text-align:center; color:#8B7355; font-size:0.9em; margin-bottom:5px;'>"
    "⚠️ 수상한 AI 연구실은 엔터테인먼트 목적으로 제작되었습니다.<br>"
    "결과는 AI가 생성한 것으로 실제와 무관합니다. 재미로만 즐겨주세요!</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#6B5B45; font-size:0.85em;'>"
    "Made with ❤️ & AI | Powered by OpenAI GPT-4o-mini & DALL-E 3</p>",
    unsafe_allow_html=True,
)
