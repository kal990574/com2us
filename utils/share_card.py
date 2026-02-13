"""
SNS share card image generator using Pillow.

Generates 1080x1080 PNG result cards for each feature
with gradient background, warm brown/amber Layton theme, and Korean text.
"""

import io
import textwrap
from PIL import Image, ImageDraw, ImageFont

# --- Color Constants (Professor Layton theme) ---
BG_TOP = (43, 30, 20)         # #2B1E14
BG_BOTTOM = (61, 43, 26)      # #3D2B1A
GOLD = (232, 193, 112)        # #E8C170
LAVENDER = (245, 230, 200)    # #F5E6C8
PURPLE = (139, 105, 20)       # #8B6914
LIGHT_PURPLE = (200, 149, 108)  # #C8956C
WHITE = (255, 255, 255)
DARK_OVERLAY = (43, 30, 20, 180)
BAR_BG = (61, 43, 26)

CARD_SIZE = 1080
WATERMARK_TEXT = "Suspicious AI Lab"

# --- Font paths ---
_FONT_PATHS = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",   # macOS
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux
]


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a Korean-capable font with fallback to default."""
    for path in _FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _draw_rounded_rect(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    radius: int,
    fill: tuple,
) -> None:
    """Draw a rounded rectangle on the given ImageDraw."""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def _draw_gradient_bg(img: Image.Image) -> None:
    """Fill image with a vertical gradient from BG_TOP to BG_BOTTOM."""
    width, height = img.size
    for y in range(height):
        ratio = y / height
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * ratio)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * ratio)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, g, b))


def _draw_watermark(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    """Draw watermark text at the bottom center of the card."""
    font = _get_font(28)
    text = WATERMARK_TEXT
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    y = height - 60
    draw.text((x, y), text, fill=LIGHT_PURPLE, font=font)


def _wrap_text(text: str, width: int = 22) -> str:
    """Wrap text to specified character width, truncating if too long."""
    if not text:
        return ""
    if len(text) > width * 8:
        text = text[: width * 8 - 3] + "..."
    return textwrap.fill(text, width=width)


def _draw_title(draw: ImageDraw.ImageDraw, title: str, width: int) -> int:
    """Draw a centered title at the top and return the y offset after it."""
    font = _get_font(52)
    bbox = draw.textbbox((0, 0), title, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    y = 60
    draw.text((x, y), title, fill=GOLD, font=font)

    # Decorative line under title
    line_y = y + 70
    line_margin = 200
    draw.line(
        [(line_margin, line_y), (width - line_margin, line_y)],
        fill=GOLD,
        width=2,
    )
    return line_y + 30


def _draw_bar(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    bar_width: int,
    score: int,
    max_score: int = 100,
    label: str = "",
) -> int:
    """Draw a horizontal bar chart element. Returns next y position."""
    font = _get_font(28)
    bar_height = 28

    # Label
    if label:
        draw.text((x, y), label, fill=LAVENDER, font=font)
        y += 36

    # Background bar
    _draw_rounded_rect(draw, (x, y, x + bar_width, y + bar_height), 14, BAR_BG)

    # Fill bar
    fill_w = int(bar_width * min(score, max_score) / max_score)
    if fill_w > 28:
        _draw_rounded_rect(draw, (x, y, x + fill_w, y + bar_height), 14, GOLD)

    # Score text
    score_text = f"{score}"
    score_font = _get_font(24)
    draw.text((x + bar_width + 12, y + 2), score_text, fill=GOLD, font=score_font)

    return y + bar_height + 16


def _to_png_bytes(img: Image.Image) -> bytes:
    """Convert PIL Image to PNG bytes."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ===================================================================
# Public card generators
# ===================================================================


