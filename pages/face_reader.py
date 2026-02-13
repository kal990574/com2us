import base64
import streamlit as st
from utils.ui_components import (apply_common_styles, show_disclaimer, safe_parse_json,
    show_error, show_other_features_legacy, show_share_section,
    track_experience, show_loading_messages)
from utils.openai_client import generate_chat_with_image, generate_image
from utils.share_card import generate_face_card

apply_common_styles()

# --- 프롬프트 ---
FACE_SYSTEM_PROMPT = """당신은 한국 전통 관상학을 현대적으로 재해석하는 AI 관상 전문가입니다.
이름: "도사 클로드"
말투: 점집 도사 느낌이지만 유쾌한 톤. "허허~ 보아하니..." 등

규칙:
1. 사진을 보고 얼굴 특징을 파악하세요 (이마, 눈, 코, 입, 턱 등)
2. 한국 전통 관상학 용어를 적절히 활용하세요 (천정, 인당, 준두 등)
3. 긍정적 해석 70% + 살짝 찔리는 해석 30% (재미 요소)
4. 절대 외모 비하나 부정적 표현 금지
5. "숨겨진 성격"은 의외의 매력 포인트로 표현하세요
6. 관상 점수는 모두 60점 이상으로 (기분 좋게!)

응답은 반드시 JSON 형식으로:
{
  "face_parts": {
    "forehead": {"feature": "특징", "meaning": "관상학적 의미", "emoji": "적절한 이모지"},
    "eyes": {"feature": "특징", "meaning": "의미", "emoji": "이모지"},
    "nose": {"feature": "특징", "meaning": "의미", "emoji": "이모지"},
    "mouth": {"feature": "특징", "meaning": "의미", "emoji": "이모지"},
    "jaw": {"feature": "특징", "meaning": "의미", "emoji": "이모지"}
  },
  "overall_reading": "종합 관상 해석 (300-400자)",
  "hidden_personality": ["성격1", "성격2", "성격3"],
  "matching_jobs": [
    {"job": "직업명", "reason": "이유"},
    {"job": "직업명", "reason": "이유"},
    {"job": "직업명", "reason": "이유"}
  ],
  "scores": {"wealth": 85, "love": 78, "health": 90, "social": 82},
  "character_description": "DALL-E용 캐릭터 일러스트 설명 (영문, 관상 특징 반영)"
}"""

CHARACTER_IMAGE_BASE = (
    "Korean traditional portrait illustration, modern stylized character art, "
    "soft watercolor and digital painting hybrid, mystical aura, "
    "hanbok-inspired decorative elements, ethereal lighting, "
    "portrait format, beautiful detailed face, "
)

# --- 세션 스테이트 ---
if "face_result" not in st.session_state:
    st.session_state.face_result = None
if "face_char_image" not in st.session_state:
    st.session_state.face_char_image = None

