import datetime
import streamlit as st
import plotly.graph_objects as go
from utils.ui_components import (
    apply_common_styles, show_disclaimer, safe_parse_json,
    show_error, show_other_features, show_share_section,
    track_experience, show_loading_messages,
)
from utils.openai_client import generate_chat, generate_chat_stream, generate_image
from utils.share_card import generate_parallel_card

apply_common_styles()

# --- prompts ---
PARALLEL_SYSTEM_PROMPT = """당신은 평행우주 연구소의 수석 연구원입니다.
사용자의 정보와 분기점 퀴즈 답변을 분석하여 평행우주 속 다른 자아의 프로필을 생성합니다.

규칙:
1. 현재의 나와 극적으로 다르면서도 설득력 있는 평행우주 버전을 만드세요
2. 직업, 성격, 일상, 연봉 모두 구체적으로 작성하세요
3. 괴리율은 현재의 나와 평행우주의 나의 차이 정도 (0-100%)
4. 능력치는 평행우주 직업에 맞게 차등 배분 (각 40-95)
5. 평행우주 이름은 같은 이름의 다른 버전이거나 해당 국가식 이름
6. 일상 묘사는 하루 스케줄 형태로 구체적으로
7. 유머러스하면서도 그럴듯한 톤 유지

응답은 반드시 JSON 형식으로:
{
    "parallel_name": "평행우주 이름",
    "occupation": "직업",
    "country": "거주 국가/도시",
    "annual_income": "연봉 (구체적 금액 + 통화)",
    "personality": "성격 설명 (200-300자)",
    "daily_routine": "하루 일과 (300-400자, 시간대별)",
    "divergence_rate": 72,
    "stats": {
        "카리스마": 85,
        "전문성": 90,
        "체력": 60,
        "운": 75,
        "사교성": 80
    },
    "fun_fact": "평행우주 나에 대한 재미있는 사실 (100-150자)",
    "message_from_parallel": "평행우주의 내가 현재의 나에게 보내는 메시지 (150-200자)",
    "portrait_prompt": "DALL-E용 평행우주 나의 초상화 프롬프트 (영문, 직업/스타일/배경 포함)"
}"""

PORTRAIT_IMAGE_BASE = (
    "professional portrait, cinematic lighting, detailed character art, "
    "vibrant colors, modern style, high quality digital art, "
)

QUIZ_QUESTIONS = [
    {
        "question": "대학 전공을 다시 고른다면?",
        "options": [
            "예술/디자인 — 창작의 길",
            "공학/IT — 기술의 길",
            "경영/경제 — 비즈니스의 길",
            "의학/생명과학 — 치유의 길",
        ],
    },
    {
        "question": "10년 전으로 돌아간다면 가장 먼저?",
        "options": [
            "비트코인을 산다",
            "해외에서 살아본다",
            "운동을 열심히 한다",
            "다른 사람에게 고백한다",
        ],
    },
    {
        "question": "다른 나라에서 태어났다면 어디?",
        "options": [
            "뉴욕 — 꿈의 도시",
            "파리 — 예술의 도시",
            "도쿄 — 기술의 도시",
            "시드니 — 자유의 도시",
        ],
    },
]

# --- session state ---
if "parallel_result" not in st.session_state:
    st.session_state.parallel_result = None
if "parallel_image" not in st.session_state:
    st.session_state.parallel_image = None
if "parallel_story_streamed" not in st.session_state:
    st.session_state.parallel_story_streamed = False

