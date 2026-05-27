import streamlit as st
from main import main as run_pipeline

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="IM QA Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg:        #080C14;
    --surface:   #0D1220;
    --card:      #111827;
    --border:    rgba(99,179,237,0.13);
    --accent:    #38BDF8;
    --accent2:   #818CF8;
    --accent3:   #34D399;
    --text:      #E2E8F0;
    --muted:     #64748B;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 99px; }

.hero-wrap {
    background: linear-gradient(135deg, #0D1220 0%, #0A1628 50%, #0D1220 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 40px 44px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-wrap::after {
    content: '';
    position: absolute;
    bottom: -80px; left: 30%;
    width: 320px; height: 200px;
    background: radial-gradient(circle, rgba(129,140,248,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 99px;
    padding: 4px 14px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 18px;
}
.hero-badge .dot { width: 6px; height: 6px; background: var(--accent3); border-radius: 50%; display: inline-block; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.8)} }
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #E2E8F0 0%, #38BDF8 60%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 10px;
}
.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--muted);
    letter-spacing: 0.04em;
}
.hero-stats {
    display: flex;
    gap: 32px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
}
.stat-item { display: flex; flex-direction: column; gap: 2px; }
.stat-val { font-size: 1.3rem; font-weight: 700; color: var(--accent); }
.stat-lbl { font-size: 0.7rem; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; }

.section-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after { content:''; flex:1; height:1px; background:var(--border); }

[data-testid="stTextInput"] input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1rem !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
}
[data-testid="stTextInput"] label {
    color: var(--muted) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
    color: #080C14 !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    padding: 14px 28px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 24px rgba(56,189,248,0.25) !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(56,189,248,0.4) !important;
}

[data-testid="stButton"] > button:not([kind="primary"]) {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    transition: all 0.2s ease !important;
    padding: 20px 10px !important;
    line-height: 1.5 !important;
    white-space: pre-line !important;
}
[data-testid="stButton"] > button:not([kind="primary"]):hover {
    border-color: var(--accent) !important;
    background: rgba(56,189,248,0.06) !important;
    color: var(--accent) !important;
}

[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stSidebar"] label {
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--accent) !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }
[data-testid="stToggle"] { accent-color: var(--accent) !important; }

