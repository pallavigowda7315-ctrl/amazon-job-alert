"""
config.py
=========
Central configuration for the ECG Clinical Decision Support Dashboard.

Holds file paths, physiological constants, the clinical severity taxonomy
(kept consistent with the project's own MSc dissertation labels so that a
real model can be dropped in later without relabeling the UI), and the
shared visual theme (colours, typography, injected CSS) used by every page.

Design language
----------------
The palette and type system are deliberately drawn from actual bedside
cardiac monitors rather than a generic "healthcare SaaS" blue/white look:
a deep clinical navy chrome, a phosphor-green ECG trace accent (the colour
real ECG monitors render waveforms in), and a monospace face for vital
readouts (mirroring the digital readout on physical monitors). IBM Plex
Sans/Mono is used throughout for a technical-but-humane clinical feel.
"""
from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "models"

LOGO_PATH = ASSETS_DIR / "logo.png"
BANNER_PATH = ASSETS_DIR / "banner.png"

for _dir in (ASSETS_DIR, SAMPLE_DATA_DIR, REPORTS_DIR, ASSETS_DIR / "icons"):
    _dir.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# App metadata
# --------------------------------------------------------------------------
APP_NAME = "CardioScope"
APP_TAGLINE = "ECG Clinical Decision Support"
APP_ICON = "🫀"
ORGANISATION = "MSc Data Science Research Project -- Group 2"

# --------------------------------------------------------------------------
# Physiological / signal constants
# --------------------------------------------------------------------------
DEFAULT_SAMPLING_RATE = 500          # Hz -- matches the PhysioNet source dataset
RECORD_DURATION_S = 10               # seconds per record
STANDARD_LEADS = ["I", "II", "III", "aVR", "aVL", "aVF",
                   "V1", "V2", "V3", "V4", "V5", "V6"]
PRIMARY_VIEW_LEADS = ["II", "V1", "V5", "V6"]   # per spec: default lead set

BANDPASS_LOW_HZ = 0.5
BANDPASS_HIGH_HZ = 40.0

# --------------------------------------------------------------------------
# Clinical severity taxonomy
# --------------------------------------------------------------------------
# NOTE: kept consistent with the 3-tier clinical grouping used elsewhere in
# this dissertation project (Normal / Doctor review / Serious), so that the
# eventual real model's output labels plug straight into this UI unchanged.
CLINICAL_TIERS = {
    "Normal / usually benign": {
        "short": "Normal",
        "color": "#2A9D8F",
        "badge_bg": "#E4F5F2",
        "description": "No urgent abnormality detected. Routine follow-up only.",
    },
    "Doctor review / possible procedure": {
        "short": "Doctor Review",
        "color": "#F5A623",
        "badge_bg": "#FDF1DC",
        "description": "Findings warrant clinician review; not immediately life-threatening.",
    },
    "Serious / urgent review": {
        "short": "Serious",
        "color": "#E63946",
        "badge_bg": "#FCE4E6",
        "description": "Findings consistent with a clinically urgent arrhythmia pattern.",
    },
}
CLINICAL_TIER_ORDER = list(CLINICAL_TIERS.keys())


def tier_long_from_short(short_label: str) -> str:
    """Resolve a model's short severity label (e.g. "Doctor review",
    "Serious") to this app's long CLINICAL_TIERS key (e.g.
    "Doctor review / possible procedure"), so badge colour/description
    lookups work regardless of the exact casing a given model uses.

    The severity model's own artefact uses `{0: "Normal", 1: "Doctor
    review", 2: "Serious"}` -- note the lowercase "review", which does
    NOT exactly match this app's "Doctor Review" (capital R). Matching
    case-insensitively here avoids that mismatch silently breaking the
    tier badge. Falls back to returning the input unchanged (with a
    generic grey badge) if nothing matches, rather than raising.
    """
    if short_label in CLINICAL_TIERS:
        return short_label  # already a long key
    low = short_label.strip().lower()
    for long_key, info in CLINICAL_TIERS.items():
        if info["short"].strip().lower() == low:
            return long_key
    return short_label