def generate_tarot_card(result: dict) -> bytes:
    """
    Generate tarot reading result card.

    Expected result keys:
    - cards: list of dict with 'name', 'direction' ('정방향'/'역방향')
    - advice: str (overall advice)
    - lucky_item: str
    """
    img = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
    _draw_gradient_bg(img)
    draw = ImageDraw.Draw(img)

    y = _draw_title(draw, "Tarot Reading", CARD_SIZE)

    # Cards section
    cards = result.get("cards", [])
    font_card = _get_font(34)
    font_small = _get_font(26)

    y += 10
    for i, card in enumerate(cards[:5]):
        name = card.get("name", f"Card {i + 1}")
        direction = card.get("direction", "")
        direction_mark = " ^" if direction == "정방향" else " v" if direction == "역방향" else ""
        card_text = f"[{name}]{direction_mark}"

        _draw_rounded_rect(
            draw, (80, y, CARD_SIZE - 80, y + 52), 12, DARK_OVERLAY
        )
        draw.text((100, y + 8), card_text, fill=GOLD, font=font_card)
        y += 64

    # Advice section
    y += 20
    draw.text((80, y), "Advice", fill=LIGHT_PURPLE, font=_get_font(30))
    y += 42
    advice = _wrap_text(result.get("advice", ""), width=25)
    for line in advice.split("\n")[:6]:
        draw.text((100, y), line, fill=LAVENDER, font=font_small)
        y += 34

    # Lucky item
    lucky = result.get("lucky_item", "")
    if lucky:
        y += 20
        draw.text((80, y), f"Lucky Item: {lucky}", fill=GOLD, font=font_card)

    _draw_watermark(draw, CARD_SIZE, CARD_SIZE)
    return _to_png_bytes(img)


def generate_face_card(result: dict) -> bytes:
    """
    Generate face reading result card.

    Expected result keys:
    - scores: dict with keys '재물', '연애', '건강', '사회' (int 0-100)
    - hidden_traits: list of str (up to 3)
    - top_jobs: list of str (up to 3)
    """
    img = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
    _draw_gradient_bg(img)
    draw = ImageDraw.Draw(img)

    y = _draw_title(draw, "AI Face Reading", CARD_SIZE)

    # Score bars
    scores = result.get("scores", {})
    bar_width = 600
    bar_x = 120
    y += 20

    for label_key in ["재물", "연애", "건강", "사회"]:
        score = scores.get(label_key, 50)
        y = _draw_bar(draw, bar_x, y, bar_width, score, label=label_key)

    # Hidden traits
    y += 20
    font_section = _get_font(32)
    font_item = _get_font(28)

    draw.text((80, y), "Hidden Traits", fill=LIGHT_PURPLE, font=font_section)
    y += 44
    traits = result.get("hidden_traits", [])
    for i, trait in enumerate(traits[:3]):
        trait_text = f"  {i + 1}. {trait}"
        if len(trait_text) > 30:
            trait_text = trait_text[:27] + "..."
        draw.text((100, y), trait_text, fill=LAVENDER, font=font_item)
        y += 38

    # Top jobs
    y += 20
    draw.text((80, y), "Best Career Fit TOP 3", fill=LIGHT_PURPLE, font=font_section)
    y += 44
    jobs = result.get("top_jobs", [])
    for i, job in enumerate(jobs[:3]):
        medal = ["1st", "2nd", "3rd"][i]
        job_text = f"  {medal}  {job}"
        if len(job_text) > 30:
            job_text = job_text[:27] + "..."
        draw.text((100, y), job_text, fill=GOLD if i == 0 else LAVENDER, font=font_item)
        y += 38

    _draw_watermark(draw, CARD_SIZE, CARD_SIZE)
    return _to_png_bytes(img)