.result-card {
    background: linear-gradient(135deg, rgba(52,211,153,0.06) 0%, rgba(56,189,248,0.04) 100%);
    border: 1px solid rgba(52,211,153,0.25);
    border-radius: 14px;
    padding: 24px 28px;
    display: flex;
    align-items: center;
    gap: 20px;
    margin-top: 16px;
}
.result-icon { font-size: 2.4rem; }
.result-text h3 { margin: 0 0 4px; font-size: 1.1rem; font-weight: 700; color: #34D399; }
.result-text p { margin: 0; font-size: 0.78rem; color: var(--muted); font-family: 'JetBrains Mono', monospace; }

.prompt-container {
    background: #060A10;
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 14px;
    overflow: hidden;
    margin-top: 8px;
}
.prompt-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    background: rgba(56,189,248,0.06);
    border-bottom: 1px solid rgba(56,189,248,0.12);
}
.prompt-dots { display:flex; gap:5px; }
.prompt-dots span { width:8px; height:8px; border-radius:50%; }
.prompt-dots .d1 { background:#F87171; }
.prompt-dots .d2 { background:#FBBF24; }
.prompt-dots .d3 { background:#34D399; }
.prompt-meta { font-size:0.62rem; color:#475569; letter-spacing:0.06em; font-family:'JetBrains Mono',monospace; }

.divider { height:1px; background:var(--border); margin:24px 0; }

[data-testid="stStatusWidget"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

/* selected platform button glow */
.plat-selected > button {
    border-color: var(--accent) !important;
    background: rgba(56,189,248,0.1) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 18px rgba(56,189,248,0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px">
      <div style="font-size:0.6rem;letter-spacing:0.18em;text-transform:uppercase;color:#38BDF8;font-weight:700;margin-bottom:4px">Configuration</div>
      <div style="font-size:0.75rem;color:#475569;">TestLink & Knowledge Base</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📂 Project")
    testlink_project_id = st.number_input(
        "TestLink Project ID", min_value=1, value=2,
        help="Numeric ID of the TestLink project (e.g. 2 = IndiaMART_Android_App)"
    )
    st.markdown("---")

    st.subheader("🧠 Knowledge Base")
    st.caption("Suite whose existing test cases are fed to the AI so it understands current module functionality.")
    testlink_kb_suite_id = st.number_input(
        "Module Test Suite ID", min_value=1, value=26691,
        help="e.g. Android Sanity Test Cases > PBR (254) — the module suite the AI should learn from"
    )
    st.markdown("---")

    st.subheader("🎯 Target Suite")
    st.caption("Where the agent will create new child test suites and test cases.")
    testlink_suite_id = st.number_input(
        "Target Test Suite ID", min_value=1, value=352634,
        help="Parent suite under which a new child suite will be created per ticket"
    )
    st.markdown("---")

    show_prompt = st.toggle(
        "🧾 Show AI Prompt",
        value=False,
        help="Displays the full LLM prompt on the UI with a one-click copy button"
    )
    st.markdown("---")

    st.markdown("""
    <div style="font-size:0.6rem;color:#334155;letter-spacing:0.06em;line-height:2;padding-top:4px">
    ⚡ Powered by IndiaMart QA Intelligence<br>
    🤖 LLM-Assisted Test Generation<br>
    📋 TestLink Integration Active<br>
    🛡 15 QA Rules Enforced
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <div class="hero-badge"><span class="dot"></span> AI Agent &nbsp;·&nbsp; Active</div>
  <div class="hero-title">IM QA Test Case<br>Generation Agent</div>
  <div class="hero-sub">// Autonomous &nbsp;·&nbsp; Intelligent &nbsp;·&nbsp; Precise &nbsp;·&nbsp; TestLink-Ready</div>
  <div class="hero-stats">
    <div class="stat-item"><span class="stat-val">LLM</span><span class="stat-lbl">Powered</span></div>
    <div class="stat-item"><span class="stat-val">4</span><span class="stat-lbl">Platforms</span></div>
    <div class="stat-item"><span class="stat-val">15</span><span class="stat-lbl">QA Rules</span></div>
    <div class="stat-item"><span class="stat-val">100%</span><span class="stat-lbl">Structured JSON</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLATFORM SELECTOR
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">🖥 &nbsp;Target Platform</div>', unsafe_allow_html=True)

if "selected_platform" not in st.session_state:
    st.session_state.selected_platform = "IndiaMart Android App"

PLATFORMS = [
    {"key": "IndiaMart Android App",  "icon": "🤖", "name": "Android App",  "type": "Native · Google Play"},
    {"key": "IndiaMart iOS App",       "icon": "🍎", "name": "iOS App",       "type": "Native · App Store"},
    {"key": "IndiaMart Mobile-Site",   "icon": "📱", "name": "Mobile Site",   "type": "Browser · Responsive"},
    {"key": "IndiaMart Desktop Site",  "icon": "🖥️", "name": "Desktop Site",  "type": "Browser · Full Width"},
]

pcols = st.columns(4)
for i, p in enumerate(PLATFORMS):
    with pcols[i]:
        is_sel = st.session_state.selected_platform == p["key"]
        check = "  ✦ selected" if is_sel else ""
        label = f"{p['icon']}  {p['name']}\n{p['type']}{check}"
        if is_sel:
            st.markdown('<div class="plat-selected">', unsafe_allow_html=True)
        if st.button(label, key=f"plat_{i}", use_container_width=True):
            st.session_state.selected_platform = p["key"]
            st.rerun()
        if is_sel:
            st.markdown('</div>', unsafe_allow_html=True)

platform = st.session_state.selected_platform

st.markdown(f"""
<div style="margin:10px 0 28px;display:flex;align-items:center;gap:8px">
  <div style="width:6px;height:6px;border-radius:50%;background:#34D399;flex-shrink:0"></div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#64748B;">
    Selected &rarr; <strong style="color:#38BDF8">{platform}</strong>
  </span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TICKET INPUT + GENERATE
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">🎟 &nbsp;OpenProject Ticket</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    ticket_id = st.text_input("TICKET ID", placeholder="Enter OpenProject Story / Task ID  e.g. 12345", label_visibility="collapsed")
with col_btn:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    generate = st.button("⚡ Generate", type="primary", use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RUN PIPELINE
# ─────────────────────────────────────────────
if generate:
    if not ticket_id.strip():
        st.warning("⚠️  Please enter an OpenProject Ticket ID.")
    elif not ticket_id.strip().isdigit():
        st.warning("⚠️  Ticket ID must be numeric (e.g. 12345).")
    else:
        with st.status("🤖  Agent initialising...", expanded=True) as status:
            st.write(f"📡  Fetching ticket **#{ticket_id}** from OpenProject...")
            st.write(f"🖥  Platform target locked → **{platform}**")
            st.write("🧠  Loading knowledge base from TestLink...")
            st.write("⚡  Sending prompt to LLM — generating test cases...")

            try:
                success, created, failed, prompt_used = run_pipeline(
                    ticket_id=ticket_id.strip(),
                    project_id=int(testlink_project_id),
                    suite_id=int(testlink_suite_id),
                    kb_suite_id=int(testlink_kb_suite_id),
                    show_prompt=show_prompt,
                    platform=platform,
                )

                if success:
                    status.update(label="✅  Agent Complete — Test cases pushed to TestLink", state="complete", expanded=False)

                    st.markdown(f"""
                    <div class="result-card">
                      <div class="result-icon">🎯</div>
                      <div class="result-text">
                        <h3>Test Cases Created Successfully</h3>
                        <p>✅ Created: {created} &nbsp;&nbsp;|&nbsp;&nbsp; ❌ Failed: {failed} &nbsp;&nbsp;|&nbsp;&nbsp; 🖥 {platform}</p>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.balloons()

                    # Prompt Inspector
                    if show_prompt and prompt_used:
                        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                        st.markdown('<div class="section-label">🧾 &nbsp;AI Prompt Inspector</div>', unsafe_allow_html=True)

                        word_count = len(prompt_used.split())
                        char_count = len(prompt_used)

                        st.markdown(f"""
                        <div class="prompt-container">
                          <div class="prompt-header">
                            <div style="display:flex;align-items:center;gap:10px">
                              <div class="prompt-dots">
                                <span class="d1"></span><span class="d2"></span><span class="d3"></span>
                              </div>
                              <span class="prompt-meta">prompt.txt &nbsp;·&nbsp; {word_count} words &nbsp;·&nbsp; {char_count:,} chars &nbsp;·&nbsp; LLM INPUT</span>
                            </div>
                            <span class="prompt-meta">↓ copy via code block below</span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.code(prompt_used, language="text")
                        st.caption("☝️ Use the copy icon at the top-right of the code block to copy the entire prompt.")

                else:
                    status.update(label="❌  Pipeline Failed", state="error")
                    st.error("The agent ran but could not create test cases. Check your ticket description (min 50 words) and TestLink configuration.")

            except Exception as e:
                status.update(label="💥  Unexpected Error", state="error")
                st.error(f"**Agent crashed:** `{e}`")
