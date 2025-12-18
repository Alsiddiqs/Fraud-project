# =============================================================================
# EMKAN FINANCE – AI Loan Application Demo (Streamlit Cloud Ready)
#
# Researchers:
#  - ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED
#  - MOHAMED ABDELSATART
# Supervisor:
#  - Dr. Khaled Eskaf
#
# Notes:
# - UI-only demo journey (no model re-training).
# - Deterministic control for demo: salary odd -> Fraud, even -> Pass (100%).
# =============================================================================

import base64
import time
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EMKAN Finance | Apply for Finance",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Assets / files
# -----------------------------------------------------------------------------
MODEL_PATH = Path("Final_model.pkl")
DATA_PATH = Path("loan_applications_fraud_4400.xlsx")
LOGO_PATH = Path("emkan_logo.png")

# -----------------------------------------------------------------------------
# Styling (Streamlit-friendly)
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
/* Reduce default padding */
.block-container { padding-top: 1.0rem; padding-bottom: 2rem; }
header, footer { visibility: hidden; }

/* Left panel */
.leftPanel {
  min-height: calc(100vh - 60px);
  border-radius: 18px;
  background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.10), rgba(255,255,255,0.0) 60%),
              linear-gradient(180deg, #3d3b6f 0%, #34335f 100%);
  padding: 2.0rem;
  position: relative;
  overflow: hidden;
}
.lpShape1 {
  position:absolute; left:-70px; top:-60px; width:240px; height:240px;
  border-radius:60px; background:rgba(255,255,255,0.08); transform:rotate(18deg);
}
.lpShape2 {
  position:absolute; left:20px; top:160px; width:210px; height:210px;
  border-radius:55px; background:rgba(255,255,255,0.05); transform:rotate(-12deg);
}
.phoneMock {
  width: 260px; height: 500px; border-radius: 38px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 18px 60px rgba(0,0,0,0.25);
  margin-top: 2.5rem;
}
.lpBrand {
  color: rgba(255,255,255,0.92);
  font-weight: 900;
  letter-spacing: 0.4px;
  font-size: 1.05rem;
}
.lpBrand small { display:block; opacity:0.75; font-weight:700; margin-top:6px; }

/* Right panel top bar */
.topbar {
  display:flex; align-items:center; justify-content:space-between;
  margin-bottom: 1.2rem;
}
.loginRow {
  display:flex; align-items:center; gap:14px;
  opacity:0.85; font-weight:700;
}
.badge {
  padding: 10px 14px;
  background: rgba(35, 197, 164, 0.18);
  border: 1px solid rgba(35, 197, 164, 0.25);
  border-radius: 12px;
  font-weight: 900;
  color: #1b7b6a;
}

