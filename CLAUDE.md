# 수상한 AI 연구실 (Suspicious AI Lab)

8-in-1 AI entertainment web app built with Streamlit and OpenAI.
4 main experiments + 4 legacy ("sealed") experiments.

## Tech Stack

- **Python** 3.14
- **Streamlit** 1.54.0 - Web UI framework
- **OpenAI SDK** 2.20.0 - GPT-4o-mini (text & vision), DALL-E 3 (image generation)
- **Pillow** 12.1.1 - Image processing
- **BeautifulSoup4** - HTML parsing for news article extraction
- **Plotly** - Interactive radar charts
- **Requests** 2.32.5 - HTTP requests

## Project Structure

```
com2us/
├── app.py                        # Main entry point (navigation)
├── pages/
│   ├── home.py                   # Landing page (연구실 로비)
│   ├── wanted_poster.py          # AI 수배전단 생성기 (NEW)
│   ├── parallel_universe.py      # AI 평행우주 연구소 (NEW)
│   ├── profiling.py              # AI 심리 프로파일링 (NEW)
│   ├── mystery_quiz.py           # AI 추리 퀴즈 (NEW)
│   ├── tarot.py                  # 타로마스터 (legacy)
│   ├── face_reader.py            # 관상카페 (legacy)
│   ├── past_life.py              # 전생스토리 (legacy)
│   └── news_comics.py            # 뉴스웹툰 (legacy)
├── utils/
│   ├── openai_client.py          # OpenAI client singleton (@st.cache_resource)
│   ├── ui_components.py          # Shared UI: loading, error, cross-promo, disclaimer
│   ├── share_card.py             # PIL-based 1080x1080 share card generators
│   └── styles.py                 # COMMON_CSS constant
├── requirements.txt
├── .streamlit/
│   ├── config.toml               # Streamlit theme configuration
│   └── secrets.toml              # API keys (NEVER commit - gitignored)
├── CLAUDE.md                     # This file
├── PLAN.md                       # Product planning document
└── color_preview.py              # (temp) Color theme preview tool
```

## Sidebar Structure

```
🏠 연구실 로비              ← home.py
─────────────────────
🔬 수상한 실험실
  🔍 수배전단 생성기        ← wanted_poster.py
  🌀 평행우주 연구소        ← parallel_universe.py
  🧠 심리 프로파일링        ← profiling.py
  ❓ 추리 퀴즈              ← mystery_quiz.py
─────────────────────
📂 봉인된 실험 기록
  🔮 타로마스터             ← tarot.py
  👁️ 관상카페               ← face_reader.py
  🌀 전생스토리             ← past_life.py
  📰 뉴스웹툰              ← news_comics.py
```

## Features

### Main Experiments (NEW)
1. **수배전단 생성기** (`pages/wanted_poster.py`): Photo upload/camera/text → Vision analyzes face → GPT creates humorous wanted poster → DALL-E generates illustration
2. **평행우주 연구소** (`pages/parallel_universe.py`): Name + birthdate + 3 branching quizzes → GPT generates parallel universe profile → DALL-E creates portrait → radar chart
3. **심리 프로파일링** (`pages/profiling.py`): 6 extreme choice quizzes → GPT generates FBI-style profile report → DALL-E creates character illustration → radar chart
4. **추리 퀴즈** (`pages/mystery_quiz.py`): Difficulty selection → GPT generates mystery case + suspects + clues → sequential clue reveal → answer judgment + detective rank

### Legacy Experiments (봉인된 실험 기록)
5. **타로마스터** (`pages/tarot.py`): Tarot reading with card-by-card reveal
6. **관상카페** (`pages/face_reader.py`): Face reading from selfie
7. **전생스토리** (`pages/past_life.py`): Past life story from quiz
8. **뉴스웹툰** (`pages/news_comics.py`): News article to 4-panel webtoon

## Coding Conventions

