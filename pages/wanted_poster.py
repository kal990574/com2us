import base64
import streamlit as st
from utils.ui_components import (
    apply_common_styles, show_disclaimer, safe_parse_json,
    show_error, show_other_features, show_share_section,
    track_experience, show_loading_messages,
)
from utils.openai_client import generate_chat, generate_chat_with_image, generate_image
from utils.share_card import generate_wanted_card

apply_common_styles()

# --- prompts ---
WANTED_SYSTEM_PROMPT = """당신은 인터폴 수배전단 작성 전문가입니다.
사용자의 외모 특징이나 사진 분석 결과를 바탕으로 유머러스하고 재미있는 수배전단을 작성합니다.

규칙:
1. 죄목은 반드시 웃기고 무해한 것으로! (예: "불법 매력 방출", "과도한 귀여움 유포")
2. 위험등급은 S/A/B/C/D 중 선택, 재미있는 이유 포함
3. 현상금은 코믹한 단위 사용 (예: "치킨 500마리", "스타벅스 기프티콘 999장")
4. 특이사항은 3-4개, 외모/성격 특징을 재치있게 표현
5. 전체적으로 밝고 유쾌한 톤 유지

응답은 반드시 JSON 형식으로:
{
    "suspect_name": "용의자 별명 (재미있게)",
    "crime": "죄목 (웃긴 것)",
    "danger_level": "위험등급 (S~D + 이유)",
    "bounty": "현상금 (코믹 단위)",
    "traits": ["특이사항1", "특이사항2", "특이사항3", "특이사항4"],
    "description": "용의자 설명 (150-200자, 유머러스하게)",
    "warning": "시민들에게 경고 한마디 (재미있게)",
    "portrait_prompt": "DALL-E용 수배전단 스타일 캐릭터 일러스트 프롬프트 (영문, wanted poster style)"
}"""

VISION_ANALYSIS_PROMPT = """이 사진의 인물 외모 특징을 분석해주세요.
다음 항목을 중심으로 간결하게 설명해주세요:
- 전체적인 인상과 분위기
- 눈에 띄는 외모적 특징
- 표정이나 포즈에서 느껴지는 성격
- 스타일/패션 특징

주의: 절대 부정적이거나 모욕적인 분석을 하지 마세요. 긍정적이고 재미있는 톤으로!"""

WANTED_IMAGE_BASE = (
    "wanted poster style character illustration, vintage paper texture, "
    "dramatic lighting, FBI mugshot style but comedic, "
    "warm sepia tones, detailed character portrait, "
)

# --- session state ---
if "wanted_result" not in st.session_state:
    st.session_state.wanted_result = None
if "wanted_image" not in st.session_state:
    st.session_state.wanted_image = None