# --- page header ---
st.markdown(
    "<div class='page-header'>"
    "<span class='page-icon float-anim'>🌀</span>"
    "<div class='page-title shimmer-text'>AI 평행우주 연구소</div>"
    "<div class='page-desc'>다른 선택을 했던 나를 만나보세요</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- basic info ---
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.markdown("<h3>📝 기본 정보</h3>", unsafe_allow_html=True)

col_name, col_birth = st.columns(2)
with col_name:
    name = st.text_input("이름 (닉네임)", max_chars=10, placeholder="홍길동", key="parallel_name_input")
with col_birth:
    birthdate = st.date_input(
        "생년월일",
        min_value=datetime.date(1940, 1, 1),
        max_value=datetime.date.today(),
        value=datetime.date(2000, 1, 1),
        key="parallel_birth",
    )
st.markdown("</div>", unsafe_allow_html=True)

# --- branching point quiz ---
st.markdown("")
st.markdown("<h3 style='text-align:center;'>🌀 분기점 퀴즈</h3>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#C8956C;'>3가지 분기점에 답하면 평행우주의 나를 찾아드려요!</p>",
    unsafe_allow_html=True,
)

answers = []
for i, q in enumerate(QUIZ_QUESTIONS):
    st.markdown(
        f"<div class='quiz-card'><span class='quiz-num'>Q{i+1}</span></div>",
        unsafe_allow_html=True,
    )
    answer = st.radio(
        f"Q{i+1}. {q['question']}",
        q["options"],
        key=f"parallel_q{i}",
        index=None,
    )
    answers.append(answer)

st.markdown("")
if st.button("🌀 평행우주 탐색", use_container_width=True, type="primary"):
    if not name or len(name.strip()) < 1:
        st.warning("이름을 입력해주세요!")
    elif None in answers:
        st.warning("모든 질문에 답해주세요! 평행우주 탐색에 필요해요 🙏")
    else:
        quiz_text = "\n".join(
            f"Q{i+1}. {QUIZ_QUESTIONS[i]['question']}\nA: {a}"
            for i, a in enumerate(answers)
        )
        user_prompt = (
            f"[이름]: {name}\n"
            f"[생년월일]: {birthdate.strftime('%Y년 %m월 %d일')}\n\n"
            f"[분기점 퀴즈 답변]:\n{quiz_text}\n\n"
            f"위 정보를 바탕으로 평행우주의 이 사람 프로필을 생성해주세요."
        )

        try:
            show_loading_messages([
                "🌀 차원의 틈을 여는 중...",
                "🔭 평행우주를 탐색하는 중...",
                "📡 다른 차원의 신호를 수신하는 중...",
            ], delay=1.5)

            with st.spinner("🌀 평행우주의 당신을 찾고 있어요..."):
                raw = generate_chat(PARALLEL_SYSTEM_PROMPT, user_prompt, json_mode=True)
                result = safe_parse_json(raw)

            if result is None:
                show_error("평행우주 탐색에 실패했어요. 다시 시도해주세요!")
            else:
                st.session_state.parallel_result = result
                st.session_state.parallel_story_streamed = False

                with st.spinner("🎨 평행우주의 당신을 그리고 있어요..."):
                    try:
                        prompt = PORTRAIT_IMAGE_BASE + result.get("portrait_prompt", "professional portrait")
                        st.session_state.parallel_image = generate_image(prompt)
                    except Exception:
                        st.session_state.parallel_image = None

                track_experience("parallel")
                st.balloons()

        except Exception as e:
            show_error(f"평행우주 탐색 중 문제가 발생했어요: {e}")

# --- result display ---
if st.session_state.parallel_result:
    result = st.session_state.parallel_result

    st.markdown("---")
    st.markdown(
        "<h2 style='text-align:center;' class='slide-up'>🌀 평행우주의 당신을 찾았습니다!</h2>",
        unsafe_allow_html=True,
    )

    # Portrait + basic info
    col_portrait, col_info = st.columns([1, 1])

    with col_portrait:
        if st.session_state.parallel_image:
            st.markdown("<div class='image-frame glow-pulse'>", unsafe_allow_html=True)
            st.image(st.session_state.parallel_image, caption="평행우주의 나", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='background:linear-gradient(145deg, #3D2B1A, #2B1E14); "
                "border:2px solid #8B6914; border-radius:12px; "
                "padding:60px; text-align:center;'>"
                "<span style='font-size:4em;'>🌀</span><br><br>"
                "<span style='color:#C8956C;'>초상화 생성 중 오류 발생</span></div>",
                unsafe_allow_html=True,
            )

    with col_info:
        # Profile card
        divergence = result.get("divergence_rate", 50)
        st.markdown(
            f"<div class='result-card' style='text-align:center;'>"
            f"<p style='color:#C8956C; font-size:1.1em;'>괴리율 {divergence}%</p>"
            f"<h2 style='color:#E8C170 !important; margin:10px 0; font-size:2em !important;'>"
            f"「{result.get('parallel_name', '')}」</h2>"
            f"<p style='color:#F5E6C8;'>{result.get('occupation', '')} | {result.get('country', '')}</p>"
            f"<p style='color:#E8C170; font-weight:bold; font-size:1.3em !important;'>"
            f"💰 {result.get('annual_income', '')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Radar chart
        stats = result.get("stats", {})
        categories = list(stats.keys())
        values = list(stats.values())
        if categories:
            values_closed = values + [values[0]]
            categories_closed = categories + [categories[0]]

            fig = go.Figure(
                data=go.Scatterpolar(
                    r=values_closed,
                    theta=categories_closed,
                    fill="toself",
                    fillcolor="rgba(200, 149, 108, 0.25)",
                    line=dict(color="#E8C170", width=2.5),
                    marker=dict(size=8, color="#E8C170"),
                )
            )
            fig.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor="rgba(200, 149, 108, 0.2)"),
                    angularaxis=dict(gridcolor="rgba(200, 149, 108, 0.2)", linecolor="rgba(200, 149, 108, 0.3)"),
                ),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F5E6C8", size=14),
                margin=dict(l=60, r=60, t=30, b=30),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)

    # Personality (streaming)
    if not st.session_state.parallel_story_streamed:
        personality_prompt = (
            f"다음 평행우주 프로필을 바탕으로 성격과 일상을 더 생생하게 500자 내외로 묘사해주세요:\n"
            f"성격: {result.get('personality', '')}\n일과: {result.get('daily_routine', '')}"
        )
        st.markdown("<div class='result-card slide-up'><h3>🧬 성격 & 일상</h3>", unsafe_allow_html=True)
        st.write_stream(generate_chat_stream(
            "당신은 평행우주 연구소의 연구원입니다. 재미있고 생생하게 묘사합니다.",
            personality_prompt,
        ))
        st.markdown("</div>", unsafe_allow_html=True)
        st.session_state.parallel_story_streamed = True
    else:
        st.markdown(
            f"<div class='result-card slide-up'><h3>🧬 성격 & 일상</h3>"
            f"<p>{result.get('personality', '')}</p>"
            f"<p>{result.get('daily_routine', '')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Fun fact
    st.markdown(
        f"<div class='result-card'>"
        f"<h3>🎲 재미있는 사실</h3>"
        f"<p>{result.get('fun_fact', '')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Message from parallel self
    st.markdown(
        f"<div class='result-card'>"
        f"<h3>💌 평행우주의 내가 보낸 메시지</h3>"
        f"<p style='color:#E8C170 !important; font-style:italic;'>"
        f"\"{result.get('message_from_parallel', '')}\"</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Share
    share_text = (
        f"평행우주의 나: {result.get('parallel_name', '')}\n"
        f"직업: {result.get('occupation', '')} | {result.get('country', '')}\n"
        f"연봉: {result.get('annual_income', '')}\n"
        f"괴리율: {result.get('divergence_rate', '')}%"
    )
    show_share_section("평행우주 결과", share_text)

    card_bytes = generate_parallel_card(result)
    st.download_button(
        "📥 평행우주 카드 다운로드",
        data=card_bytes,
        file_name="parallel_universe.png",
        mime="image/png",
        use_container_width=True,
    )

    # Reset
    st.markdown("")
    if st.button("🔄 다른 분기점으로 다시 탐색"):
        st.session_state.parallel_result = None
        st.session_state.parallel_image = None
        st.session_state.parallel_story_streamed = False
        st.rerun()

show_other_features("parallel")
show_disclaimer()
