# =============================================================================
# EMKAN FINANCE – Loan Application Demo (Multi-page, English UI)
#
# Researchers:
#   ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED
#   MOHAMED ABDELSATART
# Supervisor:
#   Dr. Khaled Iskaf
#
# Notes:
# - UI is English only.
# - Deterministic outcome (Odd/Even salary) for demo control (NOT shown to user).
# - Offer amount is computed internally; NO policy text is displayed anywhere.
# - Data retrieval page references the dataset columns and shows them slowly.
# =============================================================================

import base64
import re
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIG / PATHS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EMKAN Finance | Apply for Finance",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LOGO_PATH = Path("emkan_logo.png")                     # uploaded logo in repo
DATA_PATH = Path("loan_applications_fraud_4400.xlsx")  # dataset in repo

# Palette (as you requested)
PRIMARY_BG = "#EEF4FF"   # light bluish main background
ACCENT_BLUE = "#3B82F6"  # medium blue
TEXT_STRONG = "#1F2A44"
BORDER = "#D6E4FF"
CARD_BG = "#FFFFFF"

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def b64_image(path: Path):
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("utf-8")

LOGO_B64 = b64_image(LOGO_PATH)

def mask_value(key: str, value):
    s = "" if value is None else str(value)
    k = key.lower()

    if "email" in k:
        if "@" in s:
            u, d = s.split("@", 1)
            u2 = (u[:2] + "***") if len(u) >= 2 else "***"
            return f"{u2}@{d}"
        return "***@***"

    if "phone" in k or "mobile" in k:
        digits = re.sub(r"\D", "", s)
        return f"+966 *** *** {digits[-4:]}" if len(digits) >= 4 else "+966 ***"

    if "id" in k or "iqama" in k or "national" in k:
        digits = re.sub(r"\D", "", s)
        if len(digits) >= 4:
            return f"{digits[:2]}******{digits[-2:]}"
        return "**********"

    if "name" in k:
        parts = s.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1][0]}***"
        return s[:2] + "***" if len(s) >= 2 else "***"

    return s if len(s) <= 22 else s[:22] + "..."

def safe_read_excel_columns(path: Path):
    """
    Reads dataset columns + a sample row (for demo display).
    Requires openpyxl in requirements.txt.
    """
    if not path.exists():
        return [], {}

    try:
        df = pd.read_excel(path, engine="openpyxl")
        cols = list(df.columns)
        sample = df.iloc[0].to_dict() if len(df) else {}
        return cols, sample
    except Exception:
        return [], {}

def deterministic_decision(salary: int) -> str:
    # Hidden demo control: Odd -> Fraud, Even -> Pass
    return "FRAUD" if (salary % 2 != 0) else "PASS"

def compute_offer_amount(salary: int) -> float:
    # Internal only. Do not display any policy text.
    return float(salary * 3)

# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
# Pages:
# 0 Landing | 1 Application | 2 Fetching | 3 Decision | 4 Processing | 5 Thank you
if "page" not in st.session_state:
    st.session_state.page = 0
if "app" not in st.session_state:
    st.session_state.app = {}
if "decision" not in st.session_state:
    st.session_state.decision = None
if "offer" not in st.session_state:
    st.session_state.offer = None
if "dataset_cols" not in st.session_state:
    st.session_state.dataset_cols = []
if "dataset_sample" not in st.session_state:
    st.session_state.dataset_sample = {}

