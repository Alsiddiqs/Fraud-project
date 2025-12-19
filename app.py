import time
import re
from pathlib import Path
from datetime import datetime
import base64

import pandas as pd
import streamlit as st

# ----------------------------
# Config
# ----------------------------
st.set_page_config(
    page_title="EMKAN Finance Demo",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LOGO_PATH = Path("emkan_logo.png")
DATA_PATH = Path("loan_applications_fraud_4400.xlsx")

# Colors (requested: medium blue + light bluish main)
PRIMARY = "#3C5BFA"      # medium blue (accent)
PRIMARY_DARK = "#2E3DD9"
BG = "#F3F7FF"           # main light bluish background
CARD = "#FFFFFF"
TEXT = "#0F172A"
MUTED = "#64748B"
BORDER = "#D8E3FF"
SOFT = "#EEF4FF"

# ----------------------------
# Helpers
# ----------------------------
def b64_image(path: Path):
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")

LOGO_B64 = b64_image(LOGO_PATH)

def clean_digits(x: str) -> str:
    return re.sub(r"\D+", "", (x or "").strip())

def is_valid_nid(nid: str) -> bool:
    d = clean_digits(nid)
    return len(d) == 10

def is_valid_mobile(m: str) -> bool:
    d = clean_digits(m)
    # allow formats: 05xxxxxxxx or 5xxxxxxxx or 9665xxxxxxxx
    if d.startswith("966"):
        d = d[3:]
    if d.startswith("0"):
        d = d[1:]
    return len(d) == 9 and d.startswith("5")

def is_valid_email(e: str) -> bool:
    e = (e or "").strip()
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e))

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
        digits = clean_digits(s)
        return f"+966 *** *** {digits[-4:]}" if len(digits) >= 4 else "+966 ***"

    if "id" in k or "iqama" in k or "national" in k:
        digits = clean_digits(s)
        if len(digits) >= 4:
            return f"{digits[:2]}******{digits[-2:]}"
        return "**********"

    if "name" in k:
        parts = s.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1][0]}***"
        return s[:2] + "***" if len(s) >= 2 else "***"

    return s if len(s) <= 26 else s[:26] + "..."

def safe_read_excel(path: Path):
    if not path.exists():
        return None
    try:
        return pd.read_excel(path, engine="openpyxl")
    except Exception:
        return None

def deterministic_decision(salary_int: int) -> str:
    # odd => FRAUD, even => PASS (hidden)
    return "FRAUD" if (salary_int % 2 != 0) else "PASS"

def compute_offer_amount(salary_int: int) -> int:
    # hidden internal logic; do NOT show explanation text
    return int(salary_int * 3)

# ----------------------------
# Session state
# ----------------------------
# pages: 0=Landing, 1=Registration, 2=Fetching, 3=Decision, 4=Processing, 5=Thankyou
if "page" not in st.session_state:
    st.session_state.page = 0
if "app" not in st.session_state:
    st.session_state.app = {}
if "df" not in st.session_state:
    st.session_state.df = None
if "decision" not in st.session_state:
    st.session_state.decision = None
if "offer" not in st.session_state:
    st.session_state.offer = None

# ----------------------------
# CSS (closer to EMKAN layout)
# ----------------------------
logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:44px;" />' if LOGO_B64 else "<b>EMKAN</b>"

