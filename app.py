import streamlit as st
from pathlib import Path
import base64

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="EMKAN Demo", page_icon="✅", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
def b64_file(path: str) -> str:
    p = Path(path)
    data = p.read_bytes()
    return base64.b64encode(data).decode("utf-8")

def inject_global_css():
    # ألوان قريبة من Emkan + طلبك (أزرق متوسط + خلفية فاتحة مائلة للأزرق)
    PRIMARY = "#3B3F8F"     # medium blue/indigo
    BG_LIGHT = "#F3F6FF"    # light bluish background
    BORDER = "#E2E6F3"
    TEXT_MUTED = "#7A7F95"
    ACCENT = "#2CB6A6"      # teal accent (للـ step 1)

    st.markdown(
        f"""
        <style>
        /* Hide Streamlit chrome */
        #MainMenu, header, footer {{ display:none !important; }}
        .stApp {{ background: {BG_LIGHT}; }}

        /* Remove default paddings */
        .block-container {{
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            max-width: 1400px;
        }}

        /* Layout wrappers */
        .emk-shell {{
            display:flex;
            min-height: 100vh;
            width: 100%;
        }}

        .emk-left {{
            flex: 0 0 28%;
            background: {PRIMARY};
            display:flex;
            align-items:center;
            justify-content:center;
            padding: 32px 18px;
        }}

        .emk-left img {{
            width: 95%;
            height: auto;
            object-fit: contain;
            user-select:none;
            -webkit-user-drag:none;
        }}

        .emk-right {{
            flex: 1;
            background: transparent;
            padding: 34px 38px;
        }}

        /* Top tiny language */
        .emk-top {{
            display:flex;
            justify-content:flex-end;
            align-items:center;
            margin-bottom: 18px;
        }}
        .emk-lang {{
            font-size: 14px;
            color: {PRIMARY};
            font-weight: 600;
            display:flex;
            align-items:center;
            gap: 8px;
            opacity: .9;
        }}

        /* Titles */
        .emk-title {{
            font-size: 36px;
            font-weight: 700;
            color: #111827;
            margin: 0;
        }}
        .emk-sub {{
            font-size: 14px;
            color: {TEXT_MUTED};
            margin-top: 6px;
            margin-bottom: 18px;
        }}
        .emk-sub a {{
            color: {PRIMARY};
            text-decoration: underline;
            font-weight: 600;
            margin-left: 6px;
        }}

        /* Stepper */
        .emk-stepper {{
            display:flex;
            align-items:center;
            gap: 10px;
            margin: 18px 0 22px 0;
        }}
        .emk-step {{
            width: 26px;
            height: 26px;
            border-radius: 999px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size: 13px;
            font-weight: 700;
            color: #fff;
        }}
        .emk-step.active {{ background: {ACCENT}; }}
        .emk-step.inactive {{ background: #C7CBDC; }}
        .emk-line {{
            height: 1px;
            flex: 1;
            background: #D9DDEA;
            margin: 0 4px;
        }}
        .emk-step-label {{
            font-size: 15px;
            font-weight: 700;
            color: #111827;
            white-space: nowrap;
        }}

        /* Form labels */
        .emk-section {{
            font-size: 18px;
            font-weight: 700;
            color: #111827;
            margin: 8px 0 14px 0;
        }}
        .emk-label {{
            font-size: 14px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 6px;
        }}

        /* Inputs styling (Streamlit widgets) */
        div[data-testid="stTextInput"] input,
        div[data-testid="stDateInput"] input {{
            height: 48px !important;
            border-radius: 12px !important;
            border: 1px solid {BORDER} !important;
            background: rgba(255,255,255,0.55) !important;
            font-size: 16px !important;
        }}

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stDateInput"] input:focus {{
            border: 1px solid #B9BFE3 !important;
            box-shadow: 0 0 0 3px rgba(59,63,143,0.12) !important;
        }}

        /* Checkbox line */
        .emk-checks {{
            margin-top: 12px;
            padding-top: 14px;
        }}

        /* Primary button */
        div.stButton > button {{
            height: 48px !important;
            border-radius: 14px !important;
            border: 1px solid {PRIMARY} !important;
            background: {PRIMARY} !important;
            color: #fff !important;
            font-weight: 700 !important;
            width: 100%;
        }}
        div.stButton > button:hover {{
            filter: brightness(0.97);
        }}

        /* Home hero */
        .home-hero {{
            min-height: 100vh;
            background: {PRIMARY};
            border-radius: 0;
            display:flex;
            align-items:center;
            justify-content:center;
            padding: 60px 40px;
            position: relative;
            overflow:hidden;
        }}
        .home-card {{
            width: min(1100px, 95%);
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap: 30px;
        }}
        .home-text h1 {{
            color: #8FE0D7;
            font-size: 56px;
            line-height: 1.05;
            margin: 0 0 18px 0;
            font-weight: 800;
        }}
        .home-text p {{
            color: rgba(255,255,255,0.85);
            font-size: 16px;
            margin: 6px 0;
        }}
        .home-cta {{
            margin-top: 22px;
            max-width: 260px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def render_home():
    inject_global_css()

    st.markdown('<div class="home-hero">', unsafe_allow_html=True)
    st.markdown('<div class="home-card">', unsafe_allow_html=True)

    # Left text like Emkan main page
    st.markdown(
        """
        <div class="home-text">
          <h1>Transforming finance<br/>into a digital experience</h1>
          <p>Fast onboarding • Smart screening • Smooth journey</p>
          <p>Demo shows AI-assisted loan screening workflow</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # CTA button: Personal = Get Started
    st.markdown('<div class="home-cta">', unsafe_allow_html=True)
    if st.button("Personal  •  Get Started", key="btn_get_started"):
        st.session_state.page = "register"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)