# -----------------------------------------------------------------------------
# CSS (LIGHT, BALANCED, NO HEAVY DARK BLUE)
# -----------------------------------------------------------------------------
st.markdown(
    f"""
<style>
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stHeader"] {{ background: transparent !important; }}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
  background: {PRIMARY_BG} !important;
}}

.block-container {{
  max-width: 1180px !important;
  padding-top: 1.1rem !important;
  padding-bottom: 2rem !important;
}}

:root {{
  --bg: {PRIMARY_BG};
  --accent: {ACCENT_BLUE};
  --text: {TEXT_STRONG};
  --border: {BORDER};
  --card: {CARD_BG};
}}

.shell {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 22px;
  box-shadow: 0 18px 46px rgba(15,23,42,0.08);
  overflow: hidden;
}}

.inner {{
  display:grid;
  grid-template-columns: 340px 1fr;
  min-height: 760px;
}}
@media (max-width: 980px){{
  .inner{{ grid-template-columns: 1fr; }}
  .leftBrand{{ display:none; }}
}}

.leftBrand {{
  background:
    radial-gradient(circle at 30% 25%, rgba(59,130,246,0.18), rgba(59,130,246,0) 60%),
    linear-gradient(180deg, #F7FAFF 0%, #EEF4FF 55%, #F7FAFF 100%);
  border-right: 1px solid var(--border);
  padding: 18px;
}}

.brandTitle {{
  color: var(--text);
  font-weight: 950;
  font-size: 1.02rem;
}}
.brandSub {{
  margin-top: 6px;
  color: rgba(31,42,68,0.70);
  font-weight: 800;
  font-size: 0.92rem;
}}
.brandArt {{
  margin-top: 16px;
  width: 100%;
  height: 560px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(59,130,246,0.10), rgba(59,130,246,0.04));
  border: 1px solid rgba(59,130,246,0.10);
  position: relative;
  overflow:hidden;
}}
.brandArt:before {{
  content:"";
  position:absolute;
  left:-50px; top:-50px;
  width: 230px; height: 230px;
  background: radial-gradient(circle, rgba(59,130,246,0.20), rgba(59,130,246,0));
}}
.brandArt:after {{
  content:"";
  position:absolute;
  right:-70px; bottom:-70px;
  width: 280px; height: 280px;
  background: radial-gradient(circle, rgba(31,42,68,0.10), rgba(31,42,68,0));
}}

.right {{
  padding: 18px 22px 22px 22px;
}}

.topbar {{
  display:flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 14px;
}}

.h1 {{
  font-size: 2.05rem;
  font-weight: 950;
  margin: 12px 0 6px 0;
  color: var(--text);
}}
.h2 {{
  font-size: 1.02rem;
  font-weight: 800;
  color: rgba(31,42,68,0.62);
  margin: 0 0 14px 0;
}}

.card {{
  background: #FFFFFF;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
}}

.note {{
  background: #F6FAFF;
  border: 1px solid #DCEBFF;
  border-radius: 14px;
  padding: 12px 14px;
  color: rgba(31,42,68,0.88);
  margin-bottom: 14px;
}}

[data-baseweb="input"] > div,
[data-baseweb="select"] > div {{
  border: 1px solid #D6E2F2 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  background: #FFFFFF !important;
}}
[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"] > div:focus-within {{
  border: 1px solid rgba(59,130,246,0.85) !important;
  box-shadow: 0 0 0 4px rgba(59,130,246,0.14) !important;
}}
label {{
  color: rgba(31,42,68,0.72) !important;
  font-weight: 850 !important;
}}

.stButton > button {{
  background: var(--accent) !important;
  color: white !important;
  font-weight: 950 !important;
  border: 1px solid var(--accent) !important;
  padding: 0.85rem 1.1rem !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 22px rgba(59,130,246,0.20) !important;
}}

.secondary .stButton > button {{
  background: #FFFFFF !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
}}

.footer {{
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  color: rgba(31,42,68,0.70);
  font-size: 0.92rem;
}}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# UI BLOCKS
# -----------------------------------------------------------------------------
def render_topbar():
    if LOGO_B64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:48px;" />'
    else:
        logo_html = '<div style="font-weight:950; font-size:1.4rem; color:#1F2A44;">EMKAN</div>'

    st.markdown(
        f"""
<div class="topbar">
  <div style="display:flex; gap:10px; align-items:center; color:rgba(31,42,68,0.55); font-weight:800;">
    <span>Already have an account?</span>
    <span style="text-decoration:underline;">login</span>
  </div>
  <div>{logo_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

def render_footer():
    st.markdown(
        """
<div class="footer">
  <div><b>Researchers:</b> ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED &nbsp;|&nbsp; MOHAMED ABDELSATART</div>
  <div><b>Supervisor:</b> Dr. Khaled Iskaf</div>
  <div style="margin-top:6px;">Master's Thesis Project | Midocean University | 2025</div>
</div>
""",
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# SHELL START
# -----------------------------------------------------------------------------
st.markdown('<div class="shell"><div class="inner">', unsafe_allow_html=True)

st.markdown(
    """
<div class="leftBrand">
  <div class="brandTitle">EMKAN Finance Demo</div>
  <div class="brandSub">Loan application journey</div>
  <div class="brandArt"></div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="right">', unsafe_allow_html=True)
render_topbar()

# -----------------------------------------------------------------------------
# PAGES
# -----------------------------------------------------------------------------
if st.session_state.page == 0:
    st.markdown('<div class="h1">Apply for Finance</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">Fast, simple, and secure.</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="note">
This demo simulates a real customer journey: application → data retrieval → decision.
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if st.button("Get started", use_container_width=True):
            st.session_state.page = 1
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == 1:
    st.markdown('<div class="h1">Application</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">Enter your basic information</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    with st.form("application_form"):
        a, b = st.columns(2)

        with a:
            full_name = st.text_input("Full name", placeholder="e.g., Mohammed Ahmed Alomari")
            age = st.number_input("Age", min_value=18, max_value=65, value=30)
            employment_sector = st.selectbox("Employment sector", ["Private", "Government", "Semi-government"])
            national_id = st.text_input("National ID / Iqama", max_chars=10, placeholder="1XXXXXXXXX")

        with b:
            phone = st.text_input("Mobile number", placeholder="+966 5XXXXXXXX")
            email = st.text_input("Email address", placeholder="example@email.com")
            salary = st.number_input("Basic monthly salary (SAR)", min_value=0, max_value=1_000_000, value=15000, step=1)
            requested_amount = st.number_input("Requested finance amount (SAR)", min_value=2000, max_value=1_500_000, value=50000, step=1000)

        submitted = st.form_submit_button("Submit application")

    if submitted:
        if not full_name or not phone or not email or not national_id:
            st.warning("Please complete: Full name, National ID/Iqama, Mobile number, Email.")
        else:
            st.session_state.app = {
                "full_name": full_name.strip(),
                "age": int(age),
                "employment_sector": employment_sector,
                "national_id": national_id.strip(),
                "phone": phone.strip(),
                "email": email.strip(),
                "salary": int(salary),
                "requested_amount": float(requested_amount),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
            st.session_state.page = 2
            st.rerun()

    bc1, bc2 = st.columns([0.30, 0.70])
    with bc1:
        st.markdown('<div class="secondary">', unsafe_allow_html=True)
        if st.button("Back", use_container_width=True):
            st.session_state.page = 0
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == 2:
    st.markdown('<div class="h1">Fetching data</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">Connecting to core systems and external sources…</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Load dataset cols once
    if not st.session_state.dataset_cols:
        cols, sample = safe_read_excel_columns(DATA_PATH)
        st.session_state.dataset_cols = cols
        st.session_state.dataset_sample = sample

    if not st.session_state.dataset_cols:
        st.error(
            "Dataset could not be loaded.\n\n"
            "Please ensure:\n"
            "1) The file exists in the repo: loan_applications_fraud_4400.xlsx\n"
            "2) requirements.txt includes: openpyxl\n"
        )

    st.markdown(
        """
<div class="note">
Retrieving full customer profile and required fields aligned with the dataset schema.
</div>
""",
        unsafe_allow_html=True,
    )

    steps = [
        "Connecting to Core Loan System",
        "Retrieving SIMAH credit information",
        "Retrieving National Address",
        "Collecting device, IP and geo signals",
        "Loading required data fields",
        "Finalizing assessment",
    ]

    progress = st.progress(0)
    msg = st.empty()

    # Slow enough for committee
    for i, s in enumerate(steps, start=1):
        msg.info(s)
        time.sleep(1.25)
        progress.progress(int(i / len(steps) * 55))

    st.markdown("### Retrieved fields")
    holder = st.container()

    cols_list = st.session_state.dataset_cols[:]
    sample = st.session_state.dataset_sample or {}

    if cols_list:
        MAX_SHOW = 60  # show a good amount, keep UI clean
        shown = cols_list[:MAX_SHOW]
        remaining = max(0, len(cols_list) - MAX_SHOW)

        for idx, col_name in enumerate(shown, start=1):
            v = sample.get(col_name, "")
            mv = mask_value(col_name, v)
            with holder:
                st.write(f"✅ **{col_name}** — `{mv}`")
            time.sleep(0.11)
            progress.progress(min(95, 55 + int((idx / max(1, len(shown))) * 40)))

        if remaining > 0:
            st.info(f"Additional fields retrieved: {remaining}")

    progress.progress(100)
    st.success("Data retrieval completed.")

    # Deterministic output (hidden)
    salary = int(st.session_state.app.get("salary", 0))
    st.session_state.decision = deterministic_decision(salary)
    st.session_state.offer = compute_offer_amount(salary)

    time.sleep(0.35)
    st.session_state.page = 3
    st.rerun()

elif st.session_state.page == 3:
    st.markdown('<div class="h1">Result</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">Application status</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    decision = st.session_state.decision
    salary = int(st.session_state.app.get("salary", 0))

    if decision == "PASS":
        offer = float(st.session_state.offer or 0)

        st.success("Your application is eligible for an offer.")

        # No policy text shown
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Offer amount (SAR)", f"{offer:,.0f}")
        with c2:
            st.metric("Basic monthly salary (SAR)", f"{salary:,.0f}")

        st.markdown("<br>", unsafe_allow_html=True)
        a, b = st.columns(2)

        with a:
            if st.button("Approve", use_container_width=True):
                st.session_state.page = 4
                st.rerun()
        with b:
            st.markdown('<div class="secondary">', unsafe_allow_html=True)
            if st.button("Reject", use_container_width=True):
                st.session_state.page = 5
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error("Your application will be transferred to our Sales / Verification team.")
        st.markdown(
            """
<div class="note">
Our team will contact you to request additional information to complete the application.
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button("Continue", use_container_width=True):
            st.session_state.page = 4
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == 4:
    st.markdown('<div class="h1">Processing</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">We are working on your request.</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        """
<div class="note">
Your request is being processed. We will contact you within 24 hours.
</div>
""",
        unsafe_allow_html=True,
    )

    p = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        p.progress(i + 1)

    st.success("Request received successfully.")

    if st.button("Start a new application", use_container_width=True):
        st.session_state.page = 0
        st.session_state.app = {}
        st.session_state.decision = None
        st.session_state.offer = None
        st.session_state.dataset_cols = []
        st.session_state.dataset_sample = {}
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == 5:
    st.markdown('<div class="h1">Thank you</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">Thank you for contacting EMKAN Finance.</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="note">
We appreciate your time. You can apply again at any time.
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("Start a new application", use_container_width=True):
        st.session_state.page = 0
        st.session_state.app = {}
        st.session_state.decision = None
        st.session_state.offer = None
        st.session_state.dataset_cols = []
        st.session_state.dataset_sample = {}
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

render_footer()

# -----------------------------------------------------------------------------
# SHELL END
# -----------------------------------------------------------------------------
st.markdown("</div></div></div>", unsafe_allow_html=True)
