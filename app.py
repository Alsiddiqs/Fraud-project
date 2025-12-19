# =============================================================================
# EMKAN FINANCE – Loan Application Demo (Full Blue Page + Slow Data Retrieval)
#
# Researchers:
#  - ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED
#  - MOHAMED ABDELSATART
# Supervisor:
#  - Dr. Khaled Eskaf
#
# Demo rule (hidden): Salary ODD -> Fraud, Salary EVEN -> Pass (100% deterministic)
# =============================================================================

import base64
import re
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EMKAN Finance | Apply for Finance",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LOGO_PATH = Path("emkan_logo.png")
DATA_PATH = Path("loan_applications_fraud_4400.xlsx")

def file_b64(p: Path):
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode("utf-8")
    return None

LOGO_B64 = file_b64(LOGO_PATH)

def parity_decision(salary: int) -> str:
    return "FRAUD" if (salary % 2 != 0) else "PASS"

# -----------------------------------------------------------------------------
# SESSION STATE
# 0 Landing
# 1 Registration
# 2 Fetching (slow)
# 3 Decision
# 4 Processing
# 5 Thank you
# -----------------------------------------------------------------------------
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
# CSS (FULL BLUE BACKGROUND + CENTERED CARD)
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { background: transparent !important; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"]{
  background: linear-gradient(180deg,#2F2D5F 0%, #27255A 55%, #23214F 100%) !important;
  color: #EAF0FF !important;
}

.block-container{
  max-width: 1280px !important;
  padding-top: 1.2rem !important;
  padding-bottom: 2.2rem !important;
}

:root{
  --emkan-navy:#2F2D5F;
  --emkan-teal:#23C5A4;
  --card:#FFFFFF;
  --border:#E5EDF7;
  --text:#0F172A;
  --muted:rgba(15,23,42,0.65);
}

/* Main white card (like the website content area) */
.shell{
  background: var(--card);
  border-radius: 22px;
  border: 1px solid rgba(229,237,247,0.7);
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  padding: 22px;
}

/* Inside layout */
.inner{
  display:grid;
  grid-template-columns: 420px 1fr;
  gap: 22px;
  align-items: start;
}
@media (max-width: 980px){
  .inner{ grid-template-columns: 1fr; }
  .leftHero{ display:none; }
}

.leftHero{
  border-radius: 18px;
  background:
    radial-gradient(circle at 30% 20%, rgba(255,255,255,0.14), rgba(255,255,255,0) 62%),
    linear-gradient(180deg, #3D3B6F 0%, #2F2D5F 100%);
  padding: 18px;
  min-height: 640px;
  overflow:hidden;
}
.heroTitle{ color: rgba(255,255,255,0.92); font-weight: 950; font-size: 1.05rem; }
.heroSub{ color: rgba(255,255,255,0.78); font-weight: 800; margin-top: 8px; font-size: 0.95rem; }
.heroPhone{
  width: 270px; height: 520px;
  border-radius: 40px;
  margin-top: 18px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 18px 60px rgba(0,0,0,0.25);
}

/* Top bar inside card */
.topbar{
  display:flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.actions{
  display:flex; align-items:center; gap:14px;
  font-weight: 850; color: rgba(15,23,42,0.55);
}
.pill{
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(35,197,164,0.14);
  border: 1px solid rgba(35,197,164,0.28);
  color: #167A67;
  font-weight: 950;
}

/* Typography */
.h1{ font-size: 2.1rem; font-weight: 950; margin: 8px 0 4px 0; color: var(--text); }
.h2{ font-size: 1.02rem; font-weight: 850; color: rgba(15,23,42,0.62); margin: 0 0 14px 0; }

.note{
  background: #F1F6FF;
  border: 1px solid #DCE7F7;
  padding: 12px 14px;
  border-radius: 14px;
  color: rgba(15,23,42,0.88);
  margin-bottom: 14px;
}

.section{
  background:#FFFFFF;
  border:1px solid var(--border);
  border-radius:16px;
  padding:16px;
}

/* Force widgets light */
[data-baseweb="input"] input,
textarea{
  background:#FFFFFF !important;
  color:#0F172A !important;
}
[data-baseweb="select"] > div{
  background:#FFFFFF !important;
  color:#0F172A !important;
}
[data-baseweb="input"] > div,
[data-baseweb="select"] > div{
  border: 1px solid #D6E2F2 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
}
[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"] > div:focus-within{
  border: 1px solid rgba(35,197,164,0.75) !important;
  box-shadow: 0 0 0 4px rgba(35,197,164,0.12) !important;
}
label{ color: rgba(15,23,42,0.72) !important; font-weight: 850 !important; }

/* Buttons */
.stButton > button{
  background: var(--emkan-teal) !important;
  color: white !important;
  font-weight: 950 !important;
  border: none !important;
  padding: 0.85rem 1.2rem !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 22px rgba(35,197,164,0.22) !important;
}
.secondary .stButton > button{
  background: #FFFFFF !important;
  color: #0F172A !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
}

/* Footer */
.footer{
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  color: rgba(15,23,42,0.70);
  font-size: 0.92rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
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
        if len(digits) >= 4:
            return f"+966 *** *** {digits[-4:]}"
        return "+966 ***"
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
    return s if len(s) <= 18 else s[:18] + "..."

def load_dataset_columns_and_sample():
    """
    Loads dataset to show "retrieving all customer fields".
    Falls back gracefully if openpyxl missing.
    """
    if not DATA_PATH.exists():
        return [], {}

    try:
        df = pd.read_excel(DATA_PATH, engine="openpyxl")
        cols = list(df.columns)
        sample_row = df.iloc[0].to_dict() if len(df) else {}
        return cols, sample_row
    except Exception:
        # If openpyxl missing or file read fails, show only columns via fallback message
        return [], {}

def footer_block():
    st.markdown(
        """
<div class="footer">
  <div><b>Researchers:</b> ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED &amp; MOHAMED ABDELSATART</div>
  <div><b>Supervisor:</b> Dr. Khaled Eskaf</div>
  <div style="margin-top:6px;">Master's Thesis Project | Midocean University | 2025</div>
</div>
""",
        unsafe_allow_html=True,
    )

def topbar_block():
    logo_html = (
        f'<img src="data:image/png;base64,{LOGO_B64}" style="height:54px;" />'
        if LOGO_B64
        else '<div style="font-weight:950; font-size:1.5rem; color:#2F2D5F;">EMKAN</div>'
    )
    st.markdown(
        f"""
<div class="topbar">
  <div class="actions">
    <span>Don't have an account?</span>
    <span style="text-decoration:underline;">Create an account</span>
    <span class="pill">login</span>
  </div>
  <div>{logo_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# MAIN SHELL
# -----------------------------------------------------------------------------
st.markdown('<div class="shell"><div class="inner">', unsafe_allow_html=True)

# Left hero
st.markdown(
    """
<div class="leftHero">
  <div class="heroTitle">EMKAN Finance Demo</div>
  <div class="heroSub">AI-assisted Loan Screening</div>
  <div class="heroPhone"></div>
</div>
""",
    unsafe_allow_html=True,
)

# Right content container start
st.markdown("<div>", unsafe_allow_html=True)

topbar_block()

# -----------------------------------------------------------------------------
# PAGES
# -----------------------------------------------------------------------------
if st.session_state.page == 0:
    st.markdown('<div class="h1">Apply for Finance with EMKAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">Fast, simple, and easy to use.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="note">
This demo simulates the real journey:
Application → Data retrieval (Core + SIMAH + National Address) → Decision.
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Get Started", use_container_width=True):
            st.session_state.page = 1
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == 1:
    st.markdown('<div class="h1">Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">Your information</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="note">
Customer enters only basic information. Remaining information is retrieved automatically from core systems and government sources.
</div>
""",
        unsafe_allow_html=True,
    )

    with st.form("reg_form"):
        a, b = st.columns(2)

        with a:
            full_name = st.text_input("Full name", placeholder="e.g., Mohammed Ahmed Alomari")
            age = st.number_input("Age", min_value=18, max_value=65, value=30)
            sector = st.selectbox("Employment sector", ["Private", "Government", "Semi-government"])
            national_id = st.text_input("National ID / Iqama", max_chars=10, placeholder="1XXXXXXXXX")

        with b:
            phone = st.text_input("Mobile number", placeholder="+966 5XXXXXXXX")
            email = st.text_input("Email address", placeholder="example@email.com")
            salary = st.number_input("Basic monthly salary (SAR)", min_value=0, max_value=1_000_000, value=15000, step=1)
            requested = st.number_input("Requested finance amount (SAR)", min_value=2000, max_value=1_500_000, value=50000, step=1000)

        submit = st.form_submit_button("Submit application")

    if submit:
        if not full_name or not phone or not email or not national_id:
            st.warning("Please complete: Full name, National ID/Iqama, Mobile number, Email.")
        else:
            st.session_state.app = {
                "full_name": full_name.strip(),
                "age": int(age),
                "sector": sector,
                "national_id": national_id.strip(),
                "phone": phone.strip(),
                "email": email.strip(),
                "salary": int(salary),
                "requested": float(requested),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
            st.session_state.page = 2
            st.rerun()

    bc1, bc2 = st.columns([0.4, 0.6])
    with bc1:
        st.markdown('<div class="secondary">', unsafe_allow_html=True)
        if st.button("Back", use_container_width=True):
            st.session_state.page = 0
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == 2:
    st.markdown('<div class="h1">Fetching your data</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">Core Systems + SIMAH + National Address…</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="note">
In this step, the system retrieves <b>all required customer fields</b> from the Core Loan System and government sources,
matching the training dataset structure.
</div>
""",
        unsafe_allow_html=True,
    )

    # Load dataset columns once
    if not st.session_state.dataset_cols:
        cols, sample = load_dataset_columns_and_sample()
        st.session_state.dataset_cols = cols
        st.session_state.dataset_sample = sample

    # If dataset couldn't be loaded, show a clear message (still continue demo)
    if not st.session_state.dataset_cols:
        st.warning(
            "Dataset columns could not be loaded (likely missing openpyxl). "
            "Add openpyxl to requirements.txt, then redeploy."
        )

    steps = [
        "Connecting to Core Loan System",
        "Retrieving SIMAH credit status",
        "Retrieving National Address",
        "Collecting device / IP / geo signals",
        "Loading all customer fields from dataset schema",
        "Preparing automated decision",
    ]

    p = st.progress(0)
    msg = st.empty()

    for i, s in enumerate(steps, start=1):
        msg.info(s)
        time.sleep(1.0)  # slower for committee understanding
        p.progress(int(i / len(steps) * 100))

    st.markdown("### Retrieved fields (demo)")
    holder = st.container()
    shown = 0

    cols_list = st.session_state.dataset_cols[:]
    sample = st.session_state.dataset_sample or {}

    # Slow reveal of columns
    if cols_list:
        for col_name in cols_list:
            shown += 1
            with holder:
                # show masked sample value if exists
                v = sample.get(col_name, "")
                mv = mask_value(col_name, v)
                st.write(f"✅ **{col_name}**  —  `{mv}`")
            time.sleep(0.12)  # slow reveal of each field

            # keep progress moving during reveal
            if shown % 10 == 0:
                p.progress(min(100, 60 + int((shown / max(1, len(cols_list))) * 40)))

    st.success("Data retrieval completed (Core + Government sources + Full dataset schema).")

    # 결정 (100% deterministic)
    salary = int(st.session_state.app["salary"])
    st.session_state.decision = parity_decision(salary)
    st.session_state.offer = float(salary * 3)

    st.markdown("</div>", unsafe_allow_html=True)

    time.sleep(0.4)
    st.session_state.page = 3
    st.rerun()

elif st.session_state.page == 3:
    decision = st.session_state.decision
    salary = int(st.session_state.app.get("salary", 0))

    st.markdown('<div class="h1">Decision</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">Automated assessment result</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)

    if decision == "PASS":
        offer = float(st.session_state.offer or (salary * 3))
        st.success("Pre-approved. Offer generated successfully.")
        st.markdown(
            f"""
<div class="note">
<b>Offer amount:</b> {offer:,.0f} SAR<br>
<span style="opacity:0.75;">(Policy: 3 × basic salary)</span>
</div>
""",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Approve offer", use_container_width=True):
                st.session_state.page = 4
                st.rerun()
        with c2:
            st.markdown('<div class="secondary">', unsafe_allow_html=True)
            if st.button("Reject offer", use_container_width=True):
                st.session_state.page = 5
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error("Your application will be transferred to the Sales / Verification team.")
        st.markdown(
            """
<div class="note">
Our team will contact you to request additional information to complete your application.
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button("OK", use_container_width=True):
            st.session_state.page = 4
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == 4:
    st.markdown('<div class="h1">Processing</div>', unsafe_allow_html=True)
    st.markdown('<div class="h2">We are working on your application.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.markdown(
        """
<div class="note">
Your request is being processed. We will contact you within <b>24 hours</b>.
</div>
""",
        unsafe_allow_html=True,
    )

    p = st.progress(0)
    for i in range(100):
        time.sleep(0.02)  # slower
        p.progress(i + 1)

    st.success("Application received successfully.")
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

    st.markdown('<div class="section">', unsafe_allow_html=True)

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

footer_block()

# right end + inner + shell end
st.markdown("</div></div></div>", unsafe_allow_html=True)
