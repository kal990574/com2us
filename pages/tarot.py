import streamlit as st
from utils.ui_components import (
    apply_common_styles, show_disclaimer, safe_parse_json,
    show_error, show_other_features_legacy, show_share_section,
    track_experience, show_loading_messages,
)
from utils.openai_client import generate_chat, generate_chat_stream, generate_image
from utils.share_card import generate_tarot_card

apply_common_styles()

# --- 프롬프트 ---
TAROT_SYSTEM_PROMPT = """당신은 30년 경력의 신비로운 타로 마스터입니다.
이름: "미스틱 루나"
말투: 친근하면서도 신비로운 톤. "~했어요", "~네요" 체를 사용합니다.
성격: 따뜻하고 긍정적이지만 솔직한 조언도 해줍니다.

규칙:
1. 실제 타로카드 78장 중에서 카드를 선택해주세요 (메이저 아르카나 우선)
2. 각 카드의 정통 해석을 기반으로 하되, 질문자의 고민에 맞춰 해석하세요
3. 부정적인 카드가 나와도 희망적 메시지를 담아주세요
4. 마지막에 "오늘의 럭키 아이템"을 하나 재미있게 추천해주세요

응답은 반드시 JSON 형식으로:
{
  "cards": [
    {
      "name": "카드 영문 이름",
      "name_kr": "카드 한글 이름",
      "direction": "정방향 또는 역방향",
      "position": "과거/현재/미래 (쓰리카드만)",
      "interpretation": "카드 해석 (200-300자)",
      "image_keyword": "DALL-E 프롬프트용 핵심 키워드 3개 (영문)"
    }
  ],
  "overall_advice": "종합 조언 (300-500자)",
  "lucky_item": "오늘의 럭키 아이템"
}"""

TAROT_IMAGE_BASE = (
    "mystical tarot card illustration, ornate golden border, "
    "warm sepia and amber color scheme, vintage parchment glow, "
    "detailed fantasy art style, vertical card format, "
)

# --- 세션 스테이트 초기화 ---
if "tarot_result" not in st.session_state:
    st.session_state.tarot_result = None
if "tarot_images" not in st.session_state:
    st.session_state.tarot_images = []
if "revealed_cards" not in st.session_state:
    st.session_state.revealed_cards = set()
if "tarot_advice_streamed" not in st.session_state:
    st.session_state.tarot_advice_streamed = False

