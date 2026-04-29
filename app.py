import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · Multi-Agent AI Research",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Design tokens ── */
:root {
    --bg:            #0b0b0f;
    --bg-elev:       #111118;
    --bg-card:       rgba(255,255,255,0.025);
    --border:        rgba(255,255,255,0.08);
    --border-strong: rgba(255,255,255,0.14);
    --fg:            #ededea;
    --fg-muted:      #a3a09a;
    --fg-dim:        #6b6863;
    --accent:        #ff7a18;
    --accent-soft:   rgba(255,122,24,0.12);
    --accent-line:   rgba(255,122,24,0.28);
    --success:       #4ade80;
    --success-soft:  rgba(74,222,128,0.10);
}

/* ── Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--fg);
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: var(--bg);
    background-image:
        radial-gradient(ellipse 70% 45% at 15% -5%, rgba(255,122,24,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 55% 35% at 90% 5%, rgba(255,122,24,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 100% 60% at 50% 120%, rgba(255,122,24,0.05) 0%, transparent 60%);
    background-attachment: fixed;
}

/* subtle grain */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.025;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    z-index: 0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding: 1.5rem 2.5rem 5rem; max-width: 1240px; }

/* ── Top bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 3.5rem;
}
.brand {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: -0.01em;
}
.brand-logo {
    width: 26px; height: 26px;
    border-radius: 7px;
    background: linear-gradient(135deg, #ff9a3c 0%, #ff5a1a 100%);
    display: inline-flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 12px rgba(255,122,24,0.35), inset 0 1px 0 rgba(255,255,255,0.25);
}
.brand-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #0b0b0f;
    box-shadow: inset 0 0 0 2px #ff9a3c;
}
.topbar-meta {
    display: flex; align-items: center; gap: 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--fg-dim);
    letter-spacing: 0.06em;
}
.topbar-meta .live {
    display: inline-flex; align-items: center; gap: 0.45rem;
    color: var(--success);
}
.topbar-meta .live::before {
    content: ""; width: 6px; height: 6px; border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 8px var(--success);
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }

/* ── Hero ── */
.hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 1rem 0 3rem;
    position: relative;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 400;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--accent);
    background: var(--accent-soft);
    border: 1px solid var(--accent-line);
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    margin-bottom: 1.75rem;
}
.hero-eyebrow::before {
    content: ""; width: 5px; height: 5px; border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
}
.hero h1 {
    font-family: 'Inter', sans-serif;
    font-size: clamp(2.5rem, 6.5vw, 5.5rem);
    font-weight: 700;
    line-height: 0.98;
    letter-spacing: -0.04em;
    color: var(--fg);
    margin: 0 0 1.25rem;
    max-width: 14ch;
}
.hero h1 em {
    font-family: 'Instrument Serif', serif;
    font-style: italic;
    font-weight: 400;
    color: var(--accent);
    letter-spacing: -0.02em;
}
.hero-sub {
    font-size: 1.1rem;
    font-weight: 300;
    color: var(--fg-muted);
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── Stat strip ── */
.stat-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    margin: 2.5rem 0 0;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
}
.stat {
    padding: 1.1rem 1.25rem;
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
}
.stat:last-child { border-right: none; }
.stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--fg-dim);
}
.stat-value {
    font-family: 'Inter', sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--fg);
}
.stat-value em {
    font-family: 'Instrument Serif', serif;
    font-style: italic;
    font-weight: 400;
    color: var(--accent);
}

/* ── Section heading ── */
.section-heading {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin: 3.5rem 0 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}
.section-heading h2 {
    font-family: 'Inter', sans-serif;
    font-size: 1.35rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--fg);
    margin: 0;
}
.section-heading .section-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    color: var(--fg-dim);
}

/* ── Input card ── */
.input-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.75rem 2rem;
    backdrop-filter: blur(12px);
    transition: border-color 0.25s;
}
.input-card:focus-within {
    border-color: var(--accent-line);
}
.input-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--fg-muted);
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.input-label::before {
    content: ""; width: 14px; height: 1px; background: var(--accent);
}

