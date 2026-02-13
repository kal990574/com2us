import streamlit as st
from utils.ui_components import (
    apply_common_styles, show_disclaimer, safe_parse_json,
    show_error, show_other_features, show_share_section,
    track_experience, show_loading_messages,
)
from utils.openai_client import generate_chat, generate_image
from utils.share_card import generate_quiz_card

apply_common_styles()

# --- prompts ---
MYSTERY_SYSTEM_PROMPT = """당신은 미스터리 추리 퀴즈 출제자입니다.
난이도에 맞는 미니 미스터리 사건을 출제합니다.

규칙:
1. 사건은 살인, 도난, 실종 등 클래식 미스터리 장르
2. 용의자는 반드시 4명, 각각 뚜렷한 특징과 동기 보유
3. 단서는 3개, 난이도에 따라 명확도 조절
   - 초급: 단서가 매우 직접적, 범인이 비교적 명확
   - 중급: 단서가 간접적, 추리가 필요
   - 고급: 단서가 모호하고 반전 요소 포함
4. 반드시 논리적으로 범인을 특정할 수 있어야 함
5. 해설은 단서를 연결하여 왜 범인인지 명확히 설명

응답은 반드시 JSON 형식으로:
{
    "case_title": "사건 제목",
    "difficulty": "초급/중급/고급",
    "scenario": "사건 배경 및 상황 설명 (300-500자)",
    "suspects": [
        {
            "name": "용의자1 이름",
            "description": "외모/직업/성격 설명 (100-150자)",
            "motive": "동기 (50-100자)",
            "alibi": "알리바이 (50-100자)"
        },
        {
            "name": "용의자2 이름",
            "description": "외모/직업/성격 설명",
            "motive": "동기",
            "alibi": "알리바이"
        },
        {
            "name": "용의자3 이름",
            "description": "외모/직업/성격 설명",
            "motive": "동기",
            "alibi": "알리바이"
        },
        {
            "name": "용의자4 이름",
            "description": "외모/직업/성격 설명",
            "motive": "동기",
            "alibi": "알리바이"
        }
    ],
    "clues": [
        {"title": "단서1 제목", "content": "단서1 내용 (100-200자)"},
        {"title": "단서2 제목", "content": "단서2 내용"},
        {"title": "단서3 제목", "content": "단서3 내용"}
    ],
    "culprit": "범인 이름 (용의자 중 한 명)",
    "explanation": "해설 — 왜 이 사람이 범인인지 (300-500자, 단서 연결)",
    "scene_prompt": "DALL-E용 사건현장 일러스트 프롬프트 (영문, 미스터리 분위기)"
}"""

SCENE_IMAGE_BASE = (
    "mystery crime scene illustration, detective noir style, "
    "moody atmospheric lighting, cinematic composition, "
    "warm amber and dark brown color scheme, detailed environment art, "
)

DETECTIVE_RANKS = {
    (90, 101): "🏆 명탐정 (S등급)",
    (70, 90): "🔍 수석 수사관 (A등급)",
    (50, 70): "📋 수사관 (B등급)",
    (30, 50): "👮 순경 (C등급)",
    (0, 30): "🔰 수습 탐정 (D등급)",
}

# --- session state ---
if "quiz_case" not in st.session_state:
    st.session_state.quiz_case = None
if "quiz_revealed_clues" not in st.session_state:
    st.session_state.quiz_revealed_clues = set()
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False
if "quiz_selected" not in st.session_state:
    st.session_state.quiz_selected = None
if "quiz_scene_image" not in st.session_state:
    st.session_state.quiz_scene_image = None
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