/* Titles */
.hTitle { font-size: 2.1rem; font-weight: 900; color: #0f172a; margin: 0.4rem 0 0.2rem 0; }
.hSub { margin: 0; opacity: 0.70; font-size: 1.05rem; }

/* Card */
.card {
  border: 1px solid #eef2f7;
  background: #ffffff;
  border-radius: 18px;
  padding: 1.6rem;
  box-shadow: 0 8px 28px rgba(2,6,23,0.06);
  margin-top: 1.0rem;
}
.note {
  padding: 14px 16px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  margin: 0.8rem 0 1.2rem 0;
  color: #0f172a;
  opacity: 0.92;
}
.good {
  padding: 16px 16px;
  border-radius: 16px;
  background: rgba(16,185,129,0.13);
  border: 1px solid rgba(16,185,129,0.22);
  font-weight: 900;
}
.bad {
  padding: 16px 16px;
  border-radius: 16px;
  background: rgba(239,68,68,0.10);
  border: 1px solid rgba(239,68,68,0.22);
  font-weight: 900;
}

/* Buttons */
.stButton > button {
  background: #23c5a4 !important;
  color: white !important;
  font-weight: 900 !important;
  border: none !important;
  padding: 0.85rem 1.2rem !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 22px rgba(35, 197, 164, 0.22) !important;
}
.secondary .stButton > button {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: none !important;
}

/* Footer */
.footerBox {
  margin-top: 2.0rem;
  opacity: 0.72;
  font-size: 0.92rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Load resources
# -----------------------------------------------------------------------------
@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        st.error("Missing model file: Final_model.pkl")
        st.stop()
    return joblib.load(MODEL_PATH)

@st.cache_data
def load_dataset():
    if not DATA_PATH.exists():
        st.error("Missing dataset file: loan_applications_fraud_4400.xlsx")
        st.stop()
    # openpyxl required (in requirements.txt)
    return pd.read_excel(DATA_PATH, engine="openpyxl")

pipeline = load_model()
df = load_dataset()

# -----------------------------------------------------------------------------
# Logo base64
# -----------------------------------------------------------------------------
def logo_base64():
    if not LOGO_PATH.exists():
        return None
    return base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")

LOGO_B64 = logo_base64()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def normalize_sa_phone(phone: str) -> str:
    p = (phone or "").strip().replace(" ", "")
    if p.startswith("05"):
        return "+966" + p[1:]
    return p

def parity_decision(salary: int) -> str:
    # 100% deterministic: odd => fraud, even => pass
    return "FRAUD" if (salary % 2 != 0) else "PASS"

# -----------------------------------------------------------------------------
# Session state for pages
# 0 Landing, 1 Form, 2 Fetch, 3 Decision, 4 Processing, 5 Thank you
# -----------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = 0
if "app" not in st.session_state:
    st.session_state.app = {}
if "decision" not in st.session_state:
    st.session_state.decision = None
if "offer_amount" not in st.session_state:
    st.session_state.offer_amount = None

# -----------------------------------------------------------------------------
# Layout: Left / Right
# -----------------------------------------------------------------------------
left_col, right_col = st.columns([0.38, 0.62], gap="large")

with left_col:
    st.markdown(
        """
<div class="leftPanel">
  <div class="lpShape1"></div>
  <div class="lpShape2"></div>
  <div class="lpBrand">
    EMKAN Finance Demo
    <small>AI-assisted Loan Screening</small>
  </div>
  <div class="phoneMock"></div>
</div>
""",
        unsafe_allow_html=True,
    )

with right_col:
    # Topbar
    st.markdown('<div class="topbar">', unsafe_allow_html=True)

    # left side: login row
    st.markdown(
        """
<div class="loginRow">
  <span>Don't have an account?</span>
  <span style="text-decoration:underline;">Create an account</span>
  <span class="badge">login</span>
</div>
""",
        unsafe_allow_html=True,
    )

    # right side: logo
    if LOGO_B64:
        st.markdown(
            f'<div><img src="data:image/png;base64,{LOGO_B64}" style="height:52px;"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div style='font-weight:900;'>EMKAN</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # PAGE 0: Landing
    # -----------------------------------------------------------------------------
    if st.session_state.page == 0:
        st.markdown('<div class="hTitle">Apply for Finance with EMKAN</div>', unsafe_allow_html=True)
        st.markdown('<div class="hSub">Fast, simple, and easy to use.</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            """
<div class="note">
This demo shows the end-to-end journey:
application submission → data fetching → automated assessment → decision.
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

    # -----------------------------------------------------------------------------
    # PAGE 1: Registration form
    # -----------------------------------------------------------------------------
    elif st.session_state.page == 1:
        st.markdown('<div class="hTitle">Registration</div>', unsafe_allow_html=True)
        st.markdown('<div class="hSub">Your information</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            """
<div class="note">
Enter only basic information. Additional data will be retrieved automatically from core systems and government sources
(SIMAH, National Address, etc.).
</div>
""",
            unsafe_allow_html=True,
        )

        with st.form("loan_form", clear_on_submit=False):
            c1, c2 = st.columns(2)

            with c1:
                full_name = st.text_input("Full name", placeholder="e.g., Mohammed Ahmed Alomari")
                age = st.number_input("Age", min_value=18, max_value=65, value=30)
                sector = st.selectbox("Employment sector", ["Private", "Government", "Semi-government"])
                national_id = st.text_input("National ID / Iqama", max_chars=10, placeholder="1XXXXXXXXX")

            with c2:
                phone = st.text_input("Mobile number", placeholder="+966 5XXXXXXXX")
                email = st.text_input("Email address", placeholder="example@email.com")
                salary = st.number_input("Basic monthly salary (SAR)", min_value=0, max_value=1_000_000, value=15000, step=1)
                requested = st.number_input("Requested finance amount (SAR)", min_value=2000, max_value=1_500_000, value=50000, step=1000)

            submit = st.form_submit_button("Submit application")

        if submit:
            if not full_name or not national_id or not phone or not email:
                st.warning("Please fill: Full name, National ID/Iqama, Mobile number, Email.")
            else:
                st.session_state.app = {
                    "full_name": full_name.strip(),
                    "age": int(age),
                    "sector": sector,
                    "national_id": national_id.strip(),
                    "phone": normalize_sa_phone(phone),
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

    # -----------------------------------------------------------------------------
    # PAGE 2: Fetching data
    # -----------------------------------------------------------------------------
    elif st.session_state.page == 2:
        st.markdown('<div class="hTitle">Fetching your data</div>', unsafe_allow_html=True)
        st.markdown('<div class="hSub">Retrieving information from core systems and government sources.</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="note"><b>In progress…</b> Core Loan System • SIMAH • National Address • KYC checks</div>', unsafe_allow_html=True)

        progress = st.progress(0)
        steps = [
            "Connecting to Core Loan System",
            "Retrieving SIMAH credit status",
            "Retrieving National Address",
            "Collecting device/IP/geo signals",
            "Preparing automated assessment",
        ]
        msg = st.empty()
        for i, s in enumerate(steps, start=1):
            msg.info(s)
            time.sleep(0.6)
            progress.progress(int(i / len(steps) * 100))

        # Deterministic demo decision (100% guarantee)
        salary = int(st.session_state.app["salary"])
        st.session_state.decision = parity_decision(salary)

        # Offer policy (Pass only): 3 × salary
        st.session_state.offer_amount = float(salary * 3)

        st.success("Completed successfully.")
        st.markdown("</div>", unsafe_allow_html=True)

        time.sleep(0.3)
        st.session_state.page = 3
        st.rerun()

    # -----------------------------------------------------------------------------
    # PAGE 3: Decision
    # -----------------------------------------------------------------------------
    elif st.session_state.page == 3:
        decision = st.session_state.decision
        salary = int(st.session_state.app.get("salary", 0))

        st.markdown('<div class="hTitle">Decision</div>', unsafe_allow_html=True)
        st.markdown('<div class="hSub">Your application has been assessed.</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)

        if decision == "PASS":
            offer = float(st.session_state.offer_amount or (salary * 3))
            st.markdown('<div class="good">✅ Pre-approval completed. An offer is available.</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
<div class="note">
<b>Offer amount:</b> {offer:,.0f} SAR<br>
<span style="opacity:0.75;">(Calculated as 3 × basic salary)</span>
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
            st.markdown('<div class="bad">⚠️ Your application will be transferred to the Sales / Verification team.</div>', unsafe_allow_html=True)
            st.markdown(
                """
<div class="note">
Our team will contact you to request additional information to complete your application.
</div>
""",
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("OK, I understand", use_container_width=True):
                    st.session_state.page = 4
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # PAGE 4: Processing
    # -----------------------------------------------------------------------------
    elif st.session_state.page == 4:
        st.markdown('<div class="hTitle">Processing</div>', unsafe_allow_html=True)
        st.markdown('<div class="hSub">We are working on your application.</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            """
<div class="note">
<b>In progress…</b> Your request is being processed. We will contact you within <b>24 hours</b>.
</div>
""",
            unsafe_allow_html=True,
        )

        pb = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            pb.progress(i + 1)

        st.success("Application received successfully.")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Start a new application", use_container_width=True):
            st.session_state.page = 0
            st.session_state.app = {}
            st.session_state.decision = None
            st.session_state.offer_amount = None
            st.rerun()

    # -----------------------------------------------------------------------------
    # PAGE 5: Thank you
    # -----------------------------------------------------------------------------
    elif st.session_state.page == 5:
        st.markdown('<div class="hTitle">Thank you</div>', unsafe_allow_html=True)
        st.markdown('<div class="hSub">Thank you for contacting EMKAN Finance.</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            """
<div class="note">
We appreciate your time. You can re-apply anytime if needed.
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Start a new application", use_container_width=True):
            st.session_state.page = 0
            st.session_state.app = {}
            st.session_state.decision = None
            st.session_state.offer_amount = None
            st.rerun()

    # -----------------------------------------------------------------------------
    # Footer (logo + names)
    # -----------------------------------------------------------------------------
    st.markdown(
        """
<div class="footerBox">
  <hr style="border:none; border-top:1px solid #eef2f7; margin: 1.6rem 0 1.0rem 0;">
  <div><b>Researchers:</b> ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED &amp; MOHAMED ABDELSATART</div>
  <div><b>Supervisor:</b> Dr. Khaled Iskaf</div>
  <div style="margin-top:0.4rem;">Master's Thesis Project | Midocean University | 2025</div>
</div>
""",
        unsafe_allow_html=True,
    )
