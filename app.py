# =============================================================================
# EMKAN FINANCE – AI Loan Application Screening (Final Demo Version)
#
# Researchers:
#  - ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED
#  - MOHAMED ABDELSATART
# Supervisor:
#  - Dr. Khaled Iskaf
#
# NOTE:
# - Model is NOT changed.
# - This is a UI & journey demo with deterministic control (hidden).
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
import time
import re

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="EMKAN Finance | Apply for Finance",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# GLOBAL STYLES (EMKAN LOOK & FEEL)
# =============================================================================
st.markdown("""
<style>
.main { padding: 0 !important; background: #f5f7fa; }
.block-container { padding: 0 !important; max-width: 100% !important; }

#MainMenu, footer, header { visibility: hidden; }

.wrapper { display: flex; min-height: 100vh; }

/* LEFT PANEL */
.left-panel {
  width: 38%;
  background: linear-gradient(180deg, #3d3b6f, #34335f);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.left-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.08), transparent 60%);
}
.phone {
  width: 280px; height: 520px;
  border-radius: 36px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

/* RIGHT PANEL */
.right-panel {
  width: 62%;
  background: white;
  padding: 2.4rem 2.8rem;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo img { height: 48px; }

.hero-title {
  font-size: 2rem;
  font-weight: 900;
  margin-top: 1.5rem;
}
.hero-sub {
  opacity: 0.7;
  margin-bottom: 1.8rem;
}

.card {
  background: white;
  border-radius: 18px;
  padding: 1.6rem;
  box-shadow: 0 8px 28px rgba(0,0,0,0.06);
  margin-top: 1rem;
}

.notice {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.success {
  background: rgba(16,185,129,0.15);
  border: 1px solid rgba(16,185,129,0.25);
  padding: 1.2rem;
  border-radius: 16px;
  font-weight: 800;
}
.warning {
  background: rgba(239,68,68,0.15);
  border: 1px solid rgba(239,68,68,0.25);
  padding: 1.2rem;
  border-radius: 16px;
  font-weight: 800;
}

.stButton > button {
  background: #23c5a4;
  color: white;
  font-weight: 800;
  border-radius: 14px;
  padding: 0.8rem 1.4rem;
  border: none;
}
.stButton > button:hover { transform: translateY(-1px); }

.footer {
  margin-top: 2rem;
  font-size: 0.9rem;
  opacity: 0.75;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# LOAD FILES
# =============================================================================
MODEL_PATH = Path("Final_model.pkl")
DATA_PATH = Path("loan_applications_fraud_4400.xlsx")
LOGO_PATH = Path("emkan_logo.png")

pipeline = joblib.load(MODEL_PATH)
df = pd.read_excel(DATA_PATH)

# =============================================================================
# HELPERS
# =============================================================================
def normalize_phone(p):
    if p.startswith("05"):
        return "+966" + p[1:]
    return p

# deterministic demo control
def is_fraud_by_salary(salary):
    return salary % 2 != 0

# =============================================================================
# SESSION STATE
# =============================================================================
if "page" not in st.session_state:
    st.session_state.page = 0
if "app" not in st.session_state:
    st.session_state.app = {}
if "decision" not in st.session_state:
    st.session_state.decision = None

# =============================================================================
# LAYOUT SHELL
# =============================================================================
st.markdown('<div class="wrapper">', unsafe_allow_html=True)

# LEFT
st.markdown('<div class="left-panel"><div class="phone"></div></div>', unsafe_allow_html=True)

# RIGHT
st.markdown('<div class="right-panel">', unsafe_allow_html=True)

# =============================================================================
# PAGE 0 – LANDING
# =============================================================================
if st.session_state.page == 0:
    st.markdown('<div class="topbar">', unsafe_allow_html=True)
    st.markdown(f'<div class="logo"><img src="data:image/png;base64,{LOGO_PATH.read_bytes().hex()}"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="hero-title">Apply for Finance with EMKAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Fast, simple, and easy to use.</div>', unsafe_allow_html=True)

    st.button("Get Started", on_click=lambda: st.session_state.update(page=1))

# =============================================================================
# PAGE 1 – REGISTRATION
# =============================================================================
elif st.session_state.page == 1:
    st.markdown('<div class="hero-title">Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Your information</div>', unsafe_allow_html=True)

    with st.form("form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name")
            age = st.number_input("Age", 18, 65, 30)
            sector = st.selectbox("Employment sector", ["Private", "Government", "Semi-government"])
            nid = st.text_input("National ID / Iqama")
        with c2:
            phone = st.text_input("Mobile number")
            email = st.text_input("Email")
            salary = st.number_input("Basic salary (SAR)", 0, 1_000_000, 15000, 1)
            amount = st.number_input("Requested amount (SAR)", 2000, 1_500_000, 50000, 1000)

        submitted = st.form_submit_button("Submit application")

    if submitted:
        st.session_state.app = {
            "name": name,
            "salary": salary,
            "requested": amount
        }
        st.session_state.page = 2
        st.rerun()

# =============================================================================
# PAGE 2 – FETCHING DATA
# =============================================================================
elif st.session_state.page == 2:
    st.markdown('<div class="hero-title">Fetching your data</div>', unsafe_allow_html=True)
    st.markdown('<div class="notice">Connecting to Core Systems, SIMAH, National Address…</div>', unsafe_allow_html=True)

    p = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        p.progress(i+1)

    salary = st.session_state.app["salary"]
    st.session_state.decision = "FRAUD" if is_fraud_by_salary(salary) else "PASS"
    st.session_state.page = 3
    st.rerun()

# =============================================================================
# PAGE 3 – DECISION
# =============================================================================
elif st.session_state.page == 3:
    decision = st.session_state.decision
    salary = st.session_state.app["salary"]

    if decision == "PASS":
        offer = salary * 3
        st.markdown('<div class="success">✅ Pre-approved</div>', unsafe_allow_html=True)
        st.markdown(f"<p>Offer amount: <b>{offer:,} SAR</b></p>", unsafe_allow_html=True)
        if st.button("Approve offer"):
            st.session_state.page = 4
            st.rerun()
        if st.button("Reject offer"):
            st.session_state.page = 5
            st.rerun()
    else:
        st.markdown('<div class="warning">⚠️ Application referred to verification team</div>', unsafe_allow_html=True)
        st.button("OK", on_click=lambda: st.session_state.update(page=4))

# =============================================================================
# PAGE 4 – FINAL
# =============================================================================
elif st.session_state.page == 4:
    st.markdown('<div class="hero-title">Processing</div>', unsafe_allow_html=True)
    st.markdown("<p>We will contact you within 24 hours.</p>", unsafe_allow_html=True)
    st.button("Start new application", on_click=lambda: st.session_state.update(page=0))

# =============================================================================
# PAGE 5 – THANK YOU
# =============================================================================
elif st.session_state.page == 5:
    st.markdown('<div class="hero-title">Thank you</div>', unsafe_allow_html=True)
    st.markdown("<p>Thank you for contacting EMKAN Finance.</p>", unsafe_allow_html=True)
    st.button("Start new application", on_click=lambda: st.session_state.update(page=0))

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("""
<div class="footer">
<hr>
<b>Researchers:</b> ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED & MOHAMED ABDELSATART<br>
<b>Supervisor:</b> Dr. Khaled Iskaf<br>
Master’s Thesis – Midocean University – 2025
</div>
""", unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