def generate_pastlife_card(result: dict) -> bytes:
    """
    Generate past life story result card.

    Expected result keys:
    - era: str
    - country: str
    - place: str
    - job: str
    - name: str (past life name)
    - stats: dict with 6 stat keys (str -> int 0-100)
    - connection: str (connection to current life)
    """
    img = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
    _draw_gradient_bg(img)
    draw = ImageDraw.Draw(img)

    y = _draw_title(draw, "Past Life Story", CARD_SIZE)

    font_label = _get_font(28)
    font_value = _get_font(32)
    font_name = _get_font(48)

    # Era / Country / Place
    y += 10
    info_items = [
        ("Era", result.get("era", "")),
        ("Country", result.get("country", "")),
        ("Place", result.get("place", "")),
    ]
    for label, value in info_items:
        draw.text((100, y), label, fill=LIGHT_PURPLE, font=font_label)
        draw.text((260, y), value if len(value) <= 20 else value[:17] + "...", fill=LAVENDER, font=font_value)
        y += 44

    # Job and past life name (large)
    y += 10
    job = result.get("job", "")
    name = result.get("name", "")
    job_text = f"{job}" if job else ""
    draw.text((100, y), job_text, fill=LAVENDER, font=font_value)
    y += 48

    # Large name display
    _draw_rounded_rect(draw, (80, y, CARD_SIZE - 80, y + 72), 16, DARK_OVERLAY)
    name_bbox = draw.textbbox((0, 0), name, font=font_name)
    name_w = name_bbox[2] - name_bbox[0]
    draw.text(((CARD_SIZE - name_w) // 2, y + 10), name, fill=GOLD, font=font_name)
    y += 92

    # Stats bars
    y += 10
    stats = result.get("stats", {})
    bar_width = 500
    bar_x = 140

    stat_keys = list(stats.keys())[:6]
    for key in stat_keys:
        score = stats[key]
        y = _draw_bar(draw, bar_x, y, bar_width, score, label=key)

    # Connection to current life
    connection = result.get("connection", "")
    if connection:
        y += 10
        draw.text((80, y), "Connection to Present", fill=LIGHT_PURPLE, font=font_label)
        y += 36
        wrapped = _wrap_text(connection, width=25)
        font_conn = _get_font(24)
        for line in wrapped.split("\n")[:3]:
            draw.text((100, y), line, fill=LAVENDER, font=font_conn)
            y += 32

    _draw_watermark(draw, CARD_SIZE, CARD_SIZE)
    return _to_png_bytes(img)


def generate_news_card(result: dict) -> bytes:
    """
    Generate news webtoon result card.

    Expected result keys:
    - title: str (webtoon title)
    - summary: list of str (3-line news summary)
    - scenes: list of dict with 'description' (4 scenes)
    """
    img = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
    _draw_gradient_bg(img)
    draw = ImageDraw.Draw(img)

    y = _draw_title(draw, "AI News Webtoon", CARD_SIZE)

    font_subtitle = _get_font(36)
    font_body = _get_font(28)
    font_scene_label = _get_font(30)
    font_scene = _get_font(26)

    # Webtoon title
    y += 20
    title = result.get("title", "")
    if len(title) > 25:
        title = title[:22] + "..."
    title_bbox = draw.textbbox((0, 0), title, font=font_subtitle)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((CARD_SIZE - title_w) // 2, y), title, fill=GOLD, font=font_subtitle)
    y += 56

    # 3-line summary
    draw.text((80, y), "Summary", fill=LIGHT_PURPLE, font=font_scene_label)
    y += 42
    summary_lines = result.get("summary", [])
    for i, line in enumerate(summary_lines[:3]):
        text = f"  {line}"
        if len(text) > 35:
            text = text[:32] + "..."
        draw.text((100, y), text, fill=LAVENDER, font=font_body)
        y += 38

    # 4-panel scene descriptions
    y += 30
    draw.text((80, y), "4-Panel Scenes", fill=LIGHT_PURPLE, font=font_scene_label)
    y += 44

    scenes = result.get("scenes", [])
    for i, scene in enumerate(scenes[:4]):
        desc = scene.get("description", "") if isinstance(scene, dict) else str(scene)
        panel_label = f"#{i + 1}"

        _draw_rounded_rect(
            draw, (80, y, CARD_SIZE - 80, y + 100), 12, DARK_OVERLAY
        )

        draw.text((100, y + 8), panel_label, fill=GOLD, font=font_scene_label)

        wrapped = _wrap_text(desc, width=22)
        line_y = y + 10
        for line in wrapped.split("\n")[:2]:
            draw.text((200, line_y), line, fill=LAVENDER, font=font_scene)
            line_y += 32

        y += 116

    _draw_watermark(draw, CARD_SIZE, CARD_SIZE)
    return _to_png_bytes(img)


def generate_wanted_card(result: dict) -> bytes:
    """
    Generate wanted poster result card.

    Expected result keys:
    - crime: str
    - danger_level: str
    - bounty: str
    - traits: list of str
    - description: str
    """
    img = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
    _draw_gradient_bg(img)
    draw = ImageDraw.Draw(img)

    y = _draw_title(draw, "WANTED", CARD_SIZE)

    font_big = _get_font(36)
    font_body = _get_font(28)
    font_small = _get_font(24)

    # Crime
    y += 20
    draw.text((80, y), "Crime", fill=LIGHT_PURPLE, font=font_body)
    y += 40
    crime = result.get("crime", "")
    if len(crime) > 30:
        crime = crime[:27] + "..."
    _draw_rounded_rect(draw, (80, y, CARD_SIZE - 80, y + 56), 12, DARK_OVERLAY)
    draw.text((100, y + 12), crime, fill=GOLD, font=font_big)
    y += 76

    # Danger level
    draw.text((80, y), "Danger Level", fill=LIGHT_PURPLE, font=font_body)
    y += 40
    danger = result.get("danger_level", "")
    draw.text((100, y), danger, fill=GOLD, font=font_big)
    y += 52

    # Bounty
    draw.text((80, y), "Bounty", fill=LIGHT_PURPLE, font=font_body)
    y += 40
    bounty = result.get("bounty", "")
    draw.text((100, y), bounty, fill=GOLD, font=font_big)
    y += 60

    # Traits
    draw.text((80, y), "Special Traits", fill=LIGHT_PURPLE, font=font_body)
    y += 42
    traits = result.get("traits", [])
    for i, trait in enumerate(traits[:4]):
        text = f"  {i + 1}. {trait}"
        if len(text) > 35:
            text = text[:32] + "..."
        draw.text((100, y), text, fill=LAVENDER, font=font_small)
        y += 36

    # Description
    y += 16
    draw.text((80, y), "Description", fill=LIGHT_PURPLE, font=font_body)
    y += 40
    desc = _wrap_text(result.get("description", ""), width=28)
    for line in desc.split("\n")[:4]:
        draw.text((100, y), line, fill=LAVENDER, font=font_small)
        y += 32

    _draw_watermark(draw, CARD_SIZE, CARD_SIZE)
    return _to_png_bytes(img)


def generate_parallel_card(result: dict) -> bytes:
    """
    Generate parallel universe result card.

    Expected result keys:
    - parallel_name: str
    - occupation: str
    - country: str
    - annual_income: str
    - divergence_rate: int (0-100)
    - stats: dict (str -> int 0-100)
    """
    img = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
    _draw_gradient_bg(img)
    draw = ImageDraw.Draw(img)

    y = _draw_title(draw, "Parallel Universe", CARD_SIZE)

    font_name = _get_font(44)
    font_label = _get_font(28)
    font_value = _get_font(32)

    # Name
    y += 10
    name = result.get("parallel_name", "")
    name_bbox = draw.textbbox((0, 0), name, font=font_name)
    name_w = name_bbox[2] - name_bbox[0]
    _draw_rounded_rect(draw, (80, y, CARD_SIZE - 80, y + 68), 16, DARK_OVERLAY)
    draw.text(((CARD_SIZE - name_w) // 2, y + 10), name, fill=GOLD, font=font_name)
    y += 88

    # Info fields
    info_items = [
        ("Occupation", result.get("occupation", "")),
        ("Country", result.get("country", "")),
        ("Income", result.get("annual_income", "")),
    ]
    for label, value in info_items:
        draw.text((100, y), label, fill=LIGHT_PURPLE, font=font_label)
        val = value if len(value) <= 22 else value[:19] + "..."
        draw.text((300, y), val, fill=LAVENDER, font=font_value)
        y += 44

    # Divergence rate
    y += 10
    rate = result.get("divergence_rate", 50)
    draw.text((80, y), "Divergence Rate", fill=LIGHT_PURPLE, font=font_label)
    y += 40
    y = _draw_bar(draw, 120, y, 600, rate, label="")
    y += 10

    # Stats
    stats = result.get("stats", {})
    bar_width = 500
    bar_x = 140
    for key in list(stats.keys())[:5]:
        score = stats[key]
        y = _draw_bar(draw, bar_x, y, bar_width, score, label=key)

    _draw_watermark(draw, CARD_SIZE, CARD_SIZE)
    return _to_png_bytes(img)


def generate_profiling_card(result: dict) -> bytes:
    """
    Generate psychological profiling result card.

    Expected result keys:
    - type_name: str
    - danger_level: str
    - abilities: dict (str -> int 0-100)
    - weakness: str
    - partner_type: str
    """
    img = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
    _draw_gradient_bg(img)
    draw = ImageDraw.Draw(img)

    y = _draw_title(draw, "Psych Profile", CARD_SIZE)

    font_big = _get_font(40)
    font_label = _get_font(28)
    font_value = _get_font(30)
    font_small = _get_font(24)

    # Type name
    y += 10
    type_name = result.get("type_name", "")
    if len(type_name) > 20:
        type_name = type_name[:17] + "..."
    _draw_rounded_rect(draw, (80, y, CARD_SIZE - 80, y + 68), 16, DARK_OVERLAY)
    bbox = draw.textbbox((0, 0), type_name, font=font_big)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_SIZE - tw) // 2, y + 12), type_name, fill=GOLD, font=font_big)
    y += 88

    # Danger level
    draw.text((100, y), "Danger Level", fill=LIGHT_PURPLE, font=font_label)
    danger = result.get("danger_level", "")
    draw.text((350, y), danger, fill=GOLD, font=font_value)
    y += 50

    # Abilities
    y += 10
    draw.text((80, y), "Abilities", fill=LIGHT_PURPLE, font=font_label)
    y += 42
    abilities = result.get("abilities", {})
    bar_width = 500
    bar_x = 140
    for key in list(abilities.keys())[:6]:
        score = abilities[key]
        y = _draw_bar(draw, bar_x, y, bar_width, score, label=key)

    # Weakness
    y += 10
    draw.text((80, y), "Weakness", fill=LIGHT_PURPLE, font=font_label)
    y += 38
    weakness = result.get("weakness", "")
    if len(weakness) > 35:
        weakness = weakness[:32] + "..."
    draw.text((100, y), weakness, fill=LAVENDER, font=font_small)
    y += 40

    # Partner type
    draw.text((80, y), "Best Partner", fill=LIGHT_PURPLE, font=font_label)
    y += 38
    partner = result.get("partner_type", "")
    if len(partner) > 35:
        partner = partner[:32] + "..."
    draw.text((100, y), partner, fill=GOLD, font=font_small)

    _draw_watermark(draw, CARD_SIZE, CARD_SIZE)
    return _to_png_bytes(img)


def generate_quiz_card(result: dict) -> bytes:
    """
    Generate mystery quiz result card.

    Expected result keys:
    - case_title: str
    - correct: bool
    - detective_rank: str
    - score: int (0-100)
    - explanation_summary: str
    """
    img = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
    _draw_gradient_bg(img)
    draw = ImageDraw.Draw(img)

    y = _draw_title(draw, "Mystery Quiz", CARD_SIZE)

    font_big = _get_font(40)
    font_label = _get_font(28)
    font_value = _get_font(32)
    font_small = _get_font(24)

    # Case title
    y += 20
    draw.text((80, y), "Case", fill=LIGHT_PURPLE, font=font_label)
    y += 40
    case_title = result.get("case_title", "")
    if len(case_title) > 25:
        case_title = case_title[:22] + "..."
    _draw_rounded_rect(draw, (80, y, CARD_SIZE - 80, y + 56), 12, DARK_OVERLAY)
    draw.text((100, y + 10), case_title, fill=GOLD, font=font_value)
    y += 76

    # Result
    correct = result.get("correct", False)
    result_text = "CORRECT!" if correct else "WRONG..."
    result_color = GOLD if correct else LIGHT_PURPLE
    _draw_rounded_rect(draw, (80, y, CARD_SIZE - 80, y + 80), 16, DARK_OVERLAY)
    bbox = draw.textbbox((0, 0), result_text, font=font_big)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_SIZE - tw) // 2, y + 18), result_text, fill=result_color, font=font_big)
    y += 100

    # Detective rank
    draw.text((80, y), "Detective Rank", fill=LIGHT_PURPLE, font=font_label)
    y += 40
    rank = result.get("detective_rank", "")
    draw.text((100, y), rank, fill=GOLD, font=font_big)
    y += 60

    # Score bar
    score = result.get("score", 0)
    draw.text((80, y), "Score", fill=LIGHT_PURPLE, font=font_label)
    y += 40
    y = _draw_bar(draw, 120, y, 650, score)
    y += 20

    # Explanation
    draw.text((80, y), "Key Insight", fill=LIGHT_PURPLE, font=font_label)
    y += 40
    explanation = _wrap_text(result.get("explanation_summary", ""), width=28)
    for line in explanation.split("\n")[:5]:
        draw.text((100, y), line, fill=LAVENDER, font=font_small)
        y += 32

    _draw_watermark(draw, CARD_SIZE, CARD_SIZE)
    return _to_png_bytes(img)
