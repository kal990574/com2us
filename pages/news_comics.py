import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from utils.ui_components import (
    apply_common_styles, show_disclaimer, safe_parse_json, show_error,
    show_other_features_legacy, show_share_section, track_experience,
    show_loading_messages,
)
from utils.openai_client import generate_chat, generate_chat_stream, generate_image
from utils.share_card import generate_news_card

apply_common_styles()

# --- 프롬프트 ---
WEBTOON_SYSTEM_PROMPT = """당신은 인기 웹툰 작가이자 시사 풍자가입니다.
역할: 뉴스 기사를 재미있는 4컷 웹툰 시나리오로 변환합니다.

규칙:
1. 뉴스의 핵심 내용을 정확히 파악하세요
2. 4컷으로 기승전결 구조를 만드세요
3. 마지막 컷에는 반드시 유머 포인트(뒤집기, 풍자, 공감)를 넣으세요
4. 각 컷의 이미지 설명은 DALL-E가 그릴 수 있도록 구체적으로 작성하세요
5. 말풍선 대사는 짧고 임팩트 있게 (15자 이내)
6. 정치적으로 민감한 내용은 중립적으로 풍자하세요

응답은 반드시 JSON 형식으로:
{
  "news_summary": "뉴스 3줄 요약",
  "title": "웹툰 제목 (재치있게)",
  "panels": [
    {
      "panel_number": 1,
      "description": "컷 설명 (한국어)",
      "dialogue": "말풍선 텍스트",
      "image_prompt": "DALL-E용 영문 이미지 프롬프트 (구체적으로, 만화 스타일)",
      "emotion": "분위기 (유머/긴장/감동/반전)"
    },
    {
      "panel_number": 2,
      "description": "...",
      "dialogue": "...",
      "image_prompt": "...",
      "emotion": "..."
    },
    {
      "panel_number": 3,
      "description": "...",
      "dialogue": "...",
      "image_prompt": "...",
      "emotion": "..."
    },
    {
      "panel_number": 4,
      "description": "...",
      "dialogue": "...",
      "image_prompt": "...",
      "emotion": "..."
    }
  ]
}"""

STYLE_PROMPTS = {
    "귀여운 스타일 🥰": (
        "cute cartoon illustration, chibi characters, pastel colors, "
        "rounded shapes, simple clean background, Korean webtoon style, "
        "kawaii aesthetic, clean lineart, comic panel, "
    ),
    "시사만평 스타일 🎭": (
        "editorial cartoon, satirical illustration, exaggerated features, "
        "bold lineart, newspaper comic style, political cartoon aesthetic, "
        "expressive characters, comic panel, "
    ),
}

# --- 세션 스테이트 ---
if "webtoon_result" not in st.session_state:
    st.session_state.webtoon_result = None
if "webtoon_images" not in st.session_state:
    st.session_state.webtoon_images = []


def extract_text_from_url(url: str) -> str | None:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        article = soup.find("article") or soup.find("div", class_=re.compile(r"article|content|body|story"))
        if article:
            text = article.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 20]
        return "\n".join(lines[:50])
    except Exception:
        return None


