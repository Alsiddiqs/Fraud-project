import streamlit as st
from pathlib import Path
import time
import joblib
import pandas as pd

# ==============================
# Page Configuration
# ==============================
st.set_page_config(
    page_title="Emkan Finance – AI Loan Screening",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# Paths
# ==============================
BASE_DIR = Path(__file__).parent
LEFT_IMAGE = BASE_DIR / "sme-main.svg"     # Optional hero illustration
MODEL_PATH = BASE_DIR / "Final_model.pkl"  # If you want to load model later
DATA_PATH = BASE_DIR / "loan_applications_fraud_4400.xlsx"

# ==============================
# Custom CSS (Emkan-like look)
# ==============================
st.markdown(
    """
    <style>
    /* Global */
    body {
        background-color: #f4f7fb;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        padding-top: 0rem;
    }

    /* Top hero header */
    .hero-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #4f46e5 60%, #22c1c3 100%);
        border-radius: 18px;
        padding: 28px 32px;
        color: #ffffff;
        margin-bottom: 28px;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.35);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .hero-text {
        max-width: 60%;
    }

    .hero-title {
        font-size: 1.9rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        font-size: 0.98rem;
        opacity: 0.92;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(15, 23, 42, 0.25);
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        margin-bottom: 0.4rem;
    }

    .hero-badge-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: #22c55e;
        box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.4);
    }

    /* Form card */
    .form-card {
        background: #ffffff;
        padding: 26px 26px 20px 26px;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.10);
        border: 1px solid #e5e7eb;
    }

    .form-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .form-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #111827;
    }

    .form-subtitle {
        font-size: 0.85rem;
        color: #6b7280;
    }

    .form-badge {
        padding: 0.25rem 0.75rem;
        background-color: #eff6ff;
        color: #1d4ed8;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Result card */
    .result-card {
        background: #0f172a;
        background: radial-gradient(circle at top left, #22c55e 0, transparent 55%),
                    radial-gradient(circle at bottom right, #3b82f6 0, transparent 45%),
                    #020617;
        color: #e5e7eb;
        padding: 22px 24px 18px 24px;
        border-radius: 18px;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(148, 163, 184, 0.35);
    }

    .result-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.22rem 0.7rem;
        border-radius: 999px;
        background-color: rgba(15, 23, 42, 0.85);
        font-size: 0.75rem;
        color: #e5e7eb;
        margin-bottom: 0.2rem;
    }

    .result-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
    }

    .result-sub {
        font-size: 0.85rem;
        color: #cbd5f5;
    }

    .result-cols {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.75rem;
        margin-top: 0.9rem;
    }

    .result-chip {
        padding: 0.55rem 0.65rem;
        background-color: rgba(15, 23, 42, 0.75);
        border-radius: 0.75rem;
        font-size: 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(148, 163, 184, 0.45);
    }

    .result-chip-label {
        color: #9ca3af;
    }

    .result-chip-value {
        font-weight: 600;
        color: #e5e7eb;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 50%, #22c55e 100%);
        color: white;
        border-radius: 999px;
        height: 46px;
        font-size: 0.95rem;
        border: none;
        font-weight: 600;
        padding: 0 1.8rem;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.35);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 50%, #16a34a 100%);
        transform: translateY(-1px);
    }

    /* Make Streamlit widgets a bit tighter */
    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 1.5rem;
        max-width: 1180px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# Hero Header
# ==============================
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-text">
            <div class="hero-badge">
                <span class="hero-badge-dot"></span>
                تمويل ذكي مدعوم بالذكاء الاصطناعي
            </div>
            <div class="hero-title">Emkan Finance – AI Loan Screening Demo</div>
            <div class="hero-subtitle">
                نموذج توضيحي يبيّن كيف يمكن لأنظمة إمكان ربط بيانات العميل من الأنظمة الأساسية 
                مع نموذج كشف الاحتيال لتسريع اتخاذ القرار بشكل آلي وآمن.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================
# Layout (Form + Result)
# ==============================
form_col, result_col = st.columns([1.6, 1.4])

# ==============================
# Right side: Result placeholder
# ==============================
with result_col:
    result_placeholder = st.empty()

# ==============================
# Left side: Form
# ==============================
with form_col:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="form-header">
            <div>
                <div class="form-title">بيانات طلب التمويل</div>
                <div class="form-subtitle">
                    الرجاء إدخال البيانات الأساسية، وسيتم استكمال البيانات المتبقية آلياً من Core Banking System في الـ Demo.
                </div>
            </div>
            <div class="form-badge">
                Demo فقط
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Use a form so submit happens once
    with st.form("loan_application_form"):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("الاسم الكامل")
            age = st.number_input("العمر", min_value=18, max_value=70, step=1)
            employment_sector = st.selectbox(
                "قطاع العمل",
                ["قطاع خاص", "حكومي", "شبه حكومي"]
            )
            national_id = st.text_input("رقم الهوية / الإقامة")

        with col2:
            mobile = st.text_input("رقم الجوال")
            email = st.text_input("البريد الإلكتروني")
            salary = st.number_input("الراتب الشهري الأساسي (ريال)", min_value=0, step=500)
            requested_amount = st.number_input(
                "مبلغ التمويل المطلوب (ريال)",
                min_value=0,
                step=1000
            )

        submitted = st.form_submit_button("تقديم الطلب")

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# Processing & Demo Logic
# ==============================
if submitted:
    with st.spinner("جاري الاتصال بـ Core Banking System واسترجاع بيانات العميل..."):
        time.sleep(1.8)

    with st.spinner("جاري التحقق من البيانات وربطها بمصادر موثوقة..."):
        time.sleep(1.5)

    with st.spinner("جاري تشغيل نموذج كشف الاحتيال المدعوم بالذكاء الاصطناعي..."):
        time.sleep(1.5)

    # Simple demo rule: even salary => Pass, odd salary => Fraud
    is_fraud = salary % 2 == 1

    # Fake enriched data
    if is_fraud:
        decision_label = "⚠️ إحالة للمراجعة (شبهة احتيال)"
        scenario_text = "تم اكتشاف نمط عالي الخطورة بناءً على سلوك الجهاز والموقع وتوقيت التغييرات على الحساب."
        enriched = {
            "عمر الحساب": "حساب جديد (30 يوم)",
            "تغيير كلمة المرور": "تم قبل ساعات",
            "تغيير رقم الجوال": "تم أمس",
            "موقع GPS": "خارج السعودية (دبي)",
            "حالة الجهاز": "جهاز غير موثوق",
            "عنوان IP": "عنوان أجنبي عالي الخطورة",
        }
    else:
        decision_label = "✅ قبول مبدئي (تمرير آلي)"
        scenario_text = "لم يتم رصد مؤشرات عالية الخطورة، ويمكن متابعة الطلب عبر القنوات المعتادة."
        enriched = {
            "عمر الحساب": "5 سنوات",
            "تغيير كلمة المرور": "لا توجد تغييرات حديثة",
            "تغيير رقم الجوال": "لا توجد تغييرات حديثة",
            "موقع GPS": "الرياض – السعودية",
            "حالة الجهاز": "جهاز موثوق",
            "عنوان IP": "عنوان سعودي موثوق",
        }

    # Render result card on the right
    with result_placeholder.container():
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-pill">
                    <span>نتيجة نموذج كشف الاحتيال</span>
                </div>
                <div class="result-title">{decision_label}</div>
                <div class="result-sub">
                    {scenario_text}
                </div>

                <div class="result-cols">
                    <div class="result-chip">
                        <div class="result-chip-label">اسم العميل</div>
                        <div class="result-chip-value">{full_name or "عميل إمكان"}</div>
                    </div>
                    <div class="result-chip">
                        <div class="result-chip-label">الراتب الشهري</div>
                        <div class="result-chip-value">{salary:,.0f} ريال</div>
                    </div>
                    <div class="result-chip">
                        <div class="result-chip-label">مبلغ التمويل المطلوب</div>
                        <div class="result-chip-value">{requested_amount:,.0f} ريال</div>
                    </div>
                    <div class="result-chip">
                        <div class="result-chip-label">قطاع العمل</div>
                        <div class="result-chip-value">{employment_sector}</div>
                    </div>
                </div>

                <div style="margin-top: 1.1rem; font-size: 0.82rem; color: #9ca3af;">
                    *هذا العرض توضيحي (Demo) يهدف لشرح فكرة ربط أنظمة إمكان الأساسية مع نموذج الذكاء الاصطناعي،
                    بينما في بيئة الإنتاج الفعلية يتم استخدام جميع حقول البيانات الحقيقية ونموذج XGBoost المدّرب بالكامل.*
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    # Initial placeholder content
    with result_placeholder.container():
        st.markdown(
            """
            <div class="result-card">
                <div class="result-pill">
                    في انتظار إدخال بيانات العميل
                </div>
                <div class="result-title">سيتم عرض نتيجة نموذج كشف الاحتيال هنا</div>
                <div class="result-sub">
                    بعد إدخال بيانات العميل الأساسية والضغط على زر "تقديم الطلب"،
                    سيظهر هنا كيف يقوم النظام باستكمال البيانات من Core Banking System ثم استخدام نموذج الذكاء الاصطناعي لاتخاذ القرار.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
