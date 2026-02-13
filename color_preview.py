"""Color theme preview - run with: streamlit run color_preview.py"""
import streamlit as st

st.set_page_config(page_title="Color Theme Preview", layout="wide")

THEMES = [
    {
        "name": "1. 다크 사이버 + 네온 그린",
        "bg": "#0a0e17",
        "bg2": "#111827",
        "card": "#1a1f2e",
        "primary": "#00ff88",
        "secondary": "#22d3ee",
        "text": "#e2e8f0",
        "text_sub": "#94a3b8",
        "border": "rgba(0,255,136,0.3)",
        "btn_from": "#059669",
        "btn_to": "#047857",
        "glow": "rgba(0,255,136,0.15)",
        "desc": "해커 연구실 / 사이버펑크 / Gen Z 최선호",
    },
    {
        "name": "2. 딥 틸 + 일렉트릭 퍼플",
        "bg": "#0a1520",
        "bg2": "#0f1d2e",
        "card": "#152238",
        "primary": "#a78bfa",
        "secondary": "#06b6d4",
        "text": "#e2e8f0",
        "text_sub": "#7dd3fc",
        "border": "rgba(167,139,250,0.3)",
        "btn_from": "#7c3aed",
        "btn_to": "#6d28d9",
        "glow": "rgba(167,139,250,0.15)",
        "desc": "미스터리 실험실 / 바이오루미네선스 / 신비로운 느낌",
    },
    {
        "name": "3. 다크 네이비 + 코랄/핑크",
        "bg": "#0f0e17",
        "bg2": "#1a1825",
        "card": "#232136",
        "primary": "#ff6e8a",
        "secondary": "#ffc470",
        "text": "#e8e0f0",
        "text_sub": "#a394c0",
        "border": "rgba(255,110,138,0.3)",
        "btn_from": "#e11d48",
        "btn_to": "#be123c",
        "glow": "rgba(255,110,138,0.15)",
        "desc": "Y2K 감성 / 도파민 디자인 / 팝 + 미스터리",
    },
    {
        "name": "4. 미드나잇 블랙 + 크롬/실버",
        "bg": "#09090b",
        "bg2": "#18181b",
        "card": "#27272a",
        "primary": "#e4e4e7",
        "secondary": "#a1a1aa",
        "text": "#fafafa",
        "text_sub": "#a1a1aa",
        "border": "rgba(228,228,231,0.2)",
        "btn_from": "#52525b",
        "btn_to": "#3f3f46",
        "glow": "rgba(228,228,231,0.1)",
        "desc": "미래적 AI 연구소 / 메탈릭 / 고급스러운 다크모드",
    },
]


