import datetime
import streamlit as st
import plotly.graph_objects as go
from utils.ui_components import (apply_common_styles, show_disclaimer, safe_parse_json,
    show_error, show_other_features_legacy, show_share_section,
    track_experience, show_loading_messages)
from utils.openai_client import generate_chat, generate_chat_stream, generate_image
from utils.share_card import generate_pastlife_card

apply_common_styles()

# --- 프롬프트 ---
PASTLIFE_SYSTEM_PROMPT = """당신은 전생을 읽어내는 신비로운 영매입니다.
이름: "시간의 방랑자"
말투: 서사적이고 드라마틱한 톤. 소설처럼 이야기를 풀어가세요.

규칙:
1. 생년월일의 숫자와 퀴즈 답변을 조합하여 전생을 설정하세요
2. 전생 시대는 실제 역사적 시대/국가에서 선택하세요
3. 전생 이야기는 기승전결이 있는 미니 서사로 작성하세요
4. 전생의 특징이 현생의 성격/취향과 연결되는 포인트를 만들어주세요
5. 능력치는 전생 직업에 맞게 차등 배분하세요 (각 항목 40-95)
6. 전생 이름은 시대/국가에 맞는 이름으로 지어주세요

응답은 반드시 JSON 형식으로:
{
  "era": "시대",
  "country": "국가/지역",
  "location": "구체적 장소",
  "past_name": "전생 이름",
  "occupation": "전생 직업",
  "story": "전생 스토리 (500-800자, 소설체)",
  "stats": {
    "strength": 75,
    "intelligence": 85,
    "charisma": 60,
    "luck": 70,
    "creativity": 90,
    "resilience": 80
  },
  "connection_to_present": "현생과의 연결 포인트 (200-300자)",
  "portrait_prompt": "DALL-E용 전생 초상화 프롬프트 (영문, 시대/의상/배경 포함)"
}"""

PORTRAIT_IMAGE_BASE = (
    "historical portrait painting, detailed oil painting style, "
    "dramatic lighting, cinematic composition, rich colors, museum quality art, "
)

QUIZ_QUESTIONS = [
    {
        "question": "낯선 곳에 홀로 떨어졌습니다. 당신의 첫 행동은?",
        "options": [
            "높은 곳에 올라가 주변을 살핀다",
            "근처 사람을 찾아 말을 건다",
            "조용히 숨어서 상황을 관찰한다",
            "일단 먹을 것부터 찾는다",
        ],
    },
    {
        "question": "가장 마음이 끌리는 시대는?",
        "options": [
            "고대 이집트 — 피라미드와 파라오의 시대",
            "중세 유럽 — 기사와 성의 시대",
            "조선시대 — 선비와 한옥의 시대",
            "르네상스 — 예술과 발명의 시대",
        ],
    },
    {
        "question": "위기 상황! 마을이 위험에 처했습니다. 당신은?",
        "options": [
            "직접 앞장서서 싸운다",
            "사람들을 모아 전략을 짠다",
            "약초를 모아 부상자를 돌본다",
            "비밀 통로를 찾아 사람들을 대피시킨다",
        ],
    },
    {
        "question": "당신에게 가장 소중한 가치는?",
        "options": [
            "명예와 의리",
            "지식과 진리",
            "사랑과 아름다움",
            "자유와 모험",
        ],
    },
    {
        "question": "자주 꾸는 꿈의 분위기는?",
        "options": [
            "웅장한 궁전이나 전쟁터",
            "고요한 사원이나 서재",
            "넓은 바다나 미지의 땅",
            "활기찬 시장이나 축제",
        ],
    },
]

# --- 세션 스테이트 ---
if "pastlife_result" not in st.session_state:
    st.session_state.pastlife_result = None
if "pastlife_image" not in st.session_state:
    st.session_state.pastlife_image = None
if "pastlife_story_streamed" not in st.session_state:
    st.session_state.pastlife_story_streamed = False

