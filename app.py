# =============================================================================
# EMKAN FINANCE – Loan Application Demo (Light / Bright UI)
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
# STATE
# -----------------------------------------------------------------------------
# 0 Landing | 1 Registration | 2 Fetching | 3 Decision | 4 Processing | 5 Thank you
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
# CSS (LIGHT + BRIGHT + SMALL NAVY ACCENTS)
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { background: transparent !important; }

/* Page background (light, bright) */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"]{
  background: #F6F8FC !important;
}

/* Wider but centered */
.block-container{
  max-width: 1180px !important;
  padding-top: 1.2rem !important;
  padding-bottom: 2rem !important;
}

/* Palette */
:root{
  --navy:#2F2D5F;      /* Emkan deep tone - use lightly */
  --teal:#23C5A4;      /* CTA */
  --teal2:#7BE3D2;     /* highlight */
  --card:#FFFFFF;
  --border:#E6EEF7;
  --text:#0F172A;
  --muted:rgba(15,23,42,0.62);
  --soft:#F1F6FF;
}

/* Main card */
.shell{
  background: var(--card);
  border-radius: 22px;
  border: 1px solid var(--border);
  box-shadow: 0 18px 46px rgba(15,23,42,0.08);
  overflow: hidden;
}

/* Two columns: left slim brand panel + right content */
.inner{
  display:grid;
  grid-template-columns: 340px 1fr;
  min-height: 720px;
}
@media (max-width: 980px){
  .inner{ grid-template-columns: 1fr; }
  .leftBrand{ display:none; }
}

/* Left brand panel: light gradient, NOT dark */
.leftBrand{
  background:
    radial-gradient(circle at 30% 25%, rgba(35,197,164,0.28), rgba(35,197,164,0) 60%),
    linear-gradient(180deg, #F7FAFF 0%, #EEF4FF 55%, #F7FAFF 100%);
  border-right: 1px solid var(--border);
  padding: 20px;
}
.lbTitle{
  color: var(--navy);
  font-weight: 950;
  font-size: 1.05rem;
  letter-spacing: 0.2px;
}
.lbSub{
  margin-top: 6px;
  color: rgba(47,45,95,0.70);
  font-weight: 800;
  font-size: 0.93rem;
}
.heroMock{
  margin-top: 18px;
  width: 100%;
  height: 540px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(47,45,95,0.10), rgba(47,45,95,0.04));
  border: 1px solid rgba(47,45,95,0.10);
  position: relative;
  overflow:hidden;
}
.heroMock:before{
  content:"";
  position:absolute;
  left: -40px; top: -40px;
  width: 220px; height: 220px;
  background: radial-gradient(circle, rgba(35,197,164,0.35), rgba(35,197,164,0));
}
.heroMock:after{
  content:"";
  position:absolute;
  right: -60px; bottom: -60px;
  width: 260px; height: 260px;
  background: radial-gradient(circle, rgba(47,45,95,0.16), rgba(47,45,95,0));
}

/* Right content area */
.right{
  padding: 18px 22px 20px 22px;
}

/* Top bar inside */
.topbar{
  display:flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 14px;
}
.actions{
  display:flex; align-items:center; gap:12px;
  color: rgba(15,23,42,0.55);
  font-weight: 800;
  flex-wrap: wrap;
}
.pill{
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(35,197,164,0.16);
  border: 1px solid rgba(35,197,164,0.35);
  color: #136A5B;
  font-weight: 950;
}

/* Titles */
.h1{ font-size: 2.1rem; font-weight: 950; margin: 12px 0 6px 0; color: var(--text); }
.h2{ font-size: 1.02rem; font-weight: 850; color: rgba(15,23,42,0.62); margin: 0 0 14px 0; }

/* Info note */
.note{
  background: var(--soft);
  border: 1px solid #DCE7F7;
  padding: 12px 14px;
  border-radius: 14px;
  color: rgba(15,23,42,0.88);
  margin-bottom: 14px;
}

/* Sections */
.section{
  background:#FFFFFF;
  border:1px solid var(--border);
  border-radius:16px;
  padding:16px;
}

/* Widget theme */
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
  border: 1px solid rgba(35,197,164,0.85) !important;
  box-shadow: 0 0 0 4px rgba(35,197,164,0.14) !important;
}
label{ color: rgba(15,23,42,0.72) !important; font-weight: 850 !important; }