# --------------------------------------------------------------------------
# Visual theme
# --------------------------------------------------------------------------
COLORS = {
    "navy": "#0A2540",          # chrome / sidebar / header
    "navy_light": "#123A5C",
    "trace_green": "#16C79A",   # signature ECG-trace accent
    "trace_green_dim": "#0E8F72",
    "bg": "#F5F7FA",            # page background -- sterile, cool white
    "surface": "#FFFFFF",       # card background
    "border": "#E2E8F0",
    "text": "#1B2430",
    "text_muted": "#5C6B7A",
    "amber": "#F5A623",
    "red": "#E63946",
    "teal": "#2A9D8F",
    "grid": "#26445C",          # ECG paper grid lines on dark viewer background
}

FONT_IMPORT_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=IBM+Plex+Sans:wght@400;500;600;700&"
    "family=IBM+Plex+Mono:wght@400;500;600&display=swap"
)

# A single ECG-trace SVG (data URI) used as the recurring signature motif
# in the sidebar header and Home hero -- the one deliberately "designed"
# element the rest of the UI stays quiet around.
_ECG_TRACE_SVG = (
    "M0,20 L20,20 L25,5 L30,35 L35,20 L45,20 L50,10 L55,20 L70,20 "
    "L75,2 L80,38 L85,20 L100,20"
)
ECG_TRACE_DATA_URI = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 40' "
    "preserveAspectRatio='none'>"
    f"<path d='{_ECG_TRACE_SVG}' fill='none' stroke='%2316C79A' "
    "stroke-width='2' stroke-linejoin='round' stroke-linecap='round'/>"
    "</svg>"
)


def get_custom_css() -> str:
    """Return the shared CSS block injected on every page via st.markdown.

    Centralised here (rather than duplicated per-page) so the visual
    language stays consistent and only needs to change in one place.
    """
    c = COLORS
    return f"""
    <style>
    @import url('{FONT_IMPORT_URL}');

    html, body, [class*="css"] {{
        font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    }}

    /* ---- page background ---- */
    .stApp {{
        background-color: {c['bg']};
    }}

    /* ---- sidebar chrome ---- */
    section[data-testid="stSidebar"] {{
        background-color: {c['navy']};
    }}
    section[data-testid="stSidebar"] * {{
        color: #E7EDF3 !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: {c['navy_light']};
    }}

    /* ---- headings ---- */
    h1, h2, h3 {{
        color: {c['text']};
        font-weight: 600;
    }}

    /* ---- monospace vitals / numeric readouts ---- */
    .vital-readout {{
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}

    /* ---- generic clinical card ---- */
    .cs-card {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        box-shadow: 0 1px 3px rgba(10, 37, 64, 0.06);
        margin-bottom: 0.9rem;
    }}
    .cs-card h4 {{
        margin: 0 0 0.35rem 0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {c['text_muted']};
        font-weight: 600;
    }}

    /* ---- status badges ---- */
    .cs-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.28rem 0.75rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
    }}
    .cs-dot {{
        width: 8px; height: 8px; border-radius: 50%; display: inline-block;
    }}

    /* ---- ECG trace divider (signature motif) ---- */
    .cs-trace-divider {{
        height: 34px;
        background-image: url("{ECG_TRACE_DATA_URI}");
        background-repeat: repeat-x;
        background-size: 140px 34px;
        opacity: 0.9;
        margin: 0.3rem 0 1.1rem 0;
    }}

    /* ---- footer disclaimer ---- */
    .cs-disclaimer {{
        font-size: 0.78rem;
        color: {c['text_muted']};
        border-top: 1px solid {c['border']};
        padding-top: 0.6rem;
        margin-top: 1.5rem;
    }}

    /* tighten default streamlit block spacing slightly for a denser,
       more "instrument panel" feel */
    div.block-container {{ padding-top: 1.6rem; }}
    </style>
    """


def apply_custom_theme(st_module) -> None:
    """Inject the shared CSS. Call once near the top of every page.

    Parameters
    ----------
    st_module : the `streamlit` module (passed in rather than imported
        here so config.py has no hard dependency on streamlit and stays
        trivially unit-testable).
    """
    st_module.markdown(get_custom_css(), unsafe_allow_html=True)


def init_page(st_module, page_title: str) -> None:
    """One-call page bootstrap: set_page_config + theme injection.

    Every file in pages/ is executed by Streamlit as an independent
    script run (Streamlit does not run app.py first), so each page must
    call `st.set_page_config` itself -- this helper just removes the
    boilerplate of repeating it identically in every file. Must be the
    very first Streamlit call in the page (per Streamlit's own
    requirement for set_page_config).
    """
    st_module.set_page_config(
        page_title=f"{page_title} | {APP_NAME}",
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_theme(st_module)