def build_theme_card(t: dict) -> str:
    return f"""
    <div style="
        background: {t['bg']};
        border-radius: 20px;
        padding: 28px;
        border: 2px solid {t['border']};
        box-shadow: 0 0 30px {t['glow']};
    ">
        <h2 style="
            color: {t['primary']};
            text-align: center;
            font-size: 1.6rem;
            text-shadow: 0 0 20px {t['glow']};
            margin: 0 0 4px 0;
        ">🔬 수상한 AI 연구실</h2>
        <p style="
            color: {t['secondary']};
            text-align: center;
            font-size: 0.9rem;
            margin: 0 0 18px 0;
            letter-spacing: 2px;
        ">Suspicious AI Laboratory</p>

        <div style="
            display: flex;
            gap: 6px;
            justify-content: center;
            margin-bottom: 18px;
            flex-wrap: wrap;
        ">
            <span style="background:{t['card']}; color:{t['primary']}; padding:5px 12px;
                border-radius:8px; border:1px solid {t['border']}; font-size:0.8rem;">🔍 수배전단</span>
            <span style="background:{t['card']}; color:{t['primary']}; padding:5px 12px;
                border-radius:8px; border:1px solid {t['border']}; font-size:0.8rem;">🌀 평행우주</span>
            <span style="background:{t['card']}; color:{t['primary']}; padding:5px 12px;
                border-radius:8px; border:1px solid {t['border']}; font-size:0.8rem;">🧠 프로파일링</span>
            <span style="background:{t['card']}; color:{t['primary']}; padding:5px 12px;
                border-radius:8px; border:1px solid {t['border']}; font-size:0.8rem;">❓ 추리퀴즈</span>
        </div>

        <div style="display:flex; gap:10px; margin-bottom:16px;">
            <div style="flex:1; background:linear-gradient(145deg,{t['card']},{t['bg2']});
                border:1px solid {t['border']}; border-radius:12px; padding:16px; text-align:center;">
                <div style="font-size:2.2rem; margin-bottom:6px;">🔍</div>
                <div style="color:{t['primary']}; font-size:1rem; font-weight:bold;">수배전단 생성기</div>
                <div style="color:{t['text_sub']}; font-size:0.8rem; margin-top:4px;">AI가 만드는 수배 포스터</div>
            </div>
            <div style="flex:1; background:linear-gradient(145deg,{t['card']},{t['bg2']});
                border:1px solid {t['border']}; border-radius:12px; padding:16px; text-align:center;">
                <div style="font-size:2.2rem; margin-bottom:6px;">🧠</div>
                <div style="color:{t['primary']}; font-size:1rem; font-weight:bold;">심리 프로파일링</div>
                <div style="color:{t['text_sub']}; font-size:0.8rem; margin-top:4px;">FBI식 심리 분석</div>
            </div>
        </div>

        <div style="background:linear-gradient(145deg,{t['card']},{t['bg2']});
            border:2px solid {t['border']}; border-left:4px solid {t['primary']};
            border-radius:12px; padding:16px; margin-bottom:14px;">
            <h3 style="color:{t['primary']}; font-size:1.1rem; margin:0 0 6px 0;">🔮 분석 결과</h3>
            <p style="color:{t['text']}; font-size:0.9rem; line-height:1.7; margin:0;">
                당신의 숨겨진 유형은 <b style="color:{t['secondary']};">시간여행자</b>입니다.
                과거와 미래를 넘나드는 탐구 정신의 소유자...
            </p>
        </div>

        <div style="display:flex; gap:8px; margin-bottom:14px;">
            <div style="flex:1; background:{t['card']}; border:1px solid {t['border']};
                border-radius:10px; padding:10px; text-align:center;">
                <div style="color:{t['text_sub']}; font-size:0.8rem;">💰 재물운</div>
                <div style="color:{t['primary']}; font-size:1.6rem; font-weight:bold;">85</div>
            </div>
            <div style="flex:1; background:{t['card']}; border:1px solid {t['border']};
                border-radius:10px; padding:10px; text-align:center;">
                <div style="color:{t['text_sub']}; font-size:0.8rem;">💕 연애운</div>
                <div style="color:{t['secondary']}; font-size:1.6rem; font-weight:bold;">92</div>
            </div>
            <div style="flex:1; background:{t['card']}; border:1px solid {t['border']};
                border-radius:10px; padding:10px; text-align:center;">
                <div style="color:{t['text_sub']}; font-size:0.8rem;">💪 건강운</div>
                <div style="color:{t['primary']}; font-size:1.6rem; font-weight:bold;">78</div>
            </div>
        </div>

        <div style="text-align:center; margin-bottom:14px;">
            <span style="display:inline-block; background:linear-gradient(90deg,{t['btn_from']},{t['btn_to']});
                color:{t['text']}; padding:10px 36px; border-radius:8px; font-weight:bold;
                font-size:1rem; border:1px solid {t['border']};
                box-shadow:0 4px 15px {t['glow']};">🔬 실험 시작하기</span>
        </div>

        <div style="text-align:center;">
            <p style="color:{t['primary']}; font-size:1rem; font-weight:bold; margin:0 0 4px 0;">
                {t['name']}</p>
            <p style="color:{t['text_sub']}; font-size:0.8rem; margin:0; font-style:italic;">
                {t['desc']}</p>
        </div>
    </div>
    """


cards = [build_theme_card(t) for t in THEMES]

full_html = f"""
<div style="
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    padding: 20px;
    background: #111;
">
    <h1 style="text-align:center; color:#fff; font-size:2rem; margin-bottom:6px;">
        🎨 Color Theme Preview</h1>
    <p style="text-align:center; color:#888; font-size:1rem; margin-bottom:30px;">
        '수상한 AI 연구실'에 적용할 색상 테마 4종 미리보기</p>
    <div style="
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    ">
        {cards[0]}
        {cards[1]}
        {cards[2]}
        {cards[3]}
    </div>
</div>
"""

st.html(full_html)
