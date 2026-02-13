import streamlit as st
import plotly.graph_objects as go
from utils.ui_components import (
    apply_common_styles, show_disclaimer, safe_parse_json,
    show_error, show_other_features, show_share_section,
    track_experience, show_loading_messages,
)
from utils.openai_client import generate_chat, generate_chat_stream, generate_image
from utils.share_card import generate_profiling_card

apply_common_styles()

# --- prompts ---
PROFILING_SYSTEM_PROMPT = """당신은 FBI 행동분석팀(BAU)의 수석 프로파일러입니다.
사용자의 극한선택 퀴즈 답변을 분석하여 심리 프로파일 보고서를 작성합니다.

규칙:
1. 유형명은 인상적이고 기억에 남는 것으로 (예: "잠든 화산형", "미소 뒤의 전략가")
2. 위험등급은 S/A/B/C/D (S가 가장 위험). 재미있는 기준으로!
3. 능력치 6가지를 40-95 사이로 차등 배분
4. 약점은 귀여운 약점으로 (예: "배고프면 판단력 급감", "고양이 앞에서 무력화")
5. 최적 파트너 유형도 재미있게 표현
6. 전체적으로 FBI 보고서 톤이지만 유머러스하게
7. 한 줄 프로파일은 이 사람을 한 문장으로 정의하는 것

응답은 반드시 JSON 형식으로:
{
    "type_name": "유형명",
    "one_liner": "한 줄 프로파일 (이 사람을 한 문장으로)",
    "danger_level": "위험등급 (S~D)",
    "danger_reason": "위험등급 이유 (재미있게)",
    "abilities": {
        "분석력": 85,
        "직감": 70,
        "리더십": 60,
        "적응력": 90,
        "인내력": 75,
        "매력": 80
    },
    "strengths": ["강점1", "강점2", "강점3"],
    "weakness": "치명적 약점 (귀여운 것으로)",
    "partner_type": "최적 파트너 유형",
    "secret_personality": "겉으로 드러나지 않는 숨겨진 성격 (200-300자)",
    "recommended_role": "추천 역할 (영화/드라마에서 맡을 법한 역할)",
    "portrait_prompt": "DALL-E용 이 유형의 캐릭터 일러스트 프롬프트 (영문, 성격과 분위기 반영)"
}"""

PORTRAIT_IMAGE_BASE = (
    "character portrait illustration, dramatic moody lighting, "
    "psychological thriller style, detailed digital art, "
    "cinematic composition, mystery atmosphere, "
)

QUIZ_QUESTIONS = [
    {
        "question": "무인도에 딱 하나만 가져갈 수 있다면?",
        "options": [
            "🔪 만능 서바이벌 나이프",
            "📚 1000권이 담긴 전자책",
            "📱 위성 전화기 (하루 10분 통화 가능)",
            "🎵 좋아하는 음악이 담긴 MP3",
        ],
    },
    {
        "question": "범인을 목격했습니다! 당신의 행동은?",
        "options": [
            "즉시 경찰에 신고한다",
            "몰래 뒤를 밟아 정보를 모은다",
            "못 본 척 지나간다 (위험하니까)",
            "주변 사람들과 함께 범인을 제압한다",
        ],
    },
    {
        "question": "타임머신이 있다면?",
        "options": [
            "과거로 가서 역사적 사건을 목격한다",
            "미래로 가서 로또 번호를 확인한다",
            "과거의 나에게 조언을 한다",
            "타임머신을 분해해서 원리를 파악한다",
        ],
    },
    {
        "question": "갑자기 초능력이 생겼습니다! 어떤 능력?",
        "options": [
            "🧠 독심술 — 남의 생각을 읽는다",
            "⏰ 시간 정지 — 시간을 멈출 수 있다",
            "👻 투명화 — 투명인간이 된다",
            "🔮 예지력 — 미래를 볼 수 있다",
        ],
    },
    {
        "question": "좀비 아포칼립스! 당신의 생존 전략은?",
        "options": [
            "높은 건물에 올라가 거점을 만든다",
            "마트를 점거하고 식량을 확보한다",
            "차를 타고 인적 없는 곳으로 도망간다",
            "생존자들을 모아 팀을 구성한다",
        ],
    },
    {
        "question": "평생 하나만 먹어야 한다면?",
        "options": [
            "🍕 피자 — 토핑은 매번 바꿀 수 있음",
            "🍜 라면 — 종류는 자유",
            "🍣 초밥 — 네타는 자유",
            "🥗 샐러드 — 재료는 자유",
        ],
    },
]