### Language
- **User-facing text**: Korean
- **Code, comments, variable names**: English

### Naming
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Session state keys: `snake_case` prefixed by feature (e.g., `wanted_result`, `quiz_case`)

### Prompts
- Store all GPT/DALL-E prompts as constants at the top of each page file
- Write prompts in Korean for Korean-targeted content
- Use f-strings to inject user input into prompt templates

### State Management
- Use `st.session_state` for all stateful data (results, images, user inputs)
- Initialize session state at the top of each page with `if key not in st.session_state`

### Cross-promotion
- New pages use `show_other_features(current)` → promotes other new experiments
- Legacy pages use `show_other_features_legacy(current)` → promotes other legacy experiments

### Caching
- `@st.cache_resource` for the OpenAI client singleton
- `@st.cache_data` for expensive computations that can be cached (e.g., article parsing)
- Do NOT cache DALL-E image generation (non-deterministic)

## API Usage Patterns

### OpenAI Client
```python
# utils/openai_client.py
import streamlit as st
from openai import OpenAI

@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets["API_KEY"])
```

### Text Generation (GPT-4o-mini)
- Model: `gpt-4o-mini`
- Use streaming (`stream=True`) for long text responses to improve perceived performance
- Display streamed text with `st.write_stream()`

### Vision Analysis (GPT-4o-mini)
- Model: `gpt-4o-mini`
- Send images as base64-encoded data URLs in the user message
- Encode uploaded images: `base64.b64encode(uploaded_file.read()).decode()`

### Image Generation (DALL-E 3)
- Model: `dall-e-3`
- Size: `1024x1024` (default)
- Always `n=1` (DALL-E 3 only supports single image per request)
- Generation takes 10-30 seconds - always wrap in `st.spinner()`
- Handle failures gracefully: show placeholder image on error

## Streamlit Patterns

### Page Layout
```python
st.set_page_config(page_title="수상한 AI 연구실", page_icon="🔬", layout="wide")
```

### Multi-page Navigation
- Use `st.navigation()` with section dict for grouped sidebar
- Sections: "연구실 로비", "🔬 수상한 실험실", "📂 봉인된 실험 기록"
- Icons: Emoji embedded in `title` string (NOT `icon` parameter — global CSS font override breaks Material Icons)
- "봉인된 실험 기록" section has 300px top margin via CSS `:last-of-type` selector

### UI Components
- `st.columns()` for side-by-side layouts
- `st.tabs()` for sub-navigation within a page
- `st.spinner("메시지...")` for all loading states
- `st.image(url_or_bytes, use_container_width=True)` for responsive images
- `st.download_button()` for saving/sharing results
- `st.expander()` for detailed explanations

### Error Handling
```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    st.error("🚨 AI 응답 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
```
- All API calls must be wrapped in try/except
- Show user-friendly Korean error messages via `st.error()`
- Log actual errors for debugging but don't expose to users

## Secrets Management

- API keys stored in `.streamlit/secrets.toml`
- Access via `st.secrets["API_KEY"]`
- `.streamlit/secrets.toml` is in `.gitignore` - NEVER commit
- NEVER hardcode API keys in source code

## Deployment

- **Target**: Streamlit Cloud
- `requirements.txt` must list all dependencies with pinned versions
- Secrets configured via Streamlit Cloud dashboard (Settings > Secrets)

## Important Rules

1. **NEVER hardcode API keys** - always use `st.secrets`
2. **Handle DALL-E failures gracefully** - show placeholder on error, don't crash
3. **Always show progress** - image generation takes 10-30s, use `st.spinner()` with descriptive Korean messages
4. **Rate limit handling** - catch `RateLimitError` and show retry message
5. **Image display** - always use `use_container_width=True` for responsive layout
6. **Session state isolation** - each page manages its own session state with prefixed keys
7. **Prompt safety** - never pass raw user input directly as the sole prompt; always wrap in a system message template