/* ── Streamlit input override ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--fg) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
    padding: 0.95rem 1.15rem !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--fg-dim) !important;
    font-weight: 300 !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 4px var(--accent-soft) !important;
    background: rgba(255,255,255,0.04) !important;
}
.stTextInput > label { display: none !important; }

/* ── Button ── */
.stButton > button {
    background: linear-gradient(180deg, #ff9a3c 0%, #ff6a14 100%) !important;
    color: #15100a !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: -0.005em !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    padding: 0.85rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.12s, box-shadow 0.18s, filter 0.18s !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,0.25) inset,
        0 -1px 0 rgba(0,0,0,0.15) inset,
        0 6px 24px rgba(255,122,24,0.32) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,0.3) inset,
        0 -1px 0 rgba(0,0,0,0.15) inset,
        0 10px 32px rgba(255,122,24,0.42) !important;
    filter: brightness(1.04) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Chips ── */
.chip-row { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; margin-top: 1rem; }
.chip-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--fg-dim);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-right: 0.25rem;
}
.chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 0.35rem 0.75rem;
    font-size: 0.78rem;
    color: var(--fg-muted);
    font-weight: 400;
    transition: all 0.2s;
}
.chip:hover {
    border-color: var(--accent-line);
    color: var(--fg);
}

/* ── Pipeline rail ── */
.pipeline-rail {
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
}
.step-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
}
.step-card.active {
    border-color: var(--accent-line);
    background: linear-gradient(135deg, rgba(255,122,24,0.06) 0%, rgba(255,122,24,0.02) 100%);
    box-shadow: 0 0 0 1px var(--accent-line), 0 8px 32px rgba(255,122,24,0.08);
}
.step-card.done {
    border-color: rgba(74,222,128,0.18);
    background: var(--success-soft);
}
.step-row {
    display: flex;
    align-items: center;
    gap: 0.95rem;
}
.step-icon {
    width: 38px; height: 38px;
    border-radius: 10px;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--fg-muted);
    flex-shrink: 0;
    transition: all 0.3s;
}
.step-card.active .step-icon {
    background: var(--accent-soft);
    border-color: var(--accent-line);
    color: var(--accent);
}
.step-card.done .step-icon {
    background: var(--success-soft);
    border-color: rgba(74,222,128,0.25);
    color: var(--success);
}
.step-icon svg { width: 18px; height: 18px; }
.step-meta { display: flex; flex-direction: column; gap: 0.15rem; flex: 1; min-width: 0; }
.step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    color: var(--fg-dim);
    text-transform: uppercase;
}
.step-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--fg);
    letter-spacing: -0.01em;
}
.step-desc {
    font-size: 0.78rem;
    color: var(--fg-dim);
    margin-top: 0.1rem;
}
.step-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    padding: 0.3rem 0.6rem;
    border-radius: 6px;
    flex-shrink: 0;
}
.status-waiting  { color: var(--fg-dim); background: rgba(255,255,255,0.03); }
.status-running  {
    color: var(--accent);
    background: var(--accent-soft);
    display: inline-flex; align-items: center; gap: 0.4rem;
}
.status-running::before {
    content: ""; width: 6px; height: 6px; border-radius: 50%;
    background: var(--accent);
    animation: pulse 1.4s ease-in-out infinite;
}
.status-done {
    color: var(--success);
    background: var(--success-soft);
}

/* ── Result panels ── */
.report-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 2rem 2.4rem;
    margin-top: 1rem;
    position: relative;
}
.report-panel.feedback {
    border-color: rgba(74,222,128,0.18);
}
.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1.1rem;
    margin-bottom: 1.4rem;
    border-bottom: 1px solid var(--border);
}
.panel-title {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: -0.01em;
    color: var(--fg);
}
.panel-title .panel-icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    background: var(--accent-soft);
    color: var(--accent);
    display: inline-flex; align-items: center; justify-content: center;
}
.panel-title .panel-icon svg { width: 14px; height: 14px; }
.report-panel.feedback .panel-icon {
    background: var(--success-soft);
    color: var(--success);
}
.panel-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.16em;
    color: var(--fg-dim);
    text-transform: uppercase;
}

