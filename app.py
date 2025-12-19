import streamlit as st
from pathlib import Path
import time
import joblib
import pandas as pd

# ==============================
# Page Configuration
# ==============================
st.set_page_config(
    page_title="EMKAN Finance – AI Loan Screening",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# Paths
# ==============================
BASE_DIR = Path(__file__).parent
LEFT_IMAGE = BASE_DIR / "sme-main.svg"
MODEL_PATH = BASE_DIR / "Final_model.pkl"
DATA_PATH = BASE_DIR / "loan_applications_fraud_4400.xlsx"

# ==============================
# Custom CSS (Inspired by EMKAN)
# ==============================
st.markdown(
    """
    <style>
    body {
        background-color: #f4f7fb;
    }

    .left-panel {
        background: linear-gradient(180deg, #3f3d73 0%, #4a4fa3 100%);
        height: 100vh;
        padding: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .form-card {
        background: #ffffff;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.08);
    }

    h1, h2 {
        color: #1f2937;
    }

    label {
        font-weight: 600;
        color: #374151;
    }

    .stButton > button {
        background-color: #6f86e8;
        color: white;
        border-radius: 12px;
        height: 48px;
        font-size: 16px;
        border: none;
    }

    .stButton > button:hover {
        background-color: #5a6fd6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# Layout
# ==============================
left_col, right_col = st.columns([1.1, 1.9])

# ==============================
# Left Panel (SVG safe load)
# ==============================
with left_col:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    if LEFT_IMAGE.exists():
        if LEFT_IMAGE.suffix.lower() == ".svg":
            svg_bytes = LEFT_IMAGE.read_bytes()
            st.image(svg_bytes, use_container_width=True)
        else:
            st.image(str(LEFT_IMAGE), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# Right Panel – Registration Form
# ==============================
with right_col:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    st.markdown("### Registration")
    st.markdown("Already have an account? **Login**")

    st.markdown("---")
    st.markdown("#### Your information")

    # ---- Inputs (Only what customer enters) ----
    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input("Full name")
        age = st.number_input("Age", min_value=18, max_value=70, step=1)
        employment_sector = st.selectbox(
            "Employment sector",
            ["Private", "Government", "Self-employed"]
        )
        national_id = st.text_input("National ID / Iqama")

    with col2:
        mobile = st.text_input("Mobile number")
        email = st.text_input("Email address")
        salary = st.number_input("Basic monthly salary (SAR)", min_value=0, step=500)
        requested_amount = st.number_input(
            "Requested finance amount (SAR)",
            min_value=0,
            step=1000
        )

    st.markdown("")

    # ---- Submit ----
    submit = st.button("Submit application")

    # ==============================
    # Processing Demo (Slow & Clear)
    # ==============================
    if submit:
        with st.spinner("Retrieving customer data from core systems..."):
            time.sleep(2)

        with st.spinner("Validating information..."):
            time.sleep(2)

        with st.spinner("Running AI fraud screening model..."):
            time.sleep(2)

        st.success("Application processed successfully ✅")

        st.info(
            "For demo purposes: remaining customer information was "
            "automatically retrieved from internal systems and government sources."
        )

    st.markdown('</div>', unsafe_allow_html=True)