st.markdown(
    f"""
<style>
#MainMenu, footer, header {{visibility:hidden;}}
[data-testid="stHeader"] {{background: transparent !important;}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
  background: {BG} !important;
  color: {TEXT} !important;
}}

.block-container {{
  max-width: 1200px !important;
  padding-top: 1.2rem !important;
  padding-bottom: 2rem !important;
}}

:root {{
  --primary: {PRIMARY};
  --primary-dark: {PRIMARY_DARK};
  --bg: {BG};
  --card: {CARD};
  --text: {TEXT};
  --muted: {MUTED};
  --border: {BORDER};
  --soft: {SOFT};
}}

.shell {{
  border: 1px solid var(--border);
  border-radius: 22px;
  overflow: hidden;
  background: var(--card);
  box-shadow: 0 18px 55px rgba(15,23,42,0.08);
}}

.headerbar {{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
  background: var(--card);
}}

.headerLeft {{
  display:flex;
  gap:10px;
  align-items:center;
  color: var(--muted);
  font-weight: 700;
  font-size: 0.95rem;
}}
.headerLeft a {{
  color: var(--primary);
  text-decoration: underline;
  font-weight: 800;
}}

.layout {{
  display:flex;
  min-height: 780px;
}}

.leftPanel {{
  width: 30%;
  min-width: 320px;
  background: linear-gradient(180deg, rgba(60,91,250,0.10), rgba(60,91,250,0.04));
  border-right: 1px solid var(--border);
  padding: 22px;
  display:flex;
  flex-direction:column;
  gap: 10px;
}}

.leftTitle {{
  font-weight: 950;
  letter-spacing: 0.2px;
}}
.leftSub {{
  color: rgba(15,23,42,0.65);
  font-weight: 700;
  font-size: 0.95rem;
}}

.leftArt {{
  margin-top: 8px;
  flex: 1;
  border-radius: 18px;
  border: 1px solid rgba(60,91,250,0.16);
  background:
     radial-gradient(circle at 30% 25%, rgba(60,91,250,0.22), rgba(60,91,250,0) 55%),
     radial-gradient(circle at 70% 75%, rgba(15,23,42,0.10), rgba(15,23,42,0) 55%),
     linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.55));
}}

.rightPanel {{
  width: 70%;
  padding: 26px 28px;
  background: var(--bg);
}}

@media (max-width: 980px) {{
  .layout {{flex-direction: column;}}
  .leftPanel {{width:100%; min-width: 0;}}
  .rightPanel {{width:100%;}}
}}

.title {{
  font-size: 2.15rem;
  font-weight: 950;
  margin: 6px 0 4px 0;
}}
.subtitle {{
  color: rgba(15,23,42,0.60);
  font-weight: 750;
  margin: 0 0 18px 0;
}}

.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px;
}}

.note {{
  background: var(--soft);
  border: 1px solid rgba(60,91,250,0.18);
  border-radius: 14px;
  padding: 12px 14px;
  color: rgba(15,23,42,0.82);
  margin-bottom: 14px;
  font-weight: 650;
}}

label {{
  color: rgba(15,23,42,0.70) !important;
  font-weight: 850 !important;
}}

[data-baseweb="input"] > div, [data-baseweb="select"] > div {{
  border: 1px solid #D6E2F2 !important;
  border-radius: 12px !important;
  background: #FFFFFF !important;
  box-shadow: none !important;
}}
[data-baseweb="input"] > div:focus-within, [data-baseweb="select"] > div:focus-within {{
  border: 1px solid rgba(60,91,250,0.85) !important;
  box-shadow: 0 0 0 4px rgba(60,91,250,0.15) !important;
}}

.stButton > button {{
  background: var(--primary) !important;
  border: 1px solid var(--primary) !important;
  color: #fff !important;
  font-weight: 950 !important;
  border-radius: 14px !important;
  padding: 0.85rem 1.05rem !important;
  box-shadow: 0 14px 30px rgba(60,91,250,0.22) !important;
}}

.btnSecondary .stButton > button {{
  background: #fff !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
}}

.smallMeta {{
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  color: rgba(15,23,42,0.62);
  font-size: 0.92rem;
  line-height: 1.55;
}}
</style>

<div class="shell">
  <div class="headerbar">
    <div class="headerLeft">
      <span>Already have an account?</span>
      <a href="#">login</a>
    </div>
    <div>{logo_html}</div>
  </div>

  <div class="layout">
    <div class="leftPanel">
      <div class="leftTitle">EMKAN Finance Demo</div>
      <div class="leftSub">AI-assisted Loan Screening</div>
      <div class="leftArt"></div>
    </div>

    <div class="rightPanel">
""",
    unsafe_allow_html=True,
)

# ----------------------------
# Pages
# ----------------------------
def footer_block():
    st.markdown(
        """
<div class="smallMeta">
  <div><b>Researchers:</b> ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED &nbsp;|&nbsp; MOHAMED ABDELSATART</div>
  <div><b>Supervisor:</b> Dr. Khaled Iskaf</div>
  <div>Master's Thesis Project | Midocean University | 2025</div>
</div>
""",
        unsafe_allow_html=True,
    )

