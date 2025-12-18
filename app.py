# =============================================================================
# EMKAN FINANCE - LOAN JOURNEY + FRAUD SCORING DEMO (UI ONLY)
# Master's Thesis Project - Midocean University
# Authors: Alsiddiq & Mohammed Abdu
# Supervisor: Dr. Khaled Eskaf
#
# IMPORTANT:
# - Model is NOT changed.
# - Only UI flow + input shaping to match the trained Pipeline.
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime, timedelta
import time
import re

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="إمكان للتمويل - طلب تمويل",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# STYLING (EMKAN-LIKE THEME)
# =============================================================================
st.markdown(
    """
<style>
    .main { padding: 1.6rem; background: #f5f7fa; }

    .emkan-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.2rem;
        border-radius: 20px;
        margin-bottom: 1.2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.28);
    }
    .emkan-logo { font-size: 2.6rem; font-weight: 800; margin-bottom: 0.25rem; }
    .subtle { opacity: 0.85; }

    .card {
        background: white;
        padding: 1.6rem;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin: 0.8rem 0;
        direction: rtl;
    }
    .card-title { font-weight: 800; color: #0f172a; margin-bottom: 0.6rem; }

    .info {
        background: #eff6ff;
        border-right: 6px solid #1e3a8a;
        border-radius: 14px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        direction: rtl;
    }

    .loading {
        background: #fef3c7;
        border: 2px dashed #f59e0b;
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        margin: 0.8rem 0;
        direction: rtl;
    }

    .result-pass {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        padding: 2rem;
        border-radius: 18px;
        text-align: center;
        color: white;
        font-size: 1.4rem;
        margin: 1rem 0;
        box-shadow: 0 10px 26px rgba(16, 185, 129, 0.25);
        direction: rtl;
    }
    .result-fraud {
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
        padding: 2rem;
        border-radius: 18px;
        text-align: center;
        color: white;
        font-size: 1.4rem;
        margin: 1rem 0;
        box-shadow: 0 10px 26px rgba(239, 68, 68, 0.25);
        direction: rtl;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        font-size: 1.05rem;
        padding: 0.8rem 1.4rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 5px 14px rgba(30, 58, 138, 0.25);
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(30, 58, 138, 0.32);
    }

    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# LOAD MODEL + DATASET (USED ONLY FOR DEFAULTS)
# =============================================================================

MODEL_CANDIDATES = [
    Path("Final_model.pkl"),
    Path("./Final_model.pkl"),
    Path("./model/Final_model.pkl"),
]

DATA_CANDIDATES = [
    Path("loan_applications_fraud_4400.xlsx"),
    Path("./loan_applications_fraud_4400.xlsx"),
    Path("./data/loan_applications_fraud_4400.xlsx"),
    Path("loan_applications_fraud_4400.xlsx"),
]

@st.cache_resource
def load_pipeline():
    for p in MODEL_CANDIDATES:
        if p.exists():
            return joblib.load(p)
    return None

@st.cache_data
def load_training_data():
    for p in DATA_CANDIDATES:
        if p.exists():
            df = pd.read_excel(p)
            return df
    return None

pipeline = load_pipeline()
train_df = load_training_data()

# =============================================================================
# UTILITIES
# =============================================================================

def mask_value(v: str) -> str:
    """Simple PII masking for demo display."""
    if v is None:
        return ""
    s = str(v)
    if len(s) <= 4:
        return "*" * len(s)
    return s[:2] + "*" * (len(s) - 4) + s[-2:]

def normalize_sa_phone(phone: str) -> str:
    if not phone:
        return phone
    s = re.sub(r"\s+", "", phone.strip())
    if s.startswith("05"):
        s = "+966" + s[1:]
    return s

def get_expected_raw_columns(pipe):
    """Get raw input columns expected by a sklearn pipeline (best effort)."""
    cols = getattr(pipe, "feature_names_in_", None)
    if cols is not None:
        return list(cols)

    # try common preprocess step names
    named_steps = getattr(pipe, "named_steps", {}) or {}
    for step_name in ["preprocess", "preprocessor", "prep", "transformer"]:
        step = named_steps.get(step_name)
        if step is not None:
            cols2 = getattr(step, "feature_names_in_", None)
            if cols2 is not None:
                return list(cols2)

    return None

def build_safe_defaults_from_dataset(df: pd.DataFrame, expected_cols: list) -> dict:
    """Create safe defaults for each expected column based on training dataset distribution."""
    defaults = {}
    for c in expected_cols:
        if c not in df.columns:
            defaults[c] = np.nan
            continue

        series = df[c].dropna()
        if series.empty:
            defaults[c] = np.nan
            continue

        if np.issubdtype(series.dtype, np.number):
            defaults[c] = float(series.median())
        elif np.issubdtype(series.dtype, np.datetime64):
            defaults[c] = pd.to_datetime(series).median()
        else:
            # mode for categorical/text
            try:
                defaults[c] = series.mode().iloc[0]
            except Exception:
                defaults[c] = series.iloc[0]
    return defaults

def generate_profiles():
    """
    Profiles that match your dataset columns (from the 4400 dataset):
    - Account Opening Date
    - Date of Last Password Change
    - Date of Last Phone Number Change
    - Login GPS Country / Latitude / Longitude
    - Trusted Device Status
    - Login IP Address
    - Login Channel
    """
    now = datetime.now()

    fraud_profile = {
        "Account Opening Date": now - timedelta(days=25),
        "Date of Last Password Change": now - timedelta(hours=2),
        "Date of Last Phone Number Change": now - timedelta(days=1),
        "Login GPS Country": "United Arab Emirates",
        "Login GPS Latitude": 25.2048,
        "Login GPS Longitude": 55.2708,
        "Trusted Device Status": "No",
        "Login IP Address": "154.23.45.67",
        "Login Channel": "Web Browser",
    }

    pass_profile = {
        "Account Opening Date": now - timedelta(days=1800),
        "Date of Last Password Change": now - timedelta(days=120),
        "Date of Last Phone Number Change": now - timedelta(days=365),
        "Login GPS Country": "Saudi Arabia",
        "Login GPS Latitude": 24.7136,
        "Login GPS Longitude": 46.6753,
        "Trusted Device Status": "Yes",
        "Login IP Address": "212.51.143.22",
        "Login Channel": "Mobile App",
    }

    return fraud_profile, pass_profile

def build_input_df(pipe, df_train, full_row: dict) -> pd.DataFrame:
    """
    Build input row that matches expected columns exactly:
    - Add missing columns with safe defaults
    - Keep only expected columns
    """
    expected_cols = get_expected_raw_columns(pipe)
    if expected_cols is None:
        # Fallback: still try
        return pd.DataFrame([full_row])

    safe_defaults = build_safe_defaults_from_dataset(df_train, expected_cols) if df_train is not None else {}
    row = {c: safe_defaults.get(c, np.nan) for c in expected_cols}

    # fill only columns that exist in expected list
    for k, v in full_row.items():
        if k in row:
            row[k] = v

    input_df = pd.DataFrame([row])

    # Ensure datetime parsing where possible
    for c in input_df.columns:
        if "Date" in c or "date" in c:
            try:
                input_df[c] = pd.to_datetime(input_df[c])
            except Exception:
                pass

    return input_df

def score(pipe, input_df: pd.DataFrame):
    proba = pipe.predict_proba(input_df)[:, 1][0]
    return float(proba), float(max(proba, 1 - proba))

# =============================================================================
# SESSION STATE (MULTI-PAGE FLOW)
# =============================================================================
if "step" not in st.session_state:
    st.session_state.step = 1  # 1=form, 2=fetch, 3=decision, 4=processing, 5=thankyou

if "customer" not in st.session_state:
    st.session_state.customer = {}

if "decision" not in st.session_state:
    st.session_state.decision = None  # "PASS" or "FRAUD"

if "risk" not in st.session_state:
    st.session_state.risk = {}

# =============================================================================
# HEADER
# =============================================================================
st.markdown(
    """
<div class="emkan-header">
    <div class="emkan-logo">💙 إمكان للتمويل</div>
    <h2 style="margin:0.2rem 0;">رحلة طلب التمويل - Demo للمناقشة</h2>
    <p class="subtle" style="margin:0.4rem 0;">(UI مبسطة + تجميع بيانات من الأنظمة + تحليل نموذج XGBoost الحقيقي)</p>
</div>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# VALIDATION: PIPELINE
# =============================================================================
if pipeline is None:
    st.error("⚠️ لم يتم العثور على ملف النموذج Final_model.pkl داخل المشروع.")
    st.stop()

if train_df is None:
    st.warning("⚠️ لم يتم العثور على ملف الداتاست (loan_applications_fraud_4400.xlsx). سيتم تشغيل الديمو بدون Defaults ذكية (قد يؤثر على الاستقرار).")

# =============================================================================
# STEP 1: FORM
# =============================================================================
if st.session_state.step == 1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📝 الصفحة الأولى: إدخال البيانات الأساسية</div>', unsafe_allow_html=True)
    st.markdown("يرجى إدخال بيانات العميل الأساسية. (بقية البيانات سيتم جلبها من الأنظمة والجهات الحكومية)")

    c1, c2 = st.columns(2)

    with c1:
        full_name = st.text_input("الاسم الكامل", placeholder="مثال: محمد أحمد العمري")
        age = st.number_input("العمر", min_value=18, max_value=65, value=30)
        employment_sector = st.selectbox("مكان العمل (القطاع)", ["قطاع خاص", "حكومي", "شبه حكومي"])
        national_id = st.text_input("رقم الهوية", max_chars=10, placeholder="1XXXXXXXXX")

    with c2:
        phone = st.text_input("رقم الجوال", placeholder="+966 5XXXXXXXX")
        email = st.text_input("البريد الإلكتروني", placeholder="example@email.com")
        salary = st.number_input("الراتب الشهري (ريال)", min_value=0, max_value=1_000_000, value=15000, step=1)
        requested_amount = st.number_input("مبلغ التمويل المطلوب (ريال)", min_value=2000, max_value=1_500_000, value=50000, step=1000)

    st.markdown("</div>", unsafe_allow_html=True)

    btn_col1, btn_col2, btn_col3 = st.columns([1,2,1])
    with btn_col2:
        submit = st.button("📨 تقديم الطلب", use_container_width=True)

    if submit:
        if not full_name or not national_id or not phone or not email:
            st.warning("⚠️ يرجى تعبئة: الاسم، الهوية، الجوال، الإيميل.")
        else:
            st.session_state.customer = {
                "full_name": full_name.strip(),
                "age": int(age),
                "employment_sector": employment_sector,
                "national_id": national_id.strip(),
                "phone": normalize_sa_phone(phone),
                "email": email.strip(),
                "salary": int(salary),
                "requested_amount": float(requested_amount),
            }
            st.session_state.step = 2
            st.rerun()

# =============================================================================
# STEP 2: FETCH (CORE + GOVERNMENT SOURCES)
# =============================================================================
elif st.session_state.step == 2:
    cust = st.session_state.customer

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔄 الصفحة الثانية: جلب البيانات من الأنظمة والجهات الحكومية</div>', unsafe_allow_html=True)

    st.markdown(
        """
<div class="loading">
    <h4 style="margin:0.2rem 0;">⏳ جاري جلب البيانات…</h4>
    <p style="margin:0.2rem 0;">Core Loan System + SIMAH + العنوان الوطني + تحقق الهوية</p>
</div>
""",
        unsafe_allow_html=True,
    )

    progress = st.progress(0)
    steps = [
        "الاتصال بالنظام الرئيسي (Core Loan System)",
        "جلب بيانات سمه (SIMAH) - الحالة الائتمانية",
        "جلب العنوان الوطني (Saudi Post)",
        "تجميع سجل الجهاز/IP والموقع",
        "تجهيز ملف الإدخال للنموذج",
    ]

    status_box = st.empty()
    for i, s in enumerate(steps, start=1):
        status_box.info(f"🔹 {s}")
        time.sleep(0.6)
        progress.progress(int(i / len(steps) * 100))

    # Determine demo scenario using salary odd/even
    # Odd salary => fraud scenario (for demo control)
    is_fraud_demo = (cust["salary"] % 2 != 0)

    fraud_profile, pass_profile = generate_profiles()
    profile = fraud_profile if is_fraud_demo else pass_profile

    # "Government / Core" fetched info (UI only)
    fetched = {
        "SIMAH Credit Status": "High Risk" if is_fraud_demo else "Good Standing",
        "National Address": "خارج الرياض - عنوان غير متطابق" if is_fraud_demo else "الرياض - العنوان الوطني مطابق",
        "KYC Verification": "Needs Review" if is_fraud_demo else "Verified",
        "Employer Sector": cust["employment_sector"],
        **profile,
    }

    # Build a model row based on your dataset columns
    full_row = {
        # Columns from dataset (best-effort)
        "ApplicationID": f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "Names ClientName": cust["full_name"],
        "Phone Number": cust["phone"],
        "Email": cust["email"],
        "Total Amounts": cust["requested_amount"],   # model uses requested amount (not offer)
        "Product Type": "Personal Loan",
        "Incident Start Date": datetime.now(),
        "Complaint Date": datetime.now(),
        "E-Services Login Session ID": f"SID-{np.random.randint(100000, 999999)}",
        # Risk features from profile (only if expected by pipeline)
        **profile,
        "Login Channel": profile.get("Login Channel", "Mobile App"),
    }

    # Build input_df aligned to expected columns
    input_df = build_input_df(pipeline, train_df, full_row)
    proba, conf = score(pipeline, input_df)

    decision = "FRAUD" if proba > 0.5 else "PASS"

    # For DEMO stability: if pipeline result contradicts demo parity, we still follow the model result,
    # but we keep the parity as "demo scenario hint" in hidden expander.
    st.session_state.risk = {
        "demo_is_fraud_by_salary_parity": is_fraud_demo,
        "model_proba": proba,
        "model_confidence": conf,
        "fetched": fetched,
        "full_row_sent_to_model": full_row,
        "expected_cols_count": len(get_expected_raw_columns(pipeline) or []),
    }
    st.session_state.decision = decision

    st.success("✅ اكتمل جلب البيانات وتجهيز الطلب")
    st.markdown("</div>", unsafe_allow_html=True)

    # Auto-advance to step 3
    time.sleep(0.3)
    st.session_state.step = 3
    st.rerun()

# =============================================================================
# STEP 3: DECISION PAGE (OFFER or REFER)
# =============================================================================
elif st.session_state.step == 3:
    cust = st.session_state.customer
    risk = st.session_state.risk
    decision = st.session_state.decision

    # Show fetched info summary
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📌 ملخص البيانات المُسترجعة</div>', unsafe_allow_html=True)

    f = risk.get("fetched", {})
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='info'><b>سمه (SIMAH):</b> {f.get('SIMAH Credit Status','-')}<br><b>تحقق الهوية/KYC:</b> {f.get('KYC Verification','-')}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='info'><b>العنوان الوطني:</b> {f.get('National Address','-')}<br><b>قطاع العمل:</b> {f.get('Employer Sector','-')}</div>", unsafe_allow_html=True)

    # Metrics
    st.markdown("### 🤖 نتيجة التقييم بالذكاء الاصطناعي")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Risk Score", f"{risk['model_proba']*100:.1f}%")
    with m2:
        st.metric("Confidence", f"{risk['model_confidence']*100:.1f}%")
    with m3:
        st.metric("Requested Amount", f"{cust['requested_amount']:,.0f} ريال")

    st.markdown("</div>", unsafe_allow_html=True)

    # Branch
    if decision == "PASS":
        # Offer = 3x salary (per your demo requirement)
        offer_amount = float(cust["salary"] * 3)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">💼 الصفحة الثالثة: عرض التمويل (Offer)</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
<div class="result-pass">
    <h3 style="margin:0.2rem 0;">✅ تمت مراجعة الطلب مبدئياً</h3>
    <p style="margin:0.2rem 0;">العرض المتاح حسب سياسات الشركة: <b>{offer_amount:,.0f} ريال</b> (ثلاثة أضعاف الراتب الأساسي)</p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
<div class="info">
<b>ملاحظة:</b> هذا العرض يتم توليده آلياً لأغراض الديمو. في الواقع قد تخضع القيمة لسياسات ائتمانية إضافية.
</div>
""",
            unsafe_allow_html=True,
        )

        a1, a2, a3 = st.columns([1,2,1])
        with a2:
            approve = st.button("✅ أوافق على العرض", use_container_width=True)
            reject = st.button("❌ أرفض العرض", use_container_width=True)

        if approve:
            st.session_state.step = 4
            st.rerun()

        if reject:
            st.session_state.step = 5
            st.session_state.thankyou_msg = "نشكر لك تواصلك مع شركة إمكان للتمويل"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # FRAUD: refer to sales / verification
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚠️ الصفحة الثالثة: إجراء إضافي لاستكمال الطلب</div>', unsafe_allow_html=True)

        st.markdown(
            """
<div class="result-fraud">
    <h3 style="margin:0.2rem 0;">⚠️ سيتم تحويل الطلب للتواصل</h3>
    <p style="margin:0.2rem 0;">سيتم تحويل طلبكم لفريق المبيعات/التحقق للتواصل معكم وطلب معلومات إضافية لاستكمال الطلب.</p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
<div class="info">
<b>السبب (للعرض فقط):</b> تم رصد مؤشرات تتطلب خطوة تحقق إضافية قبل استكمال الموافقة.
</div>
""",
            unsafe_allow_html=True,
        )

        end1, end2, end3 = st.columns([1,2,1])
        with end2:
            st.button("✅ فهمت، بانتظار تواصل الفريق", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Hidden demo / diagnostics
    with st.expander("ℹ️ (للمقدم فقط) تفاصيل الديمو والتشخيص"):
        st.write("التحكم بالديمو (الراتب فردي => سيناريو احتيال) =", risk.get("demo_is_fraud_by_salary_parity"))
        st.write("عدد الأعمدة المتوقعة من الـPipeline =", risk.get("expected_cols_count"))
        st.write("البيانات المرسلة للموديل (بدون إخفاء):")
        st.json(risk.get("full_row_sent_to_model", {}))

# =============================================================================
# STEP 4: PROCESSING (APPROVED PATH)
# =============================================================================
elif st.session_state.step == 4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⏳ الصفحة الرابعة: جاري العمل على طلبك</div>', unsafe_allow_html=True)

    st.markdown(
        """
<div class="loading">
    <h4 style="margin:0.2rem 0;">⏳ جاري العمل على طلبكم…</h4>
    <p style="margin:0.2rem 0;">سيتم التواصل معكم خلال 24 ساعة</p>
</div>
""",
        unsafe_allow_html=True,
    )

    p = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        p.progress(i + 1)

    st.success("✅ تم استلام الطلب بنجاح")
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        back = st.button("🏠 العودة للصفحة الرئيسية", use_container_width=True)
        if back:
            st.session_state.step = 1
            st.session_state.customer = {}
            st.session_state.decision = None
            st.session_state.risk = {}
            st.rerun()

# =============================================================================
# STEP 5: THANK YOU (REJECT PATH)
# =============================================================================
elif st.session_state.step == 5:
    msg = st.session_state.get("thankyou_msg", "نشكر لك تواصلك مع شركة إمكان للتمويل")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🙏</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="info">
<h4 style="margin:0.2rem 0;">{msg}</h4>
<p style="margin:0.2rem 0;">نتطلع لخدمتكم دائماً.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        back = st.button("🏠 بدء طلب جديد", use_container_width=True)
        if back:
            st.session_state.step = 1
            st.session_state.customer = {}
            st.session_state.decision = None
            st.session_state.risk = {}
            st.rerun()

# =============================================================================
# FOOTER
# =============================================================================
st.markdown(
    """
<div style="text-align:center; color:#64748b; padding: 1.4rem;">
  <p style="font-size:1.1rem; color:#1e3a8a; font-weight:800; margin:0;">💙 إمكان للتمويل</p>
  <p style="margin:0.2rem 0;">شركة تمويل سعودية مرخصة | مملوكة بالكامل لبنك الراجحي</p>
  <p style="font-size:0.85rem; margin:0.2rem 0;">🎓 مشروع بحث الماجستير | Midocean University | 2025</p>
</div>
""",
    unsafe_allow_html=True,
)