# --- page header ---
st.markdown(
    "<div class='page-header'>"
    "<span class='page-icon float-anim'>🔍</span>"
    "<div class='page-title shimmer-text'>AI 수배전단 생성기</div>"
    "<div class='page-desc'>당신의 수배전단을 AI가 작성합니다</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- input section ---
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.markdown("<h3>📋 용의자 정보 입력</h3>", unsafe_allow_html=True)

input_tab1, input_tab2, input_tab3 = st.tabs(["📸 사진 업로드", "📷 카메라 촬영", "✏️ 텍스트 묘사"])

uploaded_image = None
text_description = None

with input_tab1:
    uploaded_file = st.file_uploader(
        "사진을 업로드하세요",
        type=["jpg", "jpeg", "png"],
        key="wanted_upload",
    )
    if uploaded_file:
        uploaded_image = uploaded_file
        st.image(uploaded_file, caption="업로드된 사진", use_container_width=True)

with input_tab2:
    camera_photo = st.camera_input("셀카를 찍어주세요", key="wanted_camera")
    if camera_photo:
        uploaded_image = camera_photo

with input_tab3:
    text_description = st.text_area(
        "외모를 묘사해주세요",
        placeholder="예: 큰 눈에 동글동글한 얼굴, 항상 웃는 표정, 안경 착용...",
        max_chars=300,
        height=130,
        key="wanted_text",
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")
if st.button("🔍 수배전단 생성", use_container_width=True, type="primary"):
    if not uploaded_image and (not text_description or len(text_description.strip()) < 5):
        st.warning("사진을 업로드하거나 외모를 묘사해주세요!")
    else:
        try:
            show_loading_messages([
                "🔍 용의자 정보를 수집하는 중...",
                "📋 인터폴 데이터베이스 검색 중...",
                "🖨️ 수배전단을 작성하는 중...",
            ], delay=1.5)

            # Build user prompt
            if uploaded_image:
                with st.spinner("👁️ 사진을 분석하고 있어요..."):
                    image_bytes = uploaded_image.read()
                    b64_image = base64.b64encode(image_bytes).decode()
                    appearance = generate_chat_with_image(
                        VISION_ANALYSIS_PROMPT,
                        "이 사진의 인물 외모를 분석해주세요.",
                        b64_image,
                    )
                user_prompt = f"[외모 분석 결과]:\n{appearance}\n\n위 외모 특징을 바탕으로 재미있는 수배전단을 작성해주세요."
            else:
                user_prompt = f"[용의자 외모 묘사]:\n{text_description}\n\n위 묘사를 바탕으로 재미있는 수배전단을 작성해주세요."

            with st.spinner("🔍 수배전단을 작성하고 있어요..."):
                raw = generate_chat(WANTED_SYSTEM_PROMPT, user_prompt, json_mode=True)
                result = safe_parse_json(raw)

            if result is None:
                show_error("수배전단 작성에 실패했어요. 다시 시도해주세요!")
            else:
                st.session_state.wanted_result = result

                with st.spinner("🎨 수배전단 일러스트를 그리고 있어요..."):
                    try:
                        prompt = WANTED_IMAGE_BASE + result.get("portrait_prompt", "wanted poster character")
                        st.session_state.wanted_image = generate_image(prompt)
                    except Exception:
                        st.session_state.wanted_image = None

                track_experience("wanted")
                st.balloons()

        except Exception as e:
            show_error(f"수배전단 생성 중 문제가 발생했어요: {e}")

# --- result display ---
if st.session_state.wanted_result:
    result = st.session_state.wanted_result

    st.markdown("---")
    st.markdown(
        "<h2 style='text-align:center;' class='slide-up'>🚨 수배전단 🚨</h2>",
        unsafe_allow_html=True,
    )

    col_poster, col_info = st.columns([1, 1])

    with col_poster:
        if st.session_state.wanted_image:
            st.markdown("<div class='image-frame glow-pulse'>", unsafe_allow_html=True)
            st.image(st.session_state.wanted_image, caption="용의자 몽타주", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='background:linear-gradient(145deg, #3D2B1A, #2B1E14); "
                "border:2px solid #8B6914; border-radius:12px; "
                "padding:60px; text-align:center;'>"
                "<span style='font-size:4em;'>🕵️</span><br><br>"
                "<span style='color:#C8956C;'>몽타주 생성 중 오류 발생</span></div>",
                unsafe_allow_html=True,
            )

    with col_info:
        # Suspect name
        st.markdown(
            f"<div class='result-card' style='text-align:center;'>"
            f"<p style='color:#C8956C; font-size:1.1em;'>WANTED</p>"
            f"<h2 style='color:#E8C170 !important; margin:10px 0; font-size:2em !important;'>"
            f"「{result.get('suspect_name', '')}」</h2>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Crime and danger level
        score_cols = st.columns(2)
        with score_cols[0]:
            st.markdown(
                f"<div class='score-card'>"
                f"<div class='score-label'>죄목</div>"
                f"<div class='score-value' style='font-size:1.5em !important;'>{result.get('crime', '')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with score_cols[1]:
            st.markdown(
                f"<div class='score-card'>"
                f"<div class='score-label'>위험등급</div>"
                f"<div class='score-value'>{result.get('danger_level', '')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Bounty
    st.markdown(
        f"<div class='result-card' style='text-align:center;'>"
        f"<h3>💰 현상금</h3>"
        f"<p style='font-size:1.8em !important; color:#E8C170 !important; font-weight:bold;'>"
        f"{result.get('bounty', '')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Traits
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown("<h3>📝 특이사항</h3>", unsafe_allow_html=True)
    traits = result.get("traits", [])
    for trait in traits:
        st.markdown(f"- {trait}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Description
    st.markdown(
        f"<div class='result-card'>"
        f"<h3>📋 용의자 설명</h3>"
        f"<p>{result.get('description', '')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Warning
    st.markdown(
        f"<div class='result-card'>"
        f"<h3>⚠️ 시민 경고</h3>"
        f"<p style='color:#E8C170 !important; font-weight:bold;'>{result.get('warning', '')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Share
    share_text = (
        f"수배명: {result.get('suspect_name', '')}\n"
        f"죄목: {result.get('crime', '')}\n"
        f"현상금: {result.get('bounty', '')}\n"
        f"위험등급: {result.get('danger_level', '')}"
    )
    show_share_section("수배전단 결과", share_text)

    card_bytes = generate_wanted_card(result)
    st.download_button(
        "📥 수배전단 카드 다운로드",
        data=card_bytes,
        file_name="wanted_poster.png",
        mime="image/png",
        use_container_width=True,
    )

    # Reset
    st.markdown("")
    if st.button("🔄 새로운 수배전단 만들기"):
        st.session_state.wanted_result = None
        st.session_state.wanted_image = None
        st.rerun()

show_other_features("wanted")
show_disclaimer()
