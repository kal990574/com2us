COMMON_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700;900&display=swap');

    /* ===== 전역 배경 & 폰트 (레이튼 교수 스타일) ===== */
    .stApp {
        background: linear-gradient(160deg, #2B1E14 0%, #3D2B1A 30%, #2B1E14 60%, #1A120B 100%);
        font-size: 1.35rem;
        font-family: 'Noto Serif KR', serif !important;
    }
    .stApp p, .stApp li, .stApp label, .stApp div {
        font-size: 1.3rem !important;
        color: #F5E6C8;
        font-family: 'Noto Serif KR', serif !important;
    }
    .stApp [data-testid="stMain"] span,
    .stApp [data-testid="stBottom"] span {
        font-size: 1.3rem !important;
        color: #F5E6C8;
        font-family: 'Noto Serif KR', serif !important;
    }
    .stApp .stMarkdown p {
        font-size: 1.35rem !important;
        line-height: 1.9;
        color: #F5E6C8;
    }
    .stTextArea textarea, .stTextInput input {
        font-size: 1.25rem !important;
        background: rgba(61, 43, 26, 0.8) !important;
        border-color: rgba(200, 149, 108, 0.3) !important;
        color: #F5E6C8 !important;
        font-family: 'Noto Serif KR', serif !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3D2B1A 0%, #2B1E14 50%, #1A120B 100%);
        border-right: 2px solid rgba(200, 149, 108, 0.25);
    }
    [data-testid="stSidebar"] p {
        font-size: 1.05rem !important;
    }

    /* ===== 타이틀 ===== */
    h1 {
        color: #E8C170 !important;
        text-align: center;
        font-size: 3.5rem !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5);
        letter-spacing: 2px;
        font-family: 'Noto Serif KR', serif !important;
    }
    h2 {
        color: #D4A574 !important;
        font-size: 2.4rem !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.3);
        font-family: 'Noto Serif KR', serif !important;
    }
    h3 {
        color: #D4A574 !important;
        font-size: 1.8rem !important;
        font-family: 'Noto Serif KR', serif !important;
    }

    /* ===== 페이지 헤더 ===== */
    .page-header {
        text-align: center;
        padding: 30px 20px 15px;
        margin-bottom: 10px;
        background: linear-gradient(180deg, rgba(200, 149, 108, 0.1) 0%, transparent 100%);
        border-radius: 0 0 30px 30px;
        border-bottom: 2px solid rgba(200, 149, 108, 0.15);
    }
    .stApp .page-header .page-icon {
        font-size: 4rem !important;
        display: block;
        margin-bottom: 10px;
        filter: drop-shadow(0 0 10px rgba(232, 193, 112, 0.4));
    }
    .stApp .page-header .page-title {
        font-size: 3.2rem !important;
        color: #E8C170 !important;
        font-weight: 900;
        text-shadow: 0 2px 8px rgba(0,0,0,0.4);
        margin-bottom: 8px;
        font-family: 'Noto Serif KR', serif !important;
    }
    .stApp .page-header .page-desc {
        font-size: 1.5rem !important;
        color: #C8956C !important;
        font-weight: 300;
    }

    /* ===== 히어로 섹션 ===== */
    .hero-section {
        text-align: center;
        padding: 60px 20px 30px;
        background: radial-gradient(ellipse at center, rgba(200, 149, 108, 0.08) 0%, transparent 70%);
    }
    .stApp .hero-section .hero-title {
        font-size: 4.9rem !important;
        color: #E8C170 !important;
        font-weight: 900;
        text-shadow: 0 3px 12px rgba(0,0,0,0.5), 0 0 30px rgba(232, 193, 112, 0.2);
        margin-bottom: 12px;
        letter-spacing: 4px;
        line-height: 1.2;
        font-family: 'Noto Serif KR', serif !important;
    }
    .stApp .hero-section .hero-subtitle {
        font-size: 1.55rem !important;
        color: #C8956C !important;
        margin-bottom: 12px;
        letter-spacing: 3px;
    }
    .stApp .hero-section .hero-stars {
        font-size: 2rem !important;
        letter-spacing: 12px;
        color: #8B6914;
    }

    /* 사이드바 네비게이션 */
    .stApp [data-testid="stSidebar"] span {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
        color: #D4A574 !important;
    }
    .stApp [data-testid="stSidebar"] li {
        padding: 6px 0 !important;
    }
    .stApp [data-testid="stSidebar"] li a span {
        font-size: 1.4rem !important;
        font-weight: 600 !important;
    }

    /* 사이드바 섹션 헤더 - 테마별 구분 */
    .stApp [data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {
        margin-top: 16px !important;
        margin-bottom: 6px !important;
        padding: 10px 12px !important;
        background: linear-gradient(90deg, rgba(200, 149, 108, 0.15) 0%, rgba(232, 193, 112, 0.08) 50%, transparent 100%) !important;
        border-top: 2px solid rgba(200, 149, 108, 0.3) !important;
        border-left: 3px solid #C8956C !important;
        border-radius: 0 8px 8px 0 !important;
    }
    .stApp [data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] span {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px;
        color: #E8C170 !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    /* 봉인된 실험 기록 섹션 - 더 아래로 분리 */
    .stApp [data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"]:last-of-type {
        margin-top: 300px !important;
        border-top: 1px dashed rgba(200, 149, 108, 0.25) !important;
        border-left: 3px solid rgba(139, 105, 20, 0.5) !important;
        background: linear-gradient(90deg, rgba(61, 43, 26, 0.3) 0%, transparent 100%) !important;
        opacity: 0.8;
    }
    .stApp [data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"]:last-of-type span {
        color: #A08060 !important;
        font-size: 1.05rem !important;
    }

    /* ===== 카테고리 헤더 ===== */
    .category-header {
        color: #E8C170;
        font-size: 1.9em;
        font-weight: bold;
        margin: 30px 0 15px 0;
        padding: 14px 18px;
        border-bottom: 2px solid rgba(200, 149, 108, 0.35);
        border-left: 4px solid #C8956C;
        background: linear-gradient(90deg, rgba(200, 149, 108, 0.1) 0%, transparent 100%);
        border-radius: 0 12px 12px 0;
        font-family: 'Noto Serif KR', serif !important;
    }

    /* ===== 피처 카드 (양피지 스타일) ===== */
    .feature-card {
        background: linear-gradient(145deg, rgba(61, 43, 26, 0.9), rgba(43, 30, 20, 0.95));
        border: 2px solid rgba(200, 149, 108, 0.3);
        border-radius: 12px;
        padding: 35px 20px;
        text-align: center;
        transition: all 0.3s ease;
        min-height: 240px;
        position: relative;
        overflow: hidden;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.2);
    }
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #E8C170, #C8956C, transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .feature-card::after {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(232, 193, 112, 0.05) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .feature-card:hover {
        transform: translateY(-8px);
        border-color: #C8956C;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(200, 149, 108, 0.1), inset 0 0 30px rgba(0,0,0,0.2);
    }
    .feature-card:hover::before, .feature-card:hover::after {
        opacity: 1;
    }
    .feature-card .emoji {
        font-size: 4.5em;
        margin-bottom: 15px;
        filter: drop-shadow(0 0 10px rgba(232, 193, 112, 0.3));
        position: relative;
        z-index: 1;
    }
    .feature-card .title {
        color: #E8C170;
        font-size: 1.9em !important;
        font-weight: bold;
        margin-bottom: 12px;
        position: relative;
        z-index: 1;
        font-family: 'Noto Serif KR', serif !important;
    }
    .feature-card .desc {
        color: #C8956C;
        font-size: 1.25em !important;
        line-height: 1.7;
        position: relative;
        z-index: 1;
    }
    .feature-card .tag {
        display: inline-block;
        background: linear-gradient(90deg, rgba(200, 149, 108, 0.25), rgba(139, 105, 20, 0.15));
        color: #F5E6C8;
        padding: 4px 14px;
        border-radius: 15px;
        font-size: 1.05em !important;
        margin-top: 14px;
        border: 1px solid rgba(200, 149, 108, 0.3);
        position: relative;
        z-index: 1;
    }

    /* ===== 입력 섹션 카드 ===== */
    .input-section {
        background: linear-gradient(145deg, rgba(61, 43, 26, 0.5), rgba(43, 30, 20, 0.4));
        border: 1px solid rgba(200, 149, 108, 0.2);
        border-radius: 12px;
        padding: 30px;
        margin: 15px 0;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.15);
    }
    .input-section h3 {
        color: #E8C170 !important;
        margin-bottom: 15px;
    }

    /* ===== 결과 카드 (양피지) ===== */
    .result-card {
        background: linear-gradient(145deg, rgba(61, 43, 26, 0.7), rgba(43, 30, 20, 0.6));
        border: 2px solid rgba(200, 149, 108, 0.25);
        border-radius: 12px;
        padding: 28px;
        margin: 18px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 0 25px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }
    .result-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 4px; height: 100%;
        background: linear-gradient(180deg, #E8C170, #8B6914);
        border-radius: 4px 0 0 4px;
    }
    .result-card h3 {
        color: #E8C170 !important;
        font-size: 1.8rem !important;
        margin-bottom: 12px;
        font-family: 'Noto Serif KR', serif !important;
    }
    .result-card p {
        color: #F5E6C8 !important;
        font-size: 1.35rem !important;
        line-height: 1.9 !important;
    }

    /* ===== 점수 카드 ===== */
    .score-card {
        background: linear-gradient(145deg, rgba(61, 43, 26, 0.7), rgba(43, 30, 20, 0.5));
        border: 1px solid rgba(200, 149, 108, 0.25);
        border-radius: 12px;
        padding: 18px 15px;
        text-align: center;
    }
    .score-card .score-label {
        color: #C8956C;
        font-size: 1.2em !important;
        margin-bottom: 5px;
    }
    .score-card .score-value {
        color: #E8C170;
        font-size: 2.4em !important;
        font-weight: 900;
    }

    /* ===== 통계 카드 ===== */
    .stat-card {
        background: linear-gradient(145deg, rgba(61, 43, 26, 0.6), rgba(43, 30, 20, 0.5));
        border: 1px solid rgba(200, 149, 108, 0.25);
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        transition: transform 0.2s;
    }
    .stat-card:hover {
        transform: translateY(-3px);
    }
    .stat-card .stat-number {
        font-size: 2.2em !important;
        font-weight: 900;
        color: #E8C170;
        text-shadow: 0 1px 4px rgba(0,0,0,0.3);
    }
    .stat-card .stat-label {
        color: #C8956C;
        font-size: 1.2em !important;
        margin-top: 5px;
    }

    /* ===== 사용법 스텝 ===== */
    .step-item {
        background: linear-gradient(145deg, rgba(61, 43, 26, 0.5), rgba(43, 30, 20, 0.4));
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        border: 1px solid rgba(200, 149, 108, 0.15);
        transition: transform 0.2s;
    }
    .step-item:hover {
        transform: translateY(-3px);
    }
    .step-item .step-num {
        display: inline-block;
        width: 40px; height: 40px;
        line-height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8B6914, #6B4F0A);
        color: #F5E6C8;
        font-weight: bold;
        font-size: 1.2em !important;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .step-item .step-text {
        color: #C8956C;
        font-size: 1.2em !important;
    }

    /* ===== 퀴즈 질문 카드 ===== */
    .quiz-card {
        background: linear-gradient(145deg, rgba(61, 43, 26, 0.5), rgba(43, 30, 20, 0.4));
        border: 1px solid rgba(200, 149, 108, 0.2);
        border-radius: 12px;
        padding: 22px;
        margin: 12px 0;
    }
    .quiz-card .quiz-num {
        display: inline-block;
        background: linear-gradient(135deg, #8B6914, #6B4F0A);
        color: #F5E6C8;
        padding: 5px 14px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1.1em !important;
        margin-bottom: 8px;
    }

    /* ===== 말풍선 ===== */
    .speech-bubble {
        background: linear-gradient(135deg, rgba(61, 43, 26, 0.8), rgba(80, 55, 30, 0.6));
        border: 1px solid rgba(200, 149, 108, 0.25);
        border-radius: 12px;
        padding: 14px 20px;
        text-align: center;
        margin: 8px 0;
        position: relative;
        font-size: 1.3em !important;
        color: #F5E6C8 !important;
    }

    /* ===== 패널 번호 뱃지 ===== */
    .panel-badge {
        display: inline-block;
        background: linear-gradient(135deg, #8B6914, #6B4F0A);
        color: #F5E6C8;
        padding: 6px 16px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.15em !important;
        margin-bottom: 8px;
    }

    /* ===== 버튼 (빈티지 느낌) ===== */
    .stButton > button {
        background: linear-gradient(90deg, #8B6914, #6B4F0A, #5A3E08) !important;
        color: #F5E6C8 !important;
        border: 2px solid rgba(200, 149, 108, 0.4) !important;
        border-radius: 8px !important;
        padding: 16px 32px !important;
        font-weight: bold !important;
        font-size: 1.3rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        font-family: 'Noto Serif KR', serif !important;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #A67C1A, #8B6914, #6B4F0A) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(-2px) !important;
        color: #FFF !important;
        border-color: #C8956C !important;
    }

    /* ===== 구분선 ===== */
    hr {
        border-color: rgba(200, 149, 108, 0.2) !important;
        margin: 25px 0 !important;
    }

    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        font-size: 1.35rem !important;
        color: #D4A574 !important;
        background: rgba(61, 43, 26, 0.3);
        border-radius: 8px;
    }
    details[open] .streamlit-expanderContent {
        font-size: 1.3rem !important;
    }

    /* ===== Progress bar ===== */
    .stProgress > div > div {
        background: linear-gradient(90deg, #8B6914, #E8C170) !important;
        border-radius: 6px;
    }

    /* ===== Metric ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(61, 43, 26, 0.5), rgba(43, 30, 20, 0.4));
        border: 1px solid rgba(200, 149, 108, 0.2);
        border-radius: 12px;
        padding: 12px;
    }
    [data-testid="stMetricValue"] {
        color: #E8C170 !important;
        font-size: 1.8rem !important;
    }

    /* ===== 이미지 래퍼 ===== */
    .image-frame {
        border: 3px solid rgba(200, 149, 108, 0.35);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4), inset 0 0 10px rgba(0,0,0,0.2);
    }

    /* ===== 애니메이션 ===== */
    @keyframes twinkle {
        0%, 100% { opacity: 0.2; }
        50% { opacity: 0.8; }
    }
    .sparkle { animation: twinkle 3s ease-in-out infinite; }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    .float-anim { animation: float 4s ease-in-out infinite; }

    @keyframes glow-pulse {
        0%, 100% { box-shadow: 0 0 5px rgba(200, 149, 108, 0.2); }
        50% { box-shadow: 0 0 15px rgba(200, 149, 108, 0.4), 0 0 30px rgba(232, 193, 112, 0.1); }
    }
    .glow-pulse { animation: glow-pulse 3s ease-in-out infinite; }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    .shimmer-text {
        background: linear-gradient(90deg, #E8C170 0%, #FFF 25%, #E8C170 50%, #8B6914 75%, #E8C170 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 5s linear infinite;
    }

    @keyframes slide-up {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .slide-up { animation: slide-up 0.6s ease-out; }

    /* ===== 면책 ===== */
    .disclaimer {
        text-align: center;
        color: #8B7355;
        font-size: 0.9em !important;
        margin-top: 30px;
    }

    /* ===== 모바일 반응형 ===== */
    @media (max-width: 768px) {
        .stApp .hero-section .hero-title { font-size: 2.5rem !important; }
        .stApp .hero-section .hero-subtitle { font-size: 1.1rem !important; }
        .feature-card { min-height: 180px !important; }
        .feature-card .emoji { font-size: 3em !important; }
        .stat-card .stat-number { font-size: 1.5em !important; }
    }

    /* ===== 히어로 파티클 (톱니바퀴 느낌) ===== */
    .hero-particles {
        position: relative;
        overflow: hidden;
    }
    .hero-particles::before, .hero-particles::after {
        content: '⚙';
        position: absolute;
        font-size: 1.2rem;
        color: rgba(200, 149, 108, 0.15);
        animation: particle-float 8s ease-in-out infinite;
    }
    .hero-particles::before { top: 15%; left: 8%; animation-delay: 0s; }
    .hero-particles::after { top: 55%; right: 12%; animation-delay: 4s; content: '🔍'; }
    @keyframes particle-float {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.15; }
        50% { transform: translateY(-15px) rotate(180deg); opacity: 0.4; }
    }

    /* ===== 타로 카드 뒷면 ===== */
    .stApp .card-back {
        background: linear-gradient(145deg, #3D2B1A, #5A3E08) !important;
        border: 2px solid rgba(200, 149, 108, 0.4) !important;
        border-radius: 8px;
        padding: 60px 20px;
        text-align: center;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.3);
    }
    .stApp .card-back .card-pattern {
        font-size: 4em !important;
        animation: glow-pulse 3s ease-in-out infinite;
    }
    .stApp .card-back .card-text {
        color: #C8956C !important;
        font-size: 1.2rem !important;
        margin-top: 15px;
    }

    /* ===== 스탬프 ===== */
    .stApp .stamp-container {
        text-align: center;
        padding: 15px !important;
    }
    .stApp .stamp-item {
        display: inline-block;
        font-size: 1.5rem !important;
        margin: 5px 8px;
        padding: 8px 12px;
        border-radius: 8px;
        background: rgba(61, 43, 26, 0.6);
        border: 1px solid rgba(200, 149, 108, 0.2);
    }
    .stApp .stamp-item.completed {
        border-color: #C8956C !important;
        background: rgba(200, 149, 108, 0.1) !important;
    }
    .stApp .stamp-master {
        font-size: 1.3rem !important;
        color: #E8C170 !important;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
        animation: glow-pulse 3s ease-in-out infinite;
    }


</style>
"""