/* ── Markdown styling inside panels ── */
.report-panel h1, .report-panel h2, .report-panel h3 {
    font-family: 'Inter', sans-serif;
    color: var(--fg);
    letter-spacing: -0.02em;
    margin-top: 1.5rem;
    margin-bottom: 0.6rem;
}
.report-panel h1 { font-size: 1.5rem; font-weight: 600; }
.report-panel h2 { font-size: 1.2rem; font-weight: 600; }
.report-panel h3 { font-size: 1rem; font-weight: 600; }
.report-panel p, .report-panel li {
    color: #d4d2cc;
    line-height: 1.75;
    font-size: 0.94rem;
}
.report-panel ul, .report-panel ol { padding-left: 1.3rem; }
.report-panel a { color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--accent-line); }
.report-panel a:hover { border-bottom-color: var(--accent); }
.report-panel code {
    background: rgba(255,255,255,0.05);
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85em;
    color: var(--accent);
}
.report-panel hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

/* ── Expander ── */
.streamlit-expanderHeader, details summary {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    color: var(--fg-muted) !important;
    letter-spacing: 0.08em !important;
    padding: 0.7rem 1rem !important;
}
.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    padding: 1.2rem 1.4rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    color: #cdc8bf !important;
    line-height: 1.7 !important;
    white-space: pre-wrap !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: var(--fg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.65rem 1.4rem !important;
    transition: all 0.2s !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,255,255,0.07) !important;
    border-color: var(--border-strong) !important;
    color: var(--fg) !important;
    transform: none !important;
}

/* ── Spinner ── */
.stSpinner > div { color: var(--accent) !important; }

/* ── Alerts ── */
.stAlert {
    background: rgba(255,122,24,0.08) !important;
    border: 1px solid var(--accent-line) !important;
    border-radius: 10px !important;
    color: var(--fg) !important;
}

/* ── Footer ── */
.foot {
    margin-top: 5rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--fg-dim);
    letter-spacing: 0.08em;
}
.foot-right { display: flex; gap: 1.5rem; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .block-container { padding: 1rem 1.2rem 3rem; }
    .stat-strip { grid-template-columns: repeat(2, 1fr); }
    .stat:nth-child(2) { border-right: none; }
    .stat:nth-child(1), .stat:nth-child(2) { border-bottom: 1px solid var(--border); }
}
</style>
""", unsafe_allow_html=True)


# ── SVG icon helpers ─────────────────────────────────────────────────────────
ICON_SEARCH = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>"""
ICON_READER = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h12a4 4 0 0 1 4 4v12H8a4 4 0 0 1-4-4Z"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>"""
ICON_WRITER = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>"""
ICON_CRITIC = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h11"/></svg>"""
ICON_REPORT = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h4"/></svg>"""
ICON_SPARKLE = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/></svg>"""

STEP_META = {
    "search": ("01", "Search Agent",  "Gathers recent web sources via Tavily",  ICON_SEARCH),
    "reader": ("02", "Reader Agent",  "Scrapes & extracts deep content",        ICON_READER),
    "writer": ("03", "Writer Chain",  "Drafts a structured research report",    ICON_WRITER),
    "critic": ("04", "Critic Chain",  "Reviews, scores & gives a verdict",      ICON_CRITIC),
}


# ── Helper: render step card ─────────────────────────────────────────────────
def step_card(step_key: str, state: str):
    num, title, desc, icon = STEP_META[step_key]
    status_map = {
        "waiting": ("Waiting", "status-waiting"),
        "running": ("Running", "status-running"),
        "done":    ("Done",    "status-done"),
    }
    label, scls = status_map.get(state, ("", ""))
    ccls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {ccls}">
      <div class="step-row">
        <div class="step-icon">{icon}</div>
        <div class="step-meta">
          <span class="step-num">Step {num}</span>
          <span class="step-title">{title}</span>
          <span class="step-desc">{desc}</span>
        </div>
        <span class="step-status {scls}">{label}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ───────────────────────────────────────────────────────
for key, default in [("results", {}), ("running", False), ("done", False)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Top bar ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="brand">
    <span class="brand-logo"><span class="brand-dot"></span></span>
    <span>ResearchMind</span>
  </div>
  <div class="topbar-meta">
    <span>v1.0 · gemini-2.5-flash</span>
    <span class="live">SYSTEM ONLINE</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-eyebrow">Multi-Agent AI System</div>
  <h1>Research that <em>thinks</em> for you.</h1>
  <p class="hero-sub">
    Four specialized AI agents collaborate — searching, scraping, writing, and
    critiquing — to deliver a polished research report on any topic in minutes.
  </p>
</div>

<div class="stat-strip">
  <div class="stat">
    <span class="stat-label">Agents</span>
    <span class="stat-value">04</span>
  </div>
  <div class="stat">
    <span class="stat-label">Pipeline</span>
    <span class="stat-value">Sequential</span>
  </div>
  <div class="stat">
    <span class="stat-label">Model</span>
    <span class="stat-value"><em>Gemini</em> 2.5</span>
  </div>
  <div class="stat">
    <span class="stat-label">Output</span>
    <span class="stat-value">Markdown</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Section: Query ───────────────────────────────────────────────────────────
st.markdown("""
<div class="section-heading">
  <h2>Configure your research</h2>
  <span class="section-num">01 / QUERY</span>