/* Buttons */
.stButton > button{
  background: var(--teal) !important;
  color: white !important;
  font-weight: 950 !important;
  border: none !important;
  padding: 0.85rem 1.1rem !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 22px rgba(35,197,164,0.20) !important;
}
.secondary .stButton > button{
  background: #FFFFFF !important;
  color: #0F172A !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
}

/* Footer */
.footer{
  margin-top: 16px;
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

    return s if len(s) <= 18 else s[:18] + "..."

def load_dataset_columns_and_sample():
    if not DATA_PATH.exists():
        return [], {}
    try:
        df = pd.read_excel(DATA_PATH, engine="openpyxl")
        cols = list(df.columns)
        sample_row = df.iloc[0].to_dict() if len(df) else {}
        return cols, sample_row
    except Exception:
        return [], {}

def topbar_block():
    logo_html = (
        f'<img src="data:image/png;base64,{LOGO_B64}" style="height:52px;" />'
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

# -----------------------------------------------------------------------------
# LAYOUT SHELL
# -----------------------------------------------------------------------------
st.markdown('<div class="shell"><div class="inner">', unsafe_allow_html=True)

# Left panel
st.markdown(
    """
<div class="leftBrand">
  <div class="lbTitle">EMKAN Finance Demo</div>
  <div class="lbSub">AI-assisted Loan Screening</div>
  <div class="heroMock"></div>
</div>
""",
    unsafe_allow_html=True,
)

# Right panel start
st.markdown('<div class="right">', unsafe_allow_html=True)

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
This demo simulates the real customer journey:
<b>Application</b> → <b>Data retrieval</b> (Core + SIMAH + National Address) → <b>Decision</b>.
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1.2, 1])
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

    bc1, bc2 = st.columns([0.35, 0.65])
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

    # Load dataset cols once
    if not st.session_state.dataset_cols:
        cols, sample = load_dataset_columns_and_sample()
        st.session_state.dataset_cols = cols
        st.session_state.dataset_sample = sample

    if not st.session_state.dataset_cols:
        st.warning(
            "Dataset columns could not be loaded. "
            "Make sure `openpyxl` is added to requirements.txt, then redeploy."
        )

    st.markdown(
        """
<div class="note">
Retrieving customer profile and required fields aligned with the training dataset schema.
</div>
""",
        unsafe_allow_html=True,
    )

    steps = [
        "Connecting to Core Loan System",
        "Retrieving SIMAH credit status",
        "Retrieving National Address",
        "Collecting device / IP / geo signals",
        "Loading full dataset schema fields",
        "Preparing automated decision",
    ]

    p = st.progress(0)
    msg = st.empty()

    # slower steps for committee
    for i, s in enumerate(steps, start=1):
        msg.info(s)
        time.sleep(1.2)
        p.progress(int(i / len(steps) * 55))

    st.markdown("### Retrieved fields (demo)")
    holder = st.container()

    cols_list = st.session_state.dataset_cols[:]
    sample = st.session_state.dataset_sample or {}

    if cols_list:
        # show first N gradually (still represent "all fields")
        # then show "and X more…" to keep UI clean
        MAX_SHOW = 55
        shown_cols = cols_list[:MAX_SHOW]
        remaining = max(0, len(cols_list) - MAX_SHOW)

        for idx, col_name in enumerate(shown_cols, start=1):
            v = sample.get(col_name, "")
            mv = mask_value(col_name, v)
            with holder:
                st.write(f"✅ **{col_name}**  —  `{mv}`")
            # slow reveal
            time.sleep(0.10)
            # progress continues smoothly
            p.progress(min(95, 55 + int((idx / max(1, len(shown_cols))) * 40)))

        if remaining > 0:
            st.info(f"…and **{remaining}** additional fields retrieved from the Core Loan System and government sources.")

    p.progress(100)
    st.success("Data retrieval completed successfully.")

    # 100% deterministic decision
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
<span style="opacity:0.75;">Policy: 3 × basic salary</span>
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
        time.sleep(0.02)
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

# Close right + inner + shell
st.markdown("</div></div></div>", unsafe_allow_html=True)