def render_register():
    inject_global_css()

    # Left image
    img_path = Path("assets/sme-main.svg")
    left_img_html = ""
    if img_path.exists():
        b64 = b64_file(str(img_path))
        left_img_html = f'<img src="data:image/svg+xml;base64,{b64}" alt="left"/>'
    else:
        # fallback empty (بس الأفضل تحط الصورة فعلياً)
        left_img_html = '<div style="color:white;font-weight:700;">Add assets/sme-main.svg</div>'

    st.markdown('<div class="emk-shell">', unsafe_allow_html=True)

    st.markdown(f'<div class="emk-left">{left_img_html}</div>', unsafe_allow_html=True)
    st.markdown('<div class="emk-right">', unsafe_allow_html=True)

    # Top right language
    st.markdown(
        """
        <div class="emk-top">
          <div class="emk-lang">🌐 العربية</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Title section
    st.markdown('<h1 class="emk-title">Registration</h1>', unsafe_allow_html=True)
    st.markdown('<div class="emk-sub">already have an account? <a>login</a></div>', unsafe_allow_html=True)

    # Stepper (1 active, 2-4 inactive)
    st.markdown(
        """
        <div class="emk-stepper">
          <div class="emk-step active">1</div>
          <div class="emk-step-label">Your information</div>
          <div class="emk-line"></div>
          <div class="emk-step inactive">2</div>
          <div class="emk-line"></div>
          <div class="emk-step inactive">3</div>
          <div class="emk-line"></div>
          <div class="emk-step inactive">4</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="emk-section">Your information</div>', unsafe_allow_html=True)

    # Form (معلومات العميل المطلوبة فقط)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="emk-label">National ID / Iqama</div>', unsafe_allow_html=True)
        nid = st.text_input("", placeholder="National ID / Iqama", label_visibility="collapsed", max_chars=10)

        st.markdown('<div class="emk-label">Mobile Number</div>', unsafe_allow_html=True)
        mobile = st.text_input("", placeholder="+966 Mobile Number", label_visibility="collapsed", max_chars=13)

    with col2:
        st.markdown('<div class="emk-label">Email Address</div>', unsafe_allow_html=True)
        email = st.text_input("", placeholder="Email Address", label_visibility="collapsed")

        st.markdown('<div class="emk-label">Date of birth</div>', unsafe_allow_html=True)
        dob = st.date_input("", value=None, label_visibility="collapsed")

    st.markdown('<div class="emk-checks"></div>', unsafe_allow_html=True)

    consent_1 = st.checkbox("I have read and agree to the Terms & Conditions and Privacy Notice")
    consent_2 = st.checkbox("I consent to retrieve my data from third parties (demo)")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Continue button
    can_continue = bool(nid and mobile and consent_1 and consent_2)
    if st.button("Continue", disabled=not can_continue, key="btn_continue"):
        st.session_state.page = "retrieve"  # الصفحة التالية (استرجاع البيانات ببطء) سنبنيها بالخطوة القادمة
        st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)  # close right + shell


# -----------------------------
# Router
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "register":
    render_register()
else:
    # Placeholder للخطوة القادمة (Retrieve page)
    inject_global_css()
    st.markdown("<div style='padding:40px;font-size:22px;font-weight:800;'>Next: Retrieve customer data (demo)</div>", unsafe_allow_html=True)