# --- 페이지 헤더 ---
st.markdown(
    "<div class='page-header'>"
    "<span class='page-icon float-anim'>👁️</span>"
    "<div class='page-title shimmer-text'>AI 관상카페</div>"
    "<div class='page-desc'>도사 클로드가 당신의 얼굴에 숨겨진 운명을 읽어드려요</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- 입력 섹션 ---
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.markdown("<h3>📸 셀카 업로드</h3>", unsafe_allow_html=True)

tab_upload, tab_camera = st.tabs(["📁 사진 업로드", "📷 카메라 촬영"])
with tab_upload:
    photo = st.file_uploader(
        "셀카를 올려주세요! (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        help="정면 사진이 분석에 가장 좋아요!",
    )
with tab_camera:
    camera_file = st.camera_input("셀카를 촬영해주세요!")

# Select whichever is provided
photo = photo or camera_file

if photo:
    col_photo, col_info = st.columns([1, 2])
    with col_photo:
        st.markdown("<div class='image-frame'>", unsafe_allow_html=True)
        st.image(photo, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_info:
        st.markdown(
            "<div style='padding:20px;'>"
            "<p style='color:#C8956C; font-size:1.15em;'>📷 사진이 업로드되었습니다!</p>"
            "<p style='color:#A08060;'>ℹ️ 사진은 분석 후 저장되지 않아요</p>"
            "<p style='color:#A08060;'>💡 정면 사진일수록 정확도가 올라가요</p>"
            "</div>",
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")
if st.button("👁️ 관상 보기", use_container_width=True, type="primary"):
    if not photo:
        st.warning("사진을 먼저 올려주세요!")
    else:
        try:
            image_bytes = photo.getvalue()
            b64 = base64.b64encode(image_bytes).decode()

            show_loading_messages([
                "🔍 얼굴의 기운을 읽는 중...",
                "📖 관상학 데이터 분석 중...",
                "✨ 운명을 해석하는 중...",
            ], delay=1.5)

            with st.spinner("🔍 얼굴의 기운을 읽고 있어요..."):
                raw = generate_chat_with_image(
                    FACE_SYSTEM_PROMPT,
                    "이 사진의 관상을 분석해주세요.",
                    b64,
                    json_mode=True,
                )
                result = safe_parse_json(raw)

            if result is None:
                show_error("관상 분석에 실패했어요. 다른 사진으로 시도해보세요!")
            else:
                st.session_state.face_result = result

                with st.spinner("🎨 당신만의 캐릭터를 그리고 있어요..."):
                    try:
                        char_desc = result.get("character_description", "beautiful Korean person portrait")
                        prompt = CHARACTER_IMAGE_BASE + char_desc
                        st.session_state.face_char_image = generate_image(prompt)
                    except Exception:
                        st.session_state.face_char_image = None

                track_experience("face")
                st.balloons()

        except Exception as e:
            show_error(f"관상 분석 중 문제가 생겼어요: {e}")

# --- 결과 표시 ---
if st.session_state.face_result:
    result = st.session_state.face_result

    st.markdown("---")
    st.markdown(
        "<h2 style='text-align:center;' class='slide-up'>👁️ 관상 분석 결과</h2>",
        unsafe_allow_html=True,
    )

    # 캐릭터 일러스트
    if st.session_state.face_char_image:
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.markdown("<div class='image-frame'>", unsafe_allow_html=True)
            if photo:
                st.image(photo, caption="원본 사진", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col_img2:
            st.markdown("<div class='image-frame glow-pulse'>", unsafe_allow_html=True)
            st.image(st.session_state.face_char_image, caption="AI 캐릭터 일러스트", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # 관상 점수
    st.markdown("")
    st.markdown("<h3>📊 관상 점수</h3>", unsafe_allow_html=True)
    scores = result.get("scores", {})
    score_labels = {"wealth": "💰 재물운", "love": "💕 연애운", "health": "💪 건강운", "social": "🤝 사회운"}
    score_cols = st.columns(4)
    for i, (key, label) in enumerate(score_labels.items()):
        with score_cols[i]:
            score = scores.get(key, 75)
            st.markdown(
                f"<div class='score-card'>"
                f"<div class='score-label'>{label}</div>"
                f"<div class='score-value'>{score}<span style='font-size:0.5em;'>점</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.progress(score / 100)

    # 부위별 분석
    st.markdown("")
    st.markdown("<h3>🔍 부위별 분석</h3>", unsafe_allow_html=True)
    face_parts = result.get("face_parts", {})
    part_labels = {"forehead": "이마", "eyes": "눈", "nose": "코", "mouth": "입", "jaw": "턱"}
    for key, label in part_labels.items():
        part = face_parts.get(key, {})
        if part:
            with st.expander(f"{part.get('emoji', '🔹')} {label} — {part.get('feature', '')}"):
                st.markdown(
                    f"<p style='font-size:1.15em; line-height:1.9;'>{part.get('meaning', '')}</p>",
                    unsafe_allow_html=True,
                )

    # 종합 해석
    st.markdown(
        f"<div class='result-card slide-up'>"
        f"<h3>🔮 종합 관상</h3>"
        f"<p>{result.get('overall_reading', '')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # 숨겨진 성격
    st.markdown("<h3>🎭 숨겨진 성격</h3>", unsafe_allow_html=True)
    for i, personality in enumerate(result.get("hidden_personality", []), 1):
        st.markdown(
            f"<div class='result-card' style='padding:15px 25px; margin:8px 0;'>"
            f"<span style='color:#E8C170; font-weight:bold; font-size:1.2em;'>{i}.</span> "
            f"<span style='font-size:1.15em;'>{personality}</span></div>",
            unsafe_allow_html=True,
        )

    # 어울리는 직업
    st.markdown("<h3>💼 어울리는 직업 TOP 3</h3>", unsafe_allow_html=True)
    job_cols = st.columns(3)
    for i, (col, job) in enumerate(zip(job_cols, result.get("matching_jobs", [])), 1):
        with col:
            st.markdown(
                f"<div class='score-card' style='min-height:120px;'>"
                f"<div style='color:#E8C170; font-size:1.3em; font-weight:bold; margin-bottom:8px;'>"
                f"#{i} {job.get('job', '')}</div>"
                f"<div style='color:#C8956C; font-size:1em;'>{job.get('reason', '')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # 공유
    hidden = ", ".join(result.get("hidden_personality", []))
    jobs = ", ".join(j.get("job", "") for j in result.get("matching_jobs", []))
    share_text = f"종합 관상: {result.get('overall_reading', '')}\n숨겨진 성격: {hidden}\n어울리는 직업: {jobs}"
    show_share_section("관상 분석 결과", share_text)

    # 공유 카드 이미지 다운로드
    card_bytes = generate_face_card(result)
    st.download_button("📥 결과 카드 이미지 다운로드", data=card_bytes,
        file_name="face_result.png", mime="image/png", use_container_width=True)

    # 다시 하기
    st.markdown("")
    if st.button("🔄 다른 사진으로 다시 보기"):
        st.session_state.face_result = None
        st.session_state.face_char_image = None
        st.rerun()

show_other_features_legacy("face")
show_disclaimer()
