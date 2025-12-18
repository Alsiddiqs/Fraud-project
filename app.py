# =============================================================================
# EMKAN FINANCE – Loan Application Demo (Responsive / Light Theme)
#
# Researchers:
#  - ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED
#  - MOHAMED ABDELSATART
# Supervisor:
#  - Dr. Khaled Eskaf
#
# Demo logic (hidden): Salary ODD -> Fraud, Salary EVEN -> Pass (100%).
# =============================================================================

import base64
import time
from datetime import datetime
from pathlib import Path

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

def _logo_b64():
    if LOGO_PATH.exists():
        return base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    return None

LOGO_B64 = _logo_b64()

def parity_decision(salary: int) -> str:
    return "FRAUD" if (salary % 2 != 0) else "PASS"

# -----------------------------------------------------------------------------
# SESSION STATE PAGES
# 0 Landing
# 1 Registration
# 2 Fetching
# 3 Decision (Offer or Refer)
# 4 Processing (24h)
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

# -----------------------------------------------------------------------------
# FORCE LIGHT UI + EMKAN BRAND CSS (Responsive)
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
/* ===== Force light look even if Streamlit/Dark mode ===== */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background: #f7f9fc !important;
  color: #0f172a !important;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ===== Page container ===== */
.block-container {
  padding-top: 1.2rem !important;
  padding-bottom: 2.0rem !important;
  max-width: 1200px !important;
}

/* ===== Brand palette (close to EMKAN logo) ===== */
:root{
  --emkan-navy: #2f2d5f;
  --emkan-teal: #23c5a4;
  --emkan-bg: #f7f9fc;
  --card: #ffffff;
  --border: #e7eef6;
  --text: #0f172a;
  --muted: rgba(15, 23, 42, 0.65);
}

/* ===== Topbar ===== */
.topbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.topbar .right{
  display:flex;
  align-items:center;
  gap: 14px;
  font-weight: 700;
  color: var(--muted);
}
.pill{
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(35,197,164,0.12);
  border: 1px solid rgba(35,197,164,0.25);
  color: #167a67;
  font-weight: 900;
}
.logo img{
  height: 56px;
  display:block;
}

/* ===== Layout columns ===== */
.leftPanel{
  border-radius: 22px;
  background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.12), rgba(255,255,255,0) 60%),
              linear-gradient(180deg, #3d3b6f 0%, #2f2d5f 100%);
  padding: 22px;
  min-height: 520px;
  position: relative;
  overflow: hidden;
}
.leftPanel .title{
  color: rgba(255,255,255,0.92);
  font-weight: 900;
  letter-spacing: 0.3px;
  margin-bottom: 6px;
}
.leftPanel .sub{
  color: rgba(255,255,255,0.75);
  font-weight: 700;
  font-size: 0.95rem;
}
.mock{
  width: 250px; height: 470px;
  border-radius: 38px;
  margin-top: 18px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 18px 60px rgba(0,0,0,0.25);
}

/* Hide left panel on small screens */
@media (max-width: 980px){
  .leftPanel { display:none; }
}

/* ===== Cards / typography ===== */
.h1{
  font-size: 2.2rem;
  font-weight: 950;
  color: var(--text);
  margin: 10px 0 6px 0;
}
.h2{
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--muted);
  margin: 0 0 18px 0;
}
.card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 8px 26px rgba(2,6,23,0.05);
}
.note{
  background: #f1f6ff;
  border: 1px solid #dfe9f7;
  padding: 12px 14px;
  border-radius: 14px;
  color: rgba(15,23,42,0.82);
  margin-bottom: 14px;
}

/* ===== Buttons ===== */
.stButton > button{
  background: var(--emkan-teal) !important;
  color: white !important;
  font-weight: 900 !important;
  border: none !important;
  padding: 0.85rem 1.2rem !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 22px rgba(35,197,164,0.22) !important;
}
.secondary .stButton > button{
  background: #ffffff !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
}

/* ===== Progress style (remove ugly white bars feeling) ===== */
[data-testid="stProgress"] > div > div{
  border-radius: 999px !important;
}

