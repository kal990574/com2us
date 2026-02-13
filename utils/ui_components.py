import json
import time
import streamlit as st
from utils.styles import COMMON_CSS


def apply_common_styles():
    st.markdown(COMMON_CSS, unsafe_allow_html=True)


def show_disclaimer():
    st.markdown("---")
    st.caption(
        "⚠️ 수상한 AI 연구실은 엔터테인먼트 목적으로 제작되었습니다. "
        "결과는 AI가 생성한 것으로 실제와 무관합니다. "
        "재미로만 즐겨주세요! 😊"
    )
    st.caption("Made with ❤️ & AI | Powered by OpenAI GPT-4o-mini & DALL-E 3")


def safe_parse_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0]
            return json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        pass
    try:
        if "{" in text:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def show_error(message: str = "AI 응답 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."):
    st.error(f"🚨 {message}")


def show_other_features(current: str):
    """다른 기능 추천 섹션"""
    features = {
        "wanted": ("🔍", "수배전단 생성기", "pages/wanted_poster.py"),
        "parallel": ("🌀", "평행우주 연구소", "pages/parallel_universe.py"),
        "profiling": ("🧠", "심리 프로파일링", "pages/profiling.py"),
        "quiz": ("🕵️", "추리 퀴즈", "pages/mystery_quiz.py"),
    }

    others = {k: v for k, v in features.items() if k != current}

    st.markdown("---")
    st.markdown(
        "<h3 style='text-align:center;'>🔬 다른 실험도 참여해보세요!</h3>",
        unsafe_allow_html=True,
    )
    cols = st.columns(len(others))
    for col, (key, (icon, name, page)) in zip(cols, others.items()):
        with col:
            if st.button(f"{icon} {name}", key=f"cross_{key}", use_container_width=True):
                st.switch_page(page)


def show_other_features_legacy(current: str):
    """레거시 콘텐츠용 다른 기능 추천"""
    features = {
        "tarot": ("🔮", "타로마스터", "pages/tarot.py"),
        "face": ("👁️", "관상카페", "pages/face_reader.py"),
        "past": ("🌀", "전생스토리", "pages/past_life.py"),
        "news": ("📰", "뉴스웹툰", "pages/news_comics.py"),
    }

    others = {k: v for k, v in features.items() if k != current}

    st.markdown("---")
    st.markdown(
        "<h3 style='text-align:center;'>📂 다른 봉인된 실험도 해보세요!</h3>",
        unsafe_allow_html=True,
    )
    cols = st.columns(len(others))
    for col, (key, (icon, name, page)) in zip(cols, others.items()):
        with col:
            if st.button(f"{icon} {name}", key=f"cross_{key}", use_container_width=True):
                st.switch_page(page)


def show_share_section(title: str, text_result: str):
    """결과 공유 섹션 (텍스트 복사)"""
    share_text = f"[수상한 AI 연구실] {title}\n\n{text_result}\n\n나도 해보기 → 수상한 AI 연구실"

    st.markdown("---")
    st.markdown(
        "<h3 style='text-align:center;'>📤 결과 공유하기</h3>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.text_area(
            "공유용 텍스트 (복사해서 사용하세요!)",
            value=share_text,
            height=120,
            key=f"share_{title}",
        )
    with col2:
        st.markdown(
            "<div style='padding:15px; text-align:center;'>"
            "<p style='color:#A08060;'>📋 위 텍스트를 복사해서<br>"
            "SNS에 공유해보세요!</p>"
            "<p style='color:#E8C170; font-size:1.1em; margin-top:15px;'>"
            "친구와 결과를 비교하면<br>더 재밌어요! 🎉</p>"
            "</div>",
            unsafe_allow_html=True,
        )


def track_experience(feature: str):
    """체험 기록 추가"""
    if "experiences" not in st.session_state:
        st.session_state["experiences"] = set()
    st.session_state["experiences"].add(feature)


def show_stamp_sidebar():
    """사이드바에 체험 현황 스탬프 표시"""
    features = {
        "wanted": "🔍 수배전단",
        "parallel": "🌀 평행우주",
        "profiling": "🧠 프로파일링",
        "quiz": "🕵️ 추리퀴즈",
    }
    if "experiences" not in st.session_state:
        st.session_state["experiences"] = set()

    completed = st.session_state["experiences"]

    with st.sidebar:
        st.markdown("### 🔬 실험 현황")
        html = '<div class="stamp-container">'
        for key, label in features.items():
            status = "✅" if key in completed else "⬜"
            cls = "stamp-item completed" if key in completed else "stamp-item"
            html += f'<div class="{cls}">{status} {label}</div>'
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

        if len(completed & set(features.keys())) >= 4:
            st.markdown(
                '<div class="stamp-master">🏆 수석 연구원 달성!</div>',
                unsafe_allow_html=True,
            )
        else:
            count = len(completed & set(features.keys()))
            st.caption(f"완료: {count}/4")


def show_loading_messages(messages: list[str], delay: float = 2):
    """로딩 중 메시지를 순차적으로 표시"""
    placeholder = st.empty()
    for msg in messages:
        placeholder.markdown(
            f"<div style='text-align:center; color:#C8956C; font-size:1.2rem;'>{msg}</div>",
            unsafe_allow_html=True,
        )
        time.sleep(delay)
    placeholder.empty()


def show_result_history():
    """결과 히스토리를 expander로 표시"""
    if "result_history" not in st.session_state:
        return
    history = st.session_state["result_history"]
    if not history:
        return

    with st.expander(f"📜 이전 결과 보기 ({len(history)}건)", expanded=False):
        for i, item in enumerate(reversed(history), 1):
            title = item.get("title", f"결과 #{len(history) - i + 1}")
            content = item.get("content", "")
            st.markdown(f"**{i}. {title}**")
            st.markdown(content)
            if i < len(history):
                st.markdown("---")