# --- 페이지 헤더 ---
st.markdown(
    "<div class='page-header'>"
    "<span class='page-icon float-anim'>🌀</span>"
    "<div class='page-title shimmer-text'>전생스토리</div>"
    "<div class='page-desc'>시간의 방랑자가 당신의 전생을 찾아드려요</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- 기본 정보 ---
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.markdown("<h3>📝 기본 정보</h3>", unsafe_allow_html=True)

col_name, col_birth = st.columns(2)
with col_name:
    name = st.text_input("이름 (닉네임)", max_chars=10, placeholder="홍길동")
with col_birth:
    birthdate = st.date_input(
        "생년월일",
        min_value=datetime.date(1940, 1, 1),
        max_value=datetime.date.today(),
        value=datetime.date(2000, 1, 1),
    )
st.markdown("</div>", unsafe_allow_html=True)

# --- 성격 퀴즈 ---
st.markdown("")
st.markdown("<h3 style='text-align:center;'>🧩 전생 탐색 퀴즈</h3>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#C8956C;'>5가지 질문에 답하면 전생을 찾아드려요!</p>",
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
        key=f"pastlife_q{i}",
        index=None,
    )
    answers.append(answer)

st.markdown("")
if st.button("🌀 전생 찾기", use_container_width=True, type="primary"):
    if not name or len(name.strip()) < 1:
        st.warning("이름을 알려주셔야 전생을 찾을 수 있어요!")
    elif None in answers:
        st.warning("모든 질문에 답해주세요! 전생 탐색에 필요해요 🙏")
    else:
        quiz_text = "\n".join(
            f"Q{i+1}. {QUIZ_QUESTIONS[i]['question']}\nA: {a}"
            for i, a in enumerate(answers)
        )
        user_prompt = (
            f"[이름]: {name}\n"
            f"[생년월일]: {birthdate.strftime('%Y년 %m월 %d일')}\n\n"
            f"[성격 퀴즈 답변]:\n{quiz_text}\n\n"
            f"위 정보를 바탕으로 이 사람의 전생을 찾아주세요."
        )

        try:
            show_loading_messages([
                "🌀 시간의 강을 거슬러 올라가는 중...",
                "📜 전생의 기억을 찾는 중...",
                "✨ 운명의 실을 풀어내는 중...",
            ], delay=1.5)

            with st.spinner("🌀 시간의 강을 거슬러 올라가고 있어요..."):
                raw = generate_chat(PASTLIFE_SYSTEM_PROMPT, user_prompt, json_mode=True)
                result = safe_parse_json(raw)

            if result is None:
                show_error("전생 탐색에 실패했어요. 다시 시도해주세요!")
            else:
                st.session_state.pastlife_result = result
                st.session_state.pastlife_story_streamed = False

                with st.spinner("🎨 전생의 모습을 그리고 있어요..."):
                    try:
                        prompt = PORTRAIT_IMAGE_BASE + result.get("portrait_prompt", "historical portrait")
                        st.session_state.pastlife_image = generate_image(prompt)
                    except Exception:
                        st.session_state.pastlife_image = None

                track_experience("past")
                st.snow()

        except Exception as e:
            show_error(f"전생 탐색 중 문제가 발생했어요: {e}")

# --- 결과 표시 ---
if st.session_state.pastlife_result:
    result = st.session_state.pastlife_result

    st.markdown("---")
    st.markdown(
        "<h2 style='text-align:center;' class='slide-up'>🌀 전생의 기억이 떠오릅니다...</h2>",
        unsafe_allow_html=True,
    )

    # 초상화 + 기본 정보
    col_portrait, col_info = st.columns([1, 1])

    with col_portrait:
        if st.session_state.pastlife_image:
            st.markdown("<div class='image-frame glow-pulse'>", unsafe_allow_html=True)
            st.image(st.session_state.pastlife_image, caption="전생 초상화", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='background:linear-gradient(145deg, #3D2B1A, #2B1E14); "
                "border:2px solid #8B6914; border-radius:12px; "
                "padding:60px; text-align:center;'>"
                "<span style='font-size:4em;'>🖼️</span><br><br>"
                "<span style='color:#C8956C;'>초상화 생성 중 오류 발생</span></div>",
                unsafe_allow_html=True,
            )

    with col_info:
        st.markdown(
            f"<div class='result-card' style='text-align:center;'>"
            f"<p style='color:#C8956C; font-size:1.1em;'>📍 {result.get('era', '')} · {result.get('country', '')} · {result.get('location', '')}</p>"
            f"<h2 style='color:#E8C170 !important; margin:15px 0; font-size:2em !important;'>"
            f"{result.get('occupation', '')} 「{result.get('past_name', '')}」</h2>"
            f"<p style='color:#C8956C; font-size:1.15em;'>{name}님의 전생입니다</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # 레이더 차트
        stats = result.get("stats", {})
        categories = ["💪 힘", "🧠 지능", "✨ 매력", "🍀 운", "🎨 창의력", "🛡️ 인내력"]
        values = [
            stats.get("strength", 50),
            stats.get("intelligence", 50),
            stats.get("charisma", 50),
            stats.get("luck", 50),
            stats.get("creativity", 50),
            stats.get("resilience", 50),
        ]
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

    # 전생 스토리 (스트리밍)
    if not st.session_state.pastlife_story_streamed:
        story_prompt = f"다음 전생 스토리를 더 드라마틱하게 500-800자로 다시 들려주세요. 소설체로:\n{result.get('story', '')}"
        st.markdown("<div class='result-card slide-up'><h3>📖 전생 이야기</h3>", unsafe_allow_html=True)
        st.write_stream(generate_chat_stream(
            "당신은 시간의 방랑자입니다. 서사적이고 드라마틱한 톤으로 전생 이야기를 들려줍니다.",
            story_prompt
        ))
        st.markdown("</div>", unsafe_allow_html=True)
        st.session_state.pastlife_story_streamed = True
    else:
        st.markdown(
            f"<div class='result-card slide-up'><h3>📖 전생 이야기</h3>"
            f"<p style='font-size:1.15em !important; line-height:2 !important;'>{result.get('story', '')}</p>"
            f"</div>", unsafe_allow_html=True)

    # 현생과의 연결
    st.markdown(
        f"<div class='result-card'>"
        f"<h3>🔗 현생과의 연결</h3>"
        f"<p>{result.get('connection_to_present', '')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # 전생 궁합
    with st.expander("💫 전생 궁합 알아보기"):
        st.markdown("<p style='color:#C8956C;'>친구의 정보를 입력하면 전생 궁합을 봐드려요!</p>", unsafe_allow_html=True)
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            friend_name = st.text_input("친구 이름", key="friend_name", max_chars=10)
        with col_f2:
            friend_birth = st.date_input("친구 생년월일", key="friend_birth",
                min_value=datetime.date(1940, 1, 1),
                max_value=datetime.date.today(),
                value=datetime.date(2000, 1, 1))

        if st.button("💫 궁합 보기", key="btn_compat"):
            if friend_name:
                compat_prompt = (
                    f"[나]: {name}, {result.get('era', '')} {result.get('country', '')}의 {result.get('occupation', '')}\n"
                    f"[친구]: {friend_name}, 생년월일 {friend_birth}\n"
                    f"두 사람의 전생 궁합을 재미있게 분석해주세요. 전생에서 어떤 관계였는지, 현생에서의 인연은 어떤지 300자 내외로."
                )
                with st.spinner("💫 전생 궁합을 보고 있어요..."):
                    compat_result = generate_chat(
                        "당신은 전생을 읽는 영매입니다. 두 사람의 전생 인연을 재미있고 따뜻하게 분석합니다.",
                        compat_prompt
                    )
                st.markdown(f"<div class='result-card'><h3>💫 전생 궁합 결과</h3><p>{compat_result}</p></div>", unsafe_allow_html=True)
            else:
                st.warning("친구 이름을 입력해주세요!")

    # 공유
    share_text = (
        f"전생: {result.get('era', '')} {result.get('country', '')}의 "
        f"{result.get('occupation', '')} 「{result.get('past_name', '')}」\n"
        f"{result.get('connection_to_present', '')}"
    )
    show_share_section("전생스토리 결과", share_text)

    # 공유 카드 이미지 다운로드
    card_bytes = generate_pastlife_card(result)
    st.download_button("📥 결과 카드 이미지 다운로드", data=card_bytes,
        file_name="pastlife_result.png", mime="image/png", use_container_width=True)

    # 다시 하기
    st.markdown("")
    if st.button("🔄 다른 답변으로 다시 찾기"):
        st.session_state.pastlife_result = None
        st.session_state.pastlife_image = None
        st.session_state.pastlife_story_streamed = False
        st.rerun()

show_other_features_legacy("past")
show_disclaimer()
