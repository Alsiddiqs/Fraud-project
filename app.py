import streamlit as st
from pathlib import Path

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="EMKAN | Fraud Detection",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).parent
LEFT_IMAGE = BASE_DIR / "sme-main.svg"
LOGO_IMAGE = BASE_DIR / "emkan_logo.png"

# -----------------------------
# Custom CSS (Emkan-like)
# -----------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

body {
    background-color: #f4f7ff;
}

.main {
    padding: 0;
}

/* Remove Streamlit default padding */
.block-container {
    padding-top: 0;
    padding-bottom: 0;
}

/* Left section */
.left-panel {
    background-color: #3f3d73;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Right section */
.right-panel {
    background-color: #ffffff;
    padding: 60px 80px;
    height: 100vh;
    overflow-y: auto;
}

/* Titles */
.title {
    font-size: 32px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 40px;
}

/* Section title */
.section-title {
    font-size: 20px;
    font-weight: 500;
    margin-bottom: 25px;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    height: 48px;
    border-radius: 10px;
    border: 1px solid #d1d5db;
    font-size: 15px;
}

/* Button */
.stButton button {
    height: 48px;
    border-radius: 12px;
    background-color: #5b6cff;
    color: white;
    font-size: 15px;
    font-weight: 500;
    border: none;
}

.stButton button:hover {
    background-color: #4a5af0;
}

/* Checkbox text */
.stCheckbox label {
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Layout
# -----------------------------
left_col, right_col = st.columns([1, 2], gap="large")

# -----------------------------
# Left Panel (Image)
# -----------------------------
with left_col:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    if LEFT_IMAGE.exists():
        st.image(str(LEFT_IMAGE), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Right Panel (Form)
# -----------------------------
with right_col:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    # Logo
    if LOGO_IMAGE.exists():
        st.image(str(LOGO_IMAGE), width=140)

    # Header
    st.markdown('<div class="title">Registration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Already have an account? <b>login</b></div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-title">Your information</div>', unsafe_allow_html=True)

    # Form
    with st.form("registration_form"):
        col1, col2 = st.columns(2)

        with col1:
            national_id = st.text_input("Owner National ID / Iqama", max_chars=10)
            unn = st.text_input("Unified National Number (UNN)", max_chars=10)
            mobile = st.text_input("Mobile Number", placeholder="+966xxxxxxxxx")

        with col2:
            company_name = st.text_input("English Company Name")
            email = st.text_input("Email Address")
            dob = st.date_input("Date of birth")

        st.markdown("")

        agree_terms = st.checkbox(
            "I have read and agree to the Terms & Conditions and Privacy Notice"
        )

        consent_data = st.checkbox(
            "I consent to EMKAN retrieving my data from third parties"
        )

        st.markdown("")

        submit = st.form_submit_button("Continue")

        if submit:
            if not agree_terms:
                st.warning("Please accept the Terms & Conditions.")
            else:
                st.success("Information submitted successfully.")

    st.markdown('</div>', unsafe_allow_html=True)