# --- page header ---
st.markdown(
    "<div class='page-header'>"
    "<span class='page-icon float-anim'>🕵️</span>"
    "<div class='page-title shimmer-text'>AI 추리 퀴즈</div>"
    "<div class='page-desc'>AI가 출제하는 미스터리를 풀어보세요</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- difficulty selection ---
if not st.session_state.quiz_case:
    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    st.markdown("<h3>🎯 난이도 선택</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#C8956C;'>난이도를 선택하면 AI가 미스터리 사건을 출제합니다!</p>",
        unsafe_allow_html=True,
    )

    diff_cols = st.columns(3)
    difficulties = [
        ("🟢 초급", "초급", "명확한 단서, 추리 입문자용"),
        ("🟡 중급", "중급", "간접적 단서, 추리를 즐기는 분"),
        ("🔴 고급", "고급", "모호한 단서, 반전 포함"),
    ]

    for col, (label, diff, desc) in zip(diff_cols, difficulties):
        with col:
            st.markdown(
                f"<div class='feature-card' style='min-height:160px;'>"
                f"<div class='title'>{label}</div>"
                f"<div class='desc'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if st.button(f"{label} 시작", key=f"diff_{diff}", use_container_width=True):
                user_prompt = f"난이도: {diff}\n\n위 난이도에 맞는 미스터리 추리 퀴즈를 출제해주세요."

                try:
                    show_loading_messages([
                        "🕵️ 사건 파일을 준비하는 중...",
                        "📋 용의자 명단을 작성하는 중...",
                        "🔍 단서를 배치하는 중...",
                    ], delay=1.5)

                    with st.spinner("🕵️ 미스터리 사건을 구성하고 있어요..."):
                        raw = generate_chat(MYSTERY_SYSTEM_PROMPT, user_prompt, json_mode=True)
                        case = safe_parse_json(raw)

                    if case is None:
                        show_error("사건 생성에 실패했어요. 다시 시도해주세요!")
                    else:
                        st.session_state.quiz_case = case
                        st.session_state.quiz_revealed_clues = set()
                        st.session_state.quiz_answered = False
                        st.session_state.quiz_selected = None
                        st.session_state.quiz_score = 0

                        with st.spinner("🎨 사건현장을 그리고 있어요..."):
                            try:
                                prompt = SCENE_IMAGE_BASE + case.get("scene_prompt", "mystery scene")
                                st.session_state.quiz_scene_image = generate_image(prompt)
                            except Exception:
                                st.session_state.quiz_scene_image = None

                        st.rerun()

                except Exception as e:
                    show_error(f"사건 생성 중 문제가 발생했어요: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# --- case display ---
if st.session_state.quiz_case:
    case = st.session_state.quiz_case

    # Case header
    st.markdown(
        f"<div class='result-card' style='text-align:center;'>"
        f"<p style='color:#C8956C;'>📁 사건 파일 | 난이도: {case.get('difficulty', '')}</p>"
        f"<h2 style='color:#E8C170 !important; font-size:2em !important;'>"
        f"「{case.get('case_title', '')}」</h2>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Scene image
    if st.session_state.quiz_scene_image:
        st.markdown("<div class='image-frame'>", unsafe_allow_html=True)
        st.image(st.session_state.quiz_scene_image, caption="사건 현장", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Scenario
    st.markdown(
        f"<div class='result-card'>"
        f"<h3>📖 사건 개요</h3>"
        f"<p>{case.get('scenario', '')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Suspects
    st.markdown("<h3 style='text-align:center;'>👤 용의자 목록</h3>", unsafe_allow_html=True)
    suspects = case.get("suspects", [])
    suspect_cols = st.columns(2)

    for i, suspect in enumerate(suspects[:4]):
        with suspect_cols[i % 2]:
            st.markdown(
                f"<div class='result-card'>"
                f"<h3>👤 {suspect.get('name', f'용의자 {i+1}')}</h3>"
                f"<p>{suspect.get('description', '')}</p>"
                f"<p style='color:#E8C170 !important;'>💡 동기: {suspect.get('motive', '')}</p>"
                f"<p style='color:#C8956C !important;'>🕐 알리바이: {suspect.get('alibi', '')}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Clues (sequential reveal)
    st.markdown("---")
    st.markdown("<h3 style='text-align:center;'>🔍 단서 확인</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#C8956C;'>단서를 하나씩 확인해보세요!</p>",
        unsafe_allow_html=True,
    )

    clues = case.get("clues", [])
    for i, clue in enumerate(clues[:3]):
        if i in st.session_state.quiz_revealed_clues:
            st.markdown(
                f"<div class='result-card slide-up'>"
                f"<h3>🔍 단서 #{i+1}: {clue.get('title', '')}</h3>"
                f"<p>{clue.get('content', '')}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='card-back' style='padding:25px; min-height:auto;'>"
                f"<div class='card-pattern' style='font-size:2em !important;'>🔒</div>"
                f"<div class='card-text'>단서 #{i+1} — 클릭하여 확인</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if st.button(f"🔍 단서 #{i+1} 공개", key=f"clue_{i}"):
                st.session_state.quiz_revealed_clues.add(i)
                st.rerun()

    # Answer section
    if not st.session_state.quiz_answered:
        st.markdown("---")
        st.markdown("<h3 style='text-align:center;'>🎯 범인을 지목하세요!</h3>", unsafe_allow_html=True)

        suspect_names = [s.get("name", f"용의자 {i+1}") for i, s in enumerate(suspects[:4])]
        answer_cols = st.columns(len(suspect_names))

        for col, sname in zip(answer_cols, suspect_names):
            with col:
                if st.button(f"👆 {sname}", key=f"answer_{sname}", use_container_width=True):
                    st.session_state.quiz_selected = sname
                    st.session_state.quiz_answered = True

                    # Calculate score
                    culprit = case.get("culprit", "")
                    correct = sname == culprit
                    clues_used = len(st.session_state.quiz_revealed_clues)

                    if correct:
                        base_score = 100
                        penalty = clues_used * 10
                        st.session_state.quiz_score = max(30, base_score - penalty)
                    else:
                        st.session_state.quiz_score = max(10, 30 - clues_used * 5)

                    track_experience("quiz")
                    st.rerun()

    # Result display
    if st.session_state.quiz_answered:
        culprit = case.get("culprit", "")
        selected = st.session_state.quiz_selected
        correct = selected == culprit
        score = st.session_state.quiz_score

        st.markdown("---")

        # Correct/Wrong
        if correct:
            st.markdown(
                "<h2 style='text-align:center; color:#E8C170 !important;' class='slide-up'>"
                "🎉 정답입니다! 🎉</h2>",
                unsafe_allow_html=True,
            )
            st.balloons()
        else:
            st.markdown(
                f"<h2 style='text-align:center;' class='slide-up'>"
                f"❌ 아쉽습니다! 범인은 「{culprit}」입니다</h2>",
                unsafe_allow_html=True,
            )

        # Detective rank
        rank = "🔰 수습 탐정 (D등급)"
        for (low, high), r in DETECTIVE_RANKS.items():
            if low <= score < high:
                rank = r
                break

        rank_cols = st.columns(2)
        with rank_cols[0]:
            st.markdown(
                f"<div class='score-card'>"
                f"<div class='score-label'>추리력 점수</div>"
                f"<div class='score-value'>{score}점</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with rank_cols[1]:
            st.markdown(
                f"<div class='score-card'>"
                f"<div class='score-label'>탐정 등급</div>"
                f"<div class='score-value' style='font-size:1.4em !important;'>{rank}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # Explanation
        st.markdown(
            f"<div class='result-card'>"
            f"<h3>📋 사건 해설</h3>"
            f"<p>{case.get('explanation', '')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # All clues revealed
        for i, clue in enumerate(clues[:3]):
            if i not in st.session_state.quiz_revealed_clues:
                st.markdown(
                    f"<div class='result-card'>"
                    f"<h3>🔍 미확인 단서 #{i+1}: {clue.get('title', '')}</h3>"
                    f"<p>{clue.get('content', '')}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Share
        result_text = "정답!" if correct else "오답..."
        share_text = (
            f"사건: {case.get('case_title', '')}\n"
            f"결과: {result_text}\n"
            f"추리력 점수: {score}점\n"
            f"탐정 등급: {rank}"
        )
        show_share_section("추리 퀴즈 결과", share_text)

        quiz_result = {
            "case_title": case.get("case_title", ""),
            "correct": correct,
            "detective_rank": rank,
            "score": score,
            "explanation_summary": case.get("explanation", "")[:100],
        }
        card_bytes = generate_quiz_card(quiz_result)
        st.download_button(
            "📥 추리 결과 카드 다운로드",
            data=card_bytes,
            file_name="mystery_quiz.png",
            mime="image/png",
            use_container_width=True,
        )

    # Reset
    st.markdown("")
    if st.button("🔄 새로운 사건에 도전"):
        st.session_state.quiz_case = None
        st.session_state.quiz_revealed_clues = set()
        st.session_state.quiz_answered = False
        st.session_state.quiz_selected = None
        st.session_state.quiz_scene_image = None
        st.session_state.quiz_score = 0
        st.rerun()

show_other_features("quiz")
show_disclaimer()