# --- 페이지 헤더 ---
st.markdown(
    "<div class='page-header'>"
    "<span class='page-icon float-anim'>🔮</span>"
    "<div class='page-title shimmer-text'>AI 타로마스터</div>"
    "<div class='page-desc'>미스틱 루나가 당신을 위해 카드를 펼쳐드려요</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- 입력 섹션 ---
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.markdown("<h3>📋 리딩 설정</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    spread_type = st.selectbox("스프레드 선택", ["원카드 (빠른 답변)", "쓰리카드 (과거-현재-미래)"])
with col2:
    category = st.selectbox("운세 카테고리", ["💕 연애운", "💰 금전운", "📚 학업/커리어운", "🌟 종합운"])

worry = st.text_area(
    "고민을 적어주세요",
    placeholder="오늘 고민되는 것을 자유롭게 적어주세요... ✨",
    max_chars=500,
    height=130,
)
st.markdown("</div>", unsafe_allow_html=True)

num_cards = 1 if "원카드" in spread_type else 3

st.markdown("")
if st.button("🔮 카드 뽑기", use_container_width=True, type="primary"):
    if not worry or len(worry.strip()) < 5:
        st.warning("고민을 조금 더 자세히 적어주시면 더 정확한 리딩이 가능해요!")
    else:
        user_prompt = f"[스프레드]: {'원카드' if num_cards == 1 else '쓰리카드'}\n[카테고리]: {category}\n[고민]: {worry}\n\n위 내용을 바탕으로 타로 리딩을 해주세요. 카드는 {num_cards}장 뽑아주세요."

        try:
            # 단계별 로딩 메시지
            show_loading_messages([
                "🔮 카드를 섞고 있어요...",
                "✨ 별자리와 교신 중...",
                "🌙 운명의 카드를 뽑는 중...",
            ], delay=1.5)

            with st.spinner("🔮 카드를 해석하고 있어요..."):
                raw = generate_chat(TAROT_SYSTEM_PROMPT, user_prompt, json_mode=True)
                result = safe_parse_json(raw)

            if result is None:
                show_error("타로 카드 해석에 실패했어요. 다시 시도해주세요!")
            else:
                st.session_state.tarot_result = result
                st.session_state.tarot_images = []
                st.session_state.revealed_cards = set()
                st.session_state.tarot_advice_streamed = False

                cards = result.get("cards", [])
                progress_bar = st.progress(0, text="카드 이미지를 그리고 있어요...")
                for i, card in enumerate(cards):
                    try:
                        prompt = TAROT_IMAGE_BASE + card.get("image_keyword", card.get("name", "tarot card"))
                        img_url = generate_image(prompt, size="1024x1792")
                        st.session_state.tarot_images.append(img_url)
                    except Exception:
                        st.session_state.tarot_images.append(None)
                    progress_bar.progress((i + 1) / len(cards), text=f"🎨 {i+1}/{len(cards)} 카드 완성!")
                progress_bar.empty()

                st.balloons()
                track_experience("tarot")

        except Exception as e:
            show_error(f"타로 리딩 중 문제가 발생했어요: {e}")

# --- 결과 표시 ---
if st.session_state.tarot_result:
    result = st.session_state.tarot_result
    cards = result.get("cards", [])
    images = st.session_state.tarot_images

    st.markdown("---")
    st.markdown(
        "<h2 style='text-align:center;' class='slide-up'>✨ 당신의 카드 ✨</h2>",
        unsafe_allow_html=True,
    )

    # 카드 순차 공개
    card_cols = st.columns(len(cards))
    for i, (card, col) in enumerate(zip(cards, card_cols)):
        with col:
            if i not in st.session_state.revealed_cards:
                # 카드 뒷면 표시
                st.markdown(
                    "<div class='card-back'>"
                    "<div class='card-pattern'>🃏</div>"
                    "<div class='card-text'>터치하여 카드를 공개하세요</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                if st.button(f"✨ {i+1}번 카드 공개", key=f"reveal_{i}"):
                    st.session_state.revealed_cards.add(i)
                    st.rerun()
            else:
                # 공개된 카드: 이미지/해석 표시
                if i < len(images) and images[i]:
                    st.markdown("<div class='image-frame glow-pulse'>", unsafe_allow_html=True)
                    st.image(images[i], use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div style='background:linear-gradient(145deg, #3D2B1A, #2B1E14); "
                        f"border:2px solid #8B6914; border-radius:12px; "
                        f"padding:50px 20px; text-align:center; min-height:200px;'>"
                        f"<span style='font-size:4em;'>🃏</span><br><br>"
                        f"<span style='color:#E8C170; font-size:1.2em;'>{card.get('name_kr', '타로카드')}</span></div>",
                        unsafe_allow_html=True,
                    )
                position = card.get("position", "")
                direction = card.get("direction", "")
                st.markdown(
                    f"<p style='text-align:center; color:#E8C170; font-weight:bold; font-size:1.2em; margin-top:10px;'>"
                    f"{position + ' · ' if position else ''}{card.get('name_kr', '')} ({direction})</p>",
                    unsafe_allow_html=True,
                )

    # 카드별 해석 (공개된 카드만)
    revealed = st.session_state.revealed_cards
    revealed_cards_list = [card for i, card in enumerate(cards) if i in revealed]
    if revealed_cards_list:
        st.markdown("")
        st.markdown("<h3>🃏 카드별 해석</h3>", unsafe_allow_html=True)
        for card in revealed_cards_list:
            position = card.get("position", "")
            header = f"{position} · " if position else ""
            with st.expander(f"🃏 {header}{card.get('name_kr', '')} ({card.get('direction', '')})"):
                st.markdown(f"<p style='font-size:1.15em; line-height:1.9;'>{card.get('interpretation', '')}</p>", unsafe_allow_html=True)

    # 종합 조언 (모든 카드 공개 시)
    if len(revealed) == len(cards):
        # 스트리밍 종합 조언
        if not st.session_state.tarot_advice_streamed:
            advice_prompt = f"다음 타로 리딩 결과에 대해 따뜻하고 신비로운 톤으로 300-500자 종합 조언을 해주세요:\n{result.get('overall_advice', '')}"
            st.markdown("<div class='result-card slide-up'><h3>✨ 종합 조언</h3>", unsafe_allow_html=True)
            st.write_stream(generate_chat_stream("당신은 따뜻한 타로 마스터 미스틱 루나입니다. 친근하면서도 신비로운 톤으로 말합니다.", advice_prompt))
            st.markdown("</div>", unsafe_allow_html=True)
            st.session_state.tarot_advice_streamed = True
        else:
            st.markdown(
                f"<div class='result-card slide-up'>"
                f"<h3>✨ 종합 조언</h3>"
                f"<p>{result.get('overall_advice', '')}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # 럭키 아이템
        st.markdown(
            f"<div class='result-card'>"
            f"<h3>🍀 오늘의 럭키 아이템</h3>"
            f"<p style='font-size:1.4em !important; color:#E8C170 !important; font-weight:bold;'>"
            f"{result.get('lucky_item', '')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # 공유
        card_names = ", ".join(c.get("name_kr", "") for c in cards)
        share_text = f"카드: {card_names}\n종합 조언: {result.get('overall_advice', '')}\n럭키 아이템: {result.get('lucky_item', '')}"
        show_share_section("타로 리딩 결과", share_text)

        # 공유 카드 이미지 다운로드
        card_bytes = generate_tarot_card(result)
        st.download_button(
            "📥 결과 카드 이미지 다운로드",
            data=card_bytes,
            file_name="tarot_result.png",
            mime="image/png",
            use_container_width=True,
        )

    # 다시 하기
    st.markdown("")
    if st.button("🔄 다른 고민으로 다시 뽑기"):
        st.session_state.tarot_result = None
        st.session_state.tarot_images = []
        st.session_state.revealed_cards = set()
        st.session_state.tarot_advice_streamed = False
        st.rerun()

show_other_features_legacy("tarot")
show_disclaimer()