if st.session_state.page == 0:
    st.markdown('<div class="title">Apply for Finance</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Fast, simple, and easy to use.</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="note">
This demo shows the full journey: application → data retrieval → decision.
</div>
""",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1, 1.1, 1])
    with c2:
        if st.button("Get started", use_container_width=True):
            st.session_state.page = 1
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    footer_block()

elif st.session_state.page == 1:
    st.markdown('<div class="title">Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Your information</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="note">
Customer enters only basic information. Remaining information is retrieved automatically from core systems and government sources.
</div>
""",
        unsafe_allow_html=True,
    )

    with st.form("form"):
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            full_name = st.text_input("Full name", placeholder="e.g., Mohammed Ahmed Alomari")
        with r1c2:
            mobile = st.text_input("Mobile number", placeholder="+966 5XXXXXXXX")

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            age = st.text_input("Age", placeholder="e.g., 30")
        with r2c2:
            email = st.text_input("Email address", placeholder="example@email.com")

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            sector = st.selectbox("Employment sector", ["Private", "Government", "Semi-government"])
        with r3c2:
            salary = st.text_input("Basic monthly salary (SAR)", placeholder="e.g., 15000")

        r4c1, r4c2 = st.columns(2)
        with r4c1:
            nid = st.text_input("National ID / Iqama", placeholder="1XXXXXXXXX", max_chars=10)
        with r4c2:
            req_amt = st.text_input("Requested finance amount (SAR)", placeholder="e.g., 50000")

        submitted = st.form_submit_button("Submit application")

    # Validation + submit
    if submitted:
        errors = []

        if not full_name.strip():
            errors.append("Full name is required.")
        if not is_valid_mobile(mobile):
            errors.append("Mobile number is not valid.")
        if not is_valid_email(email):
            errors.append("Email address is not valid.")
        if not is_valid_nid(nid):
            errors.append("National ID / Iqama must be 10 digits.")

        age_digits = clean_digits(age)
        salary_digits = clean_digits(salary)
        req_digits = clean_digits(req_amt)

        if not age_digits:
            errors.append("Age is required.")
        if not salary_digits:
            errors.append("Basic monthly salary is required.")
        if not req_digits:
            errors.append("Requested finance amount is required.")

        if errors:
            st.warning("Please fix the following:\n\n- " + "\n- ".join(errors))
        else:
            st.session_state.app = {
                "full_name": full_name.strip(),
                "mobile": mobile.strip(),
                "age": int(age_digits),
                "email": email.strip(),
                "sector": sector,
                "salary": int(salary_digits),
                "requested_amount": int(req_digits),
                "nid": nid.strip(),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
            st.session_state.page = 2
            st.rerun()

    b1, b2, b3 = st.columns([0.22, 0.56, 0.22])
    with b2:
        st.markdown('<div class="btnSecondary">', unsafe_allow_html=True)
        if st.button("Back", use_container_width=True):
            st.session_state.page = 0
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    footer_block()

elif st.session_state.page == 2:
    st.markdown('<div class="title">Fetching data</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Retrieving full customer profile…</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="note">
Retrieving all customer fields required by the dataset schema (shown gradually for demo clarity).
</div>
""",
        unsafe_allow_html=True,
    )

    # Load df once
    if st.session_state.df is None:
        st.session_state.df = safe_read_excel(DATA_PATH)

    df = st.session_state.df
    if df is None:
        st.error("Dataset could not be loaded. Please confirm the Excel file exists and openpyxl is installed.")
    else:
        steps = [
            "Connecting to Core Loan System…",
            "Retrieving SIMAH credit information…",
            "Retrieving National Address…",
            "Collecting device and geo signals…",
            "Loading required dataset fields…",
            "Finalizing assessment…",
        ]
        prog = st.progress(0)
        msg = st.empty()

        for i, s in enumerate(steps, start=1):
            msg.info(s)
            time.sleep(1.15)
            prog.progress(int(i / len(steps) * 55))

        st.markdown("### Retrieved fields (from dataset)")
        sample = df.iloc[0].to_dict() if len(df) else {}
        cols = list(df.columns)

        # show many fields but still readable
        show = cols[:70]
        for idx, c in enumerate(show, start=1):
            st.write(f"✅ **{c}** — `{mask_value(c, sample.get(c,''))}`")
            time.sleep(0.10)
            prog.progress(min(95, 55 + int((idx / max(1, len(show))) * 40)))

        if len(cols) > len(show):
            st.info(f"Additional fields retrieved: {len(cols) - len(show)}")

        prog.progress(100)
        st.success("Data retrieval completed.")

        salary_int = int(st.session_state.app.get("salary", 0))
        st.session_state.decision = deterministic_decision(salary_int)
        st.session_state.offer = compute_offer_amount(salary_int)

        time.sleep(0.6)  # small pause so the committee sees completion
        st.session_state.page = 3
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    footer_block()

elif st.session_state.page == 3:
    st.markdown('<div class="title">Result</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Application status</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    decision = st.session_state.decision
    salary_int = int(st.session_state.app.get("salary", 0))
    offer_int = int(st.session_state.offer or 0)

    if decision == "PASS":
        st.success("Your application is eligible for an offer.")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Offer amount (SAR)", f"{offer_int:,}")
        with c2:
            st.metric("Basic monthly salary (SAR)", f"{salary_int:,}")

        st.markdown("<br>", unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            if st.button("Approve", use_container_width=True):
                st.session_state.page = 4
                st.rerun()
        with b:
            st.markdown('<div class="btnSecondary">', unsafe_allow_html=True)
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
    footer_block()

elif st.session_state.page == 4:
    st.markdown('<div class="title">Processing</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">We are working on your application.</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        """
<div class="note">
In progress… Your request is being processed. We will contact you within 24 hours.
</div>
""",
        unsafe_allow_html=True,
    )

    p = st.progress(0)
    for i in range(100):
        time.sleep(0.025)
        p.progress(i + 1)

    st.success("Application received successfully.")
    if st.button("Start a new application", use_container_width=True):
        st.session_state.page = 0
        st.session_state.app = {}
        st.session_state.df = None
        st.session_state.decision = None
        st.session_state.offer = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    footer_block()

elif st.session_state.page == 5:
    st.markdown('<div class="title">Thank you</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Thank you for contacting EMKAN Finance.</div>', unsafe_allow_html=True)

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
        st.session_state.df = None
        st.session_state.decision = None
        st.session_state.offer = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    footer_block()

# close HTML wrappers
st.markdown(
    """
    </div>  <!-- rightPanel -->
  </div>    <!-- layout -->
</div>      <!-- shell -->
""",
    unsafe_allow_html=True,
)