</div>
""", unsafe_allow_html=True)

col_input, col_spacer, col_pipeline = st.columns([5, 0.4, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="input-label">Research Topic</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2026",
        key="topic_input",
        label_visibility="collapsed",
    )
    run_btn = st.button("Run Research Pipeline  →", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    examples = ["LLM agents 2026", "CRISPR gene editing", "Fusion energy progress", "AI in drug discovery"]
    chips_html = '<div class="chip-row"><span class="chip-label">Try →</span>'
    for ex in examples:
        chips_html += f'<span class="chip">{ex}</span>'
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)

with col_pipeline:
    r = st.session_state.results

    def s(step):
        steps = ["search", "reader", "writer", "critic"]
        if step in r:
            return "done"
        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    st.markdown('<div class="pipeline-rail">', unsafe_allow_html=True)
    for sk in ["search", "reader", "writer", "critic"]:
        step_card(sk, s(sk))
    st.markdown('</div>', unsafe_allow_html=True)


# ── Run pipeline ─────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    with st.spinner("Search Agent is gathering sources…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    # ── Step 2: Reader ──
    with st.spinner("Reader Agent is scraping top resources…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    # ── Step 3: Writer ──
    with st.spinner("Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # ── Step 4: Critic ──
    with st.spinner("Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ──────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown("""
    <div class="section-heading">
      <h2>Pipeline output</h2>
      <span class="section-num">02 / RESULTS</span>
    </div>
    """, unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("Search Agent · raw output", expanded=False):
            st.write(r["search"])

    if "reader" in r:
        with st.expander("Reader Agent · scraped content", expanded=False):
            st.write(r["reader"])

    # Final report
    if "writer" in r:
        st.markdown(f"""
        <div class="report-panel">
          <div class="panel-header">
            <div class="panel-title">
              <span class="panel-icon">{ICON_REPORT}</span>
              <span>Final Research Report</span>
            </div>
            <span class="panel-tag">Writer Chain · Output</span>
          </div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;display:flex;justify-content:flex-end;'>", unsafe_allow_html=True)
        st.download_button(
            label="Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Critic feedback
    if "critic" in r:
        st.markdown(f"""
        <div class="report-panel feedback">
          <div class="panel-header">
            <div class="panel-title">
              <span class="panel-icon">{ICON_CRITIC}</span>
              <span>Critic Feedback</span>
            </div>
            <span class="panel-tag">Critic Chain · Output</span>
          </div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="foot">
  <span>RESEARCHMIND © 2026</span>
  <div class="foot-right">
    <span>LANGCHAIN</span>
    <span>GEMINI</span>
    <span>TAVILY</span>
    <span>STREAMLIT</span>
  </div>
</div>
""", unsafe_allow_html=True)