# --- session state ---
if "profiling_result" not in st.session_state:
    st.session_state.profiling_result = None
if "profiling_image" not in st.session_state:
    st.session_state.profiling_image = None
if "profiling_streamed" not in st.session_state:
    st.session_state.profiling_streamed = False

# --- page header ---
st.markdown(
    "<div class='page-header'>"
    "<span class='page-icon float-anim'>🧠</span>"
    "<div class='page-title shimmer-text'>AI 심리 프로파일링</div>"
    "<div class='page-desc'>FBI 행동분석팀이 당신을 분석합니다</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- quiz section ---
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.markdown("<h3>🧠 극한선택 퀴즈</h3>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#C8956C;'>6가지 극한선택에 답하면 당신의 심리를 프로파일링합니다!</p>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

answers = []
for i, q in enumerate(QUIZ_QUESTIONS):
    st.markdown(
        f"<div class='quiz-card'><span class='quiz-num'>Q{i+1}</span></div>",
        unsafe_allow_html=True,
    )
    answer = st.radio(
        f"Q{i+1}. {q['question']}",
        q["options"],
        key=f"profiling_q{i}",
        index=None,
    )
    answers.append(answer)

st.markdown("")
if st.button("🧠 프로파일링 시작", use_container_width=True, type="primary"):
    if None in answers:
        st.warning("모든 질문에 답해주세요! 정확한 프로파일링에 필요해요 🙏")
    else:
        quiz_text = "\n".join(
            f"Q{i+1}. {QUIZ_QUESTIONS[i]['question']}\nA: {a}"
            for i, a in enumerate(answers)
        )
        user_prompt = (
            f"[극한선택 퀴즈 답변]:\n{quiz_text}\n\n"
            f"위 답변을 분석하여 심리 프로파일 보고서를 작성해주세요."
        )

        try:
            show_loading_messages([
                "🧠 행동 패턴을 분석하는 중...",
                "📊 심리 프로파일을 구축하는 중...",
                "🔍 숨겨진 성격을 해독하는 중...",
            ], delay=1.5)

            with st.spinner("🧠 심리 프로파일을 작성하고 있어요..."):
                raw = generate_chat(PROFILING_SYSTEM_PROMPT, user_prompt, json_mode=True)
                result = safe_parse_json(raw)

            if result is None:
                show_error("프로파일링에 실패했어요. 다시 시도해주세요!")
            else:
                st.session_state.profiling_result = result
                st.session_state.profiling_streamed = False

                with st.spinner("🎨 프로파일 캐릭터를 그리고 있어요..."):
                    try:
                        prompt = PORTRAIT_IMAGE_BASE + result.get("portrait_prompt", "mystery character")
                        st.session_state.profiling_image = generate_image(prompt)
                    except Exception:
                        st.session_state.profiling_image = None

                track_experience("profiling")
                st.balloons()

        except Exception as e:
            show_error(f"프로파일링 중 문제가 발생했어요: {e}")

# --- result display ---
if st.session_state.profiling_result:
    result = st.session_state.profiling_result

    st.markdown("---")
    st.markdown(
        "<h2 style='text-align:center;' class='slide-up'>🧠 FBI 심리 프로파일 보고서</h2>",
        unsafe_allow_html=True,
    )

    # Portrait + type info
    col_portrait, col_info = st.columns([1, 1])

    with col_portrait:
        if st.session_state.profiling_image:
            st.markdown("<div class='image-frame glow-pulse'>", unsafe_allow_html=True)
            st.image(st.session_state.profiling_image, caption="프로파일 캐릭터", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='background:linear-gradient(145deg, #3D2B1A, #2B1E14); "
                "border:2px solid #8B6914; border-radius:12px; "
                "padding:60px; text-align:center;'>"
                "<span style='font-size:4em;'>🧠</span><br><br>"
                "<span style='color:#C8956C;'>캐릭터 생성 중 오류 발생</span></div>",
                unsafe_allow_html=True,
            )

    with col_info:
        # Type name and danger level
        st.markdown(
            f"<div class='result-card' style='text-align:center;'>"
            f"<p style='color:#C8956C; font-size:1.1em;'>SUBJECT PROFILE</p>"
            f"<h2 style='color:#E8C170 !important; margin:10px 0; font-size:2em !important;'>"
            f"「{result.get('type_name', '')}」</h2>"
            f"<p style='color:#F5E6C8; font-style:italic;'>\"{result.get('one_liner', '')}\"</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Danger level
        danger_cols = st.columns(2)
        with danger_cols[0]:
            st.markdown(
                f"<div class='score-card'>"
                f"<div class='score-label'>위험등급</div>"
                f"<div class='score-value'>{result.get('danger_level', '')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with danger_cols[1]:
            st.markdown(
                f"<div class='score-card'>"
                f"<div class='score-label'>추천 역할</div>"
                f"<div class='score-value' style='font-size:1.3em !important;'>{result.get('recommended_role', '')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Danger reason
    st.markdown(
        f"<div class='result-card'>"
        f"<h3>⚠️ 위험등급 판정 사유</h3>"
        f"<p>{result.get('danger_reason', '')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Abilities radar chart
    abilities = result.get("abilities", {})
    if abilities:
        st.markdown("<div class='result-card'><h3>📊 능력치 분석</h3>", unsafe_allow_html=True)
        categories = list(abilities.keys())
        values = list(abilities.values())
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
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Strengths
    st.markdown("<div class='result-card'><h3>💪 강점</h3>", unsafe_allow_html=True)
    strengths = result.get("strengths", [])
    for s in strengths:
        st.markdown(f"- {s}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Weakness and partner
    weak_cols = st.columns(2)
    with weak_cols[0]:
        st.markdown(
            f"<div class='result-card'>"
            f"<h3>💔 치명적 약점</h3>"
            f"<p style='font-size:1.3em !important;'>{result.get('weakness', '')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with weak_cols[1]:
        st.markdown(
            f"<div class='result-card'>"
            f"<h3>💕 최적 파트너</h3>"
            f"<p style='font-size:1.3em !important; color:#E8C170 !important;'>{result.get('partner_type', '')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Secret personality (streaming)
    if not st.session_state.profiling_streamed:
        secret_prompt = (
            f"다음 숨겨진 성격 분석을 FBI 프로파일러 톤으로 더 상세하게 400자 내외로 풀어주세요:\n"
            f"{result.get('secret_personality', '')}"
        )
        st.markdown("<div class='result-card slide-up'><h3>🔍 숨겨진 성격 분석</h3>", unsafe_allow_html=True)
        st.write_stream(generate_chat_stream(
            "당신은 FBI 행동분석팀 프로파일러입니다. 전문적이면서도 흥미로운 톤으로 분석합니다.",
            secret_prompt,
        ))
        st.markdown("</div>", unsafe_allow_html=True)
        st.session_state.profiling_streamed = True
    else:
        st.markdown(
            f"<div class='result-card slide-up'><h3>🔍 숨겨진 성격 분석</h3>"
            f"<p>{result.get('secret_personality', '')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Share
    share_text = (
        f"유형: {result.get('type_name', '')}\n"
        f"위험등급: {result.get('danger_level', '')}\n"
        f"약점: {result.get('weakness', '')}\n"
        f"파트너: {result.get('partner_type', '')}"
    )
    show_share_section("심리 프로파일링 결과", share_text)

    card_bytes = generate_profiling_card(result)
    st.download_button(
        "📥 프로파일 카드 다운로드",
        data=card_bytes,
        file_name="profiling_result.png",
        mime="image/png",
        use_container_width=True,
    )

    # Reset
    st.markdown("")
    if st.button("🔄 다시 프로파일링하기"):
        st.session_state.profiling_result = None
        st.session_state.profiling_image = None
        st.session_state.profiling_streamed = False
        st.rerun()

show_other_features("profiling")
show_disclaimer()