/* ===== Footer ===== */
.footer{
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
  color: rgba(15,23,42,0.70);
  font-size: 0.92rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# TOPBAR (Logo + actions)
# -----------------------------------------------------------------------------
top_left, top_right = st.columns([0.55, 0.45])
with top_left:
    st.markdown(
        """
<div class="topbar">
  <div class="right">
    <span>Don't have an account?</span>
    <span style="text-decoration:underline; cursor:default;">Create an account</span>
    <span class="pill">login</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with top_right:
    if LOGO_B64:
        st.markdown(f'<div class="logo" style="display:flex; justify-content:flex-end;"><img src="data:image/png;base64,{LOGO_B64}"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:right; font-weight:950; font-size:1.6rem; color:#2f2d5f;">EMKAN</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN LAYOUT (Left illustration + Right content)
# -----------------------------------------------------------------------------
lcol, rcol = st.columns([0.36, 0.64], gap="large")

with lcol:
    st.markdown(
        """
<div class="leftPanel">
  <div class="title">EMKAN Finance Demo</div>
  <div class="sub">AI-assisted Loan Screening</div>
  <div class="mock"></div>
</div>
""",
        unsafe_allow_html=True,
    )

with rcol:
    # -------------------------------------------------------------------------
    # PAGE 0: LANDING
    # -------------------------------------------------------------------------
    if st.session_state.page == 0:
        st.markdown('<div class="h1">Apply for Finance with EMKAN</div>', unsafe_allow_html=True)
        st.markdown('<div class="h2">Fast, simple, and easy to use.</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            """
<div class="note">
This demo simulates a real customer journey:
Application → Data retrieval (Core + SIMAH + National Address) → Automated decision.
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

    # -------------------------------------------------------------------------
    # PAGE 1: REGISTRATION
    # -------------------------------------------------------------------------
    elif st.session_state.page == 1:
        st.markdown('<div class="h1">Registration</div>', unsafe_allow_html=True)
        st.markdown('<div class="h2">Your information</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            """
<div class="note">
Customer enters only basic information. The remaining data is retrieved automatically from core systems and government sources.
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

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="secondary">', unsafe_allow_html=True)
        if st.button("Back", use_container_width=True):
            st.session_state.page = 0
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # PAGE 2: FETCHING
    # -------------------------------------------------------------------------
    elif st.session_state.page == 2:
        st.markdown('<div class="h1">Fetching your data</div>', unsafe_allow_html=True)
        st.markdown('<div class="h2">Retrieving from Core Systems + SIMAH + National Address…</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)

        steps = [
            "Connecting to Core Loan System",
            "Retrieving SIMAH credit status",
            "Retrieving National Address",
            "Collecting device / IP / geo signals",
            "Preparing automated decision",
        ]

        p = st.progress(0)
        msg = st.empty()

        for i, s in enumerate(steps, start=1):
            msg.info(s)
            time.sleep(0.6)
            p.progress(int(i / len(steps) * 100))

        salary = int(st.session_state.app["salary"])
        st.session_state.decision = parity_decision(salary)
        st.session_state.offer = float(salary * 3)

        st.success("Data retrieval completed.")
        st.markdown("</div>", unsafe_allow_html=True)

        time.sleep(0.25)
        st.session_state.page = 3
        st.rerun()

    # -------------------------------------------------------------------------
    # PAGE 3: DECISION
    # -------------------------------------------------------------------------
    elif st.session_state.page == 3:
        decision = st.session_state.decision
        salary = int(st.session_state.app.get("salary", 0))

        st.markdown('<div class="h1">Decision</div>', unsafe_allow_html=True)
        st.markdown('<div class="h2">Automated assessment result</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)

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

    # -------------------------------------------------------------------------
    # PAGE 4: PROCESSING (24h)
    # -------------------------------------------------------------------------
    elif st.session_state.page == 4:
        st.markdown('<div class="h1">Processing</div>', unsafe_allow_html=True)
        st.markdown('<div class="h2">We are working on your application.</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            """
<div class="note">
Your request is being processed. We will contact you within <b>24 hours</b>.
</div>
""",
            unsafe_allow_html=True,
        )

        # clean minimal progress (no extra empty boxes)
        p = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            p.progress(i + 1)

        st.success("Application received successfully.")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Start a new application", use_container_width=True):
            st.session_state.page = 0
            st.session_state.app = {}
            st.session_state.decision = None
            st.session_state.offer = None
            st.rerun()

    # -------------------------------------------------------------------------
    # PAGE 5: THANK YOU
    # -------------------------------------------------------------------------
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
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Start a new application", use_container_width=True):
            st.session_state.page = 0
            st.session_state.app = {}
            st.session_state.decision = None
            st.session_state.offer = None
            st.rerun()

    # -------------------------------------------------------------------------
    # FOOTER (Correct supervisor name)
    # -------------------------------------------------------------------------
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