# --- 페이지 헤더 ---
st.markdown(
    "<div class='page-header'>"
    "<span class='page-icon float-anim'>📰</span>"
    "<div class='page-title shimmer-text'>AI 뉴스웹툰</div>"
    "<div class='page-desc'>뉴스가 웹툰이 되는 마법 ✨</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- 입력 섹션 ---
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.markdown("<h3>📰 뉴스 입력</h3>", unsafe_allow_html=True)

input_method = st.radio("뉴스를 어떻게 입력할까요?", ["🔗 URL 입력", "📝 직접 입력"], horizontal=True)

news_text = None

if "URL" in input_method:
    url = st.text_input("뉴스 URL을 붙여넣어주세요", placeholder="https://news.example.com/article/...")
    if url:
        with st.spinner("뉴스를 가져오고 있어요..."):
            news_text = extract_text_from_url(url)
        if news_text:
            with st.expander("📋 추출된 뉴스 내용 (미리보기)"):
                st.markdown(
                    f"<p style='font-size:1.05em;'>{news_text[:500]}{'...' if len(news_text) > 500 else ''}</p>",
                    unsafe_allow_html=True,
                )
        elif url:
            st.warning("URL에서 내용을 가져올 수 없어요. 직접 입력해주세요!")
else:
    news_text = st.text_area(
        "뉴스 내용을 붙여넣어주세요",
        placeholder="뉴스 기사 내용을 복사해서 붙여넣어주세요...",
        max_chars=2000,
        height=200,
    )

st.markdown("")
style = st.selectbox("웹툰 스타일", list(STYLE_PROMPTS.keys()))
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")
if st.button("🎨 웹툰 만들기", use_container_width=True, type="primary"):
    if not news_text or len(news_text.strip()) < 30:
        st.warning("뉴스 내용이 너무 짧아요. 좀 더 자세한 내용을 입력해주세요!")
    else:
        user_prompt = f"[웹툰 스타일]: {style}\n\n[뉴스 내용]:\n{news_text[:2000]}\n\n위 뉴스를 4컷 웹툰으로 만들어주세요."

        try:
            show_loading_messages([
                "📰 뉴스를 분석하는 중...",
                "🎨 웹툰 시나리오를 구상 중...",
                "✏️ 스토리보드를 그리는 중...",
            ], delay=1.5)

            with st.spinner("📖 뉴스를 읽고 시나리오를 구상 중..."):
                raw = generate_chat(WEBTOON_SYSTEM_PROMPT, user_prompt, json_mode=True)
                result = safe_parse_json(raw)

            if result is None:
                show_error("웹툰 시나리오 생성에 실패했어요. 다시 시도해주세요!")
            else:
                st.session_state.webtoon_result = result
                st.session_state.webtoon_images = []

                panels = result.get("panels", [])
                style_prefix = STYLE_PROMPTS[style]

                progress_bar = st.progress(0, text="🎨 웹툰을 그리고 있어요...")
                for i, panel in enumerate(panels):
                    with st.spinner(f"🎨 {i+1}번째 컷 그리는 중... ({i+1}/{len(panels)})"):
                        try:
                            prompt = style_prefix + panel.get("image_prompt", "comic panel")
                            img_url = generate_image(prompt)
                            st.session_state.webtoon_images.append(img_url)
                        except Exception:
                            st.session_state.webtoon_images.append(None)
                    progress_bar.progress((i + 1) / len(panels), text=f"🎨 {i+1}/{len(panels)} 컷 완성!")
                progress_bar.empty()

                track_experience("news")
                st.balloons()

        except Exception as e:
            show_error(f"웹툰 생성 중 문제가 발생했어요: {e}")

# --- 결과 표시 ---
if st.session_state.webtoon_result:
    result = st.session_state.webtoon_result
    images = st.session_state.webtoon_images
    panels = result.get("panels", [])

    st.markdown("---")

    # 뉴스 요약
    st.markdown(
        f"<div class='result-card slide-up'>"
        f"<h3>📋 뉴스 요약</h3>"
        f"<p>{result.get('news_summary', '')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # 웹툰 제목
    st.markdown(
        f"<h2 style='text-align:center; color:#E8C170 !important; margin:25px 0;'>"
        f"🎬 {result.get('title', '웹툰')}</h2>",
        unsafe_allow_html=True,
    )

    # 4컷 웹툰 (2x2 그리드)
    for row in range(0, len(panels), 2):
        cols = st.columns(2)
        for j in range(2):
            idx = row + j
            if idx < len(panels):
                panel = panels[idx]
                with cols[j]:
                    # 패널 번호
                    st.markdown(
                        f"<div class='panel-badge'>{idx+1}컷 · {panel.get('emotion', '')}</div>",
                        unsafe_allow_html=True,
                    )
                    # 이미지
                    if idx < len(images) and images[idx]:
                        st.markdown("<div class='image-frame'>", unsafe_allow_html=True)
                        st.image(images[idx], use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f"<div style='background:linear-gradient(145deg, #3D2B1A, #2B1E14); "
                            f"border:2px solid #8B6914; border-radius:12px; "
                            f"padding:50px 20px; text-align:center; min-height:200px;'>"
                            f"<span style='font-size:3em;'>🎨</span><br><br>"
                            f"<span style='color:#C8956C;'>{panel.get('description', '')}</span></div>",
                            unsafe_allow_html=True,
                        )
                    # 말풍선
                    dialogue = panel.get("dialogue", "")
                    if dialogue:
                        st.markdown(
                            f"<div class='speech-bubble'>"
                            f"💬 <b style='color:#E8C170;'>{dialogue}</b></div>",
                            unsafe_allow_html=True,
                        )
                    st.markdown(
                        f"<p style='color:#A08060; font-size:0.95em; margin-top:5px;'>{panel.get('description', '')}</p>",
                        unsafe_allow_html=True,
                    )

    # 공유
    share_text = (
        f"제목: {result.get('title', '')}\n"
        f"뉴스 요약: {result.get('news_summary', '')}"
    )
    show_share_section("뉴스웹툰 결과", share_text)

    card_bytes = generate_news_card(result)
    st.download_button(
        "📥 결과 카드 이미지 다운로드",
        data=card_bytes,
        file_name="webtoon_result.png",
        mime="image/png",
        use_container_width=True,
    )

    # 다시 하기
    st.markdown("")
    if st.button("🔄 다른 뉴스로 웹툰 만들기"):
        st.session_state.webtoon_result = None
        st.session_state.webtoon_images = []
        st.rerun()

show_other_features_legacy("news")
show_disclaimer()
