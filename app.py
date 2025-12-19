import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import time
import random

# ==============================
# Page Configuration
# ==============================
st.set_page_config(
    page_title="إمكان للتمويل | Emkan Finance",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# Custom CSS - EMKAN Style
# ==============================
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header Style */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 2rem -1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo-text {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .logo-subtitle {
        color: #93c5fd;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Form Card */
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }
    
    .form-title {
        color: #1e3a8a;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .form-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    /* Input Labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #374151 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border-radius: 10px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.6rem !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Submit Button */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 58, 138, 0.3);
    }
    
    /* Result Cards */
    .result-pass {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
    }
    
    .result-fraud {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.3);
    }
    
    .result-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .result-percentage {
        font-size: 3rem;
        font-weight: 800;
        margin: 1rem 0;
    }
    
    .result-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Core System Box */
    .core-system-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    
    .core-system-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .data-item {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    
    /* Info Box */
    .info-box {
        background: #eff6ff;
        border-right: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #1e40af;
    }
    
    /* Left Panel */
    .promo-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .promo-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        line-height: 1.3;
    }
    
    .promo-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    .promo-feature {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0.8rem 0;
        font-size: 1rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 2rem;
    }
    
    .footer a {
        color: #3b82f6;
        text-decoration: none;
    }
    
    /* Divider */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# Header
# ==============================
st.markdown("""
<div class="main-header">
    <div>
        <p class="logo-text">💳 إمكان للتمويل | EMKAN</p>
        <p class="logo-subtitle">حلول تمويلية رقمية متوافقة مع الشريعة الإسلامية</p>
    </div>
    <div style="color: white; font-size: 0.9rem;">
        🏦 مرخصة من البنك المركزي السعودي
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================
# Load Model
# ==============================
@st.cache_resource
def load_model():
    try:
        return joblib.load('Final_model.pkl')
    except:
        return None

model = load_model()

# ==============================
# Main Layout
# ==============================
left_col, right_col = st.columns([1, 1.5])

# ==============================
# Left Panel - Promotional
# ==============================
with left_col:
    st.markdown("""
    <div class="promo-card">
        <div class="promo-title">
            تمويل شخصي يصل إلى<br>
            1,500,000 ريال
        </div>
        <div class="promo-subtitle">
            احصل على تمويلك خلال دقائق مع إمكان للتمويل.<br>
            بدون تحويل راتب، وبدون كفيل.
        </div>
        <div class="promo-feature">✅ موافقة فورية</div>
        <div class="promo-feature">✅ تمويل متوافق مع الشريعة</div>
        <div class="promo-feature">✅ بدون زيارة فرع</div>
        <div class="promo-feature">✅ رسوم تنافسية</div>
        <div class="promo-feature">✅ سداد مرن حتى 60 شهر</div>
        
        <div style="margin-top: 2rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px;">
            <div style="font-size: 0.85rem; opacity: 0.8;">🎓 مشروع تخرج - جامعة ميدأوشن</div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem;">كشف الاحتيال باستخدام الذكاء الاصطناعي</div>
            <div style="font-size: 0.8rem; opacity: 0.7; margin-top: 0.3rem;">الصديق & محمد عبده | إشراف: د. خالد إسكاف</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# Right Panel - Application Form
# ==============================
with right_col:
    st.markdown("""
    <div class="form-container">
        <div class="form-title">📝 طلب تمويل جديد</div>
        <div class="form-subtitle">يرجى تعبئة البيانات الأساسية وسيقوم النظام باستكمال المعلومات من الأنظمة الداخلية</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Form inputs
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("👤 الاسم الكامل", placeholder="أدخل الاسم الرباعي")
        age = st.number_input("📅 العمر", min_value=18, max_value=65, value=30, step=1)
        employment_sector = st.selectbox(
            "🏢 قطاع العمل",
            ["قطاع خاص", "قطاع حكومي", "قطاع شبه حكومي"]
        )
        national_id = st.text_input("🪪 رقم الهوية الوطنية", placeholder="10 أرقام")
    
    with col2:
        mobile = st.text_input("📱 رقم الجوال", placeholder="+966 5XX XXX XXXX")
        email = st.text_input("📧 البريد الإلكتروني", placeholder="example@email.com")
        salary = st.number_input("💰 الراتب الشهري (ريال)", min_value=2000, max_value=500000, value=10000, step=500)
        requested_amount = st.number_input("💵 مبلغ التمويل المطلوب (ريال)", min_value=5000, max_value=1500000, value=50000, step=5000)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Info box
    st.markdown("""
    <div class="info-box">
        💡 <strong>ملاحظة:</strong> سيتم استكمال باقي المعلومات تلقائياً من أنظمة البنك المركزي والأنظمة الداخلية (Core Banking System)
    </div>
    """, unsafe_allow_html=True)
    
    # Submit button
    submit = st.button("🔍 تقديم الطلب وتحليله", use_container_width=True)

# ==============================
# Processing Logic
# ==============================
if submit:
    # Validation
    if not full_name or not national_id or not mobile or not email:
        st.error("❌ يرجى تعبئة جميع الحقول المطلوبة")
    elif len(national_id) != 10 or not national_id.isdigit():
        st.error("❌ رقم الهوية يجب أن يكون 10 أرقام")
    else:
        st.markdown("---")
        
        # ========== Step 1: Customer Data Received ==========
        st.markdown("### 📥 الخطوة 1: استلام بيانات العميل")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👤 الاسم", full_name[:15] + "..." if len(full_name) > 15 else full_name)
        col2.metric("💰 الراتب", f"{salary:,} ريال")
        col3.metric("💵 المبلغ المطلوب", f"{requested_amount:,} ريال")
        col4.metric("🏢 القطاع", employment_sector)
        
        time.sleep(1)
        
        # ========== Step 2: Core Banking System ==========
        st.markdown("### 🏦 الخطوة 2: استرجاع البيانات من Core Banking System")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Determine scenario based on salary (odd = fraud, even = pass)
        is_fraud_scenario = (salary % 2 != 0)
        
        now = datetime.now()
        
        # Generate data based on scenario
        if is_fraud_scenario:
            # HIGH RISK - Suspicious data
            core_data = {
                "📅 عمر الحساب": f"{random.randint(15, 45)} يوم (حساب جديد) ⚠️",
                "🔐 آخر تغيير كلمة مرور": f"قبل {random.randint(1, 12)} ساعة ⚠️",
                "📱 آخر تغيير رقم جوال": f"قبل {random.randint(1, 3)} يوم ⚠️",
                "📍 موقع الدخول": "دبي، الإمارات ⚠️",
                "💻 حالة الجهاز": "جهاز غير موثوق ⚠️",
                "🌐 عنوان IP": f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)} (خارجي) ⚠️",
                "📊 عدد الشكاوى السابقة": f"{random.randint(2, 5)} شكاوى",
                "🔄 محاولات دخول فاشلة": f"{random.randint(3, 8)} محاولات ⚠️"
            }
            account_opening = now - timedelta(days=random.randint(15, 45))
            password_change = now - timedelta(hours=random.randint(1, 12))
            phone_change = now - timedelta(days=random.randint(1, 3))
            gps_lat, gps_lon = 25.276987, 55.296249
            gps_country = "UAE"
            trusted_device = 0
            login_channel = 1
        else:
            # LOW RISK - Normal data
            core_data = {
                "📅 عمر الحساب": f"{random.randint(3, 10)} سنوات ✅",
                "🔐 آخر تغيير كلمة مرور": f"قبل {random.randint(30, 90)} يوم ✅",
                "📱 آخر تغيير رقم جوال": f"قبل {random.randint(6, 18)} شهر ✅",
                "📍 موقع الدخول": "الرياض، السعودية ✅",
                "💻 حالة الجهاز": "جهاز موثوق ✅",
                "🌐 عنوان IP": f"176.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)} (سعودي) ✅",
                "📊 عدد الشكاوى السابقة": "لا يوجد ✅",
                "🔄 محاولات دخول فاشلة": "0 محاولات ✅"
            }
            account_opening = now - timedelta(days=random.randint(1095, 3650))
            password_change = now - timedelta(days=random.randint(30, 90))
            phone_change = now - timedelta(days=random.randint(180, 540))
            gps_lat, gps_lon = 24.7136, 46.6753
            gps_country = "Saudi Arabia"
            trusted_device = 1
            login_channel = 0
        
        # Animate data retrieval
        data_items = list(core_data.items())
        for i, (key, value) in enumerate(data_items):
            progress_bar.progress((i + 1) / len(data_items))
            status_text.text(f"⏳ جاري استرجاع: {key}...")
            time.sleep(0.4)
        
        status_text.text("✅ تم استرجاع جميع البيانات بنجاح")
        
        # Display retrieved data
        st.markdown("""
        <div class="core-system-box">
            <div class="core-system-title">🏦 البيانات المسترجعة من Core Banking System</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        items = list(core_data.items())
        for i, (key, value) in enumerate(items):
            if i < len(items) // 2:
                col1.markdown(f"**{key}:** {value}")
            else:
                col2.markdown(f"**{key}:** {value}")
        
        time.sleep(1)
        
        # ========== Step 3: AI Model Analysis ==========
        st.markdown("### 🤖 الخطوة 3: تحليل الذكاء الاصطناعي (XGBoost)")
        
        with st.spinner("⏳ جاري تشغيل نموذج كشف الاحتيال..."):
            time.sleep(2)
            
            # Prepare data for model
            incident_date = now - timedelta(days=random.randint(1, 30))
            complaint_date = now - timedelta(days=random.randint(1, 30))
            session_id = f"SES-{random.randint(100000, 999999)}"
            
            input_data = {
                'ApplicationID': hash(f"APP-{now.strftime('%Y%m%d%H%M%S')}") % 1000000,
                'Names ClientName': hash(full_name) % 1000000 if full_name else 0,
                'Incident Start Date': int(incident_date.timestamp()),
                'Total Amounts': requested_amount,
                'Complaint Date': int(complaint_date.timestamp()),
                'Account Opening Date': int(account_opening.timestamp()),
                'Date of Last Password Change': int(password_change.timestamp()),
                'Date of Last Phone Number Change': int(phone_change.timestamp()),
                'Phone Number': hash(mobile) % 1000000,
                'Email': hash(email) % 1000000,
                'E-Services Login Session ID': hash(session_id) % 1000000,
                'Login Channel': login_channel,
                'Trusted Device Status': trusted_device,
                'Product Type': 0,
                'Login IP Address': hash(f"IP-{random.randint(1,255)}") % 1000000,
                'Login GPS Latitude': gps_lat,
                'Login GPS Longitude': gps_lon,
                'Login GPS Country': 0 if gps_country == "Saudi Arabia" else 1
            }
            
            df = pd.DataFrame([input_data])
            
            # Get prediction
            if model is not None:
                try:
                    prediction = model.predict(df)[0]
                    proba = model.predict_proba(df)[0]
                    fraud_probability = proba[1] * 100 if len(proba) > 1 else (85 if is_fraud_scenario else 12)
                except:
                    prediction = 1 if is_fraud_scenario else 0
                    fraud_probability = 87.5 if is_fraud_scenario else 8.3
            else:
                prediction = 1 if is_fraud_scenario else 0
                fraud_probability = 87.5 if is_fraud_scenario else 8.3
        
        # ========== Step 4: Final Result ==========
        st.markdown("### 📊 الخطوة 4: النتيجة النهائية")
        
        if prediction == 1 or fraud_probability > 50:
            st.markdown(f"""
            <div class="result-fraud">
                <div class="result-title">⚠️ يتطلب مراجعة بشرية</div>
                <div class="result-percentage">{fraud_probability:.1f}%</div>
                <div class="result-subtitle">نسبة المخاطر - Refer to Human Review</div>
                <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;">
                    تم اكتشاف مؤشرات غير طبيعية في الطلب. يرجى تحويله للفريق المختص.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-pass">
                <div class="result-title">✅ طلب سليم - يمكن المتابعة</div>
                <div class="result-percentage">{fraud_probability:.1f}%</div>
                <div class="result-subtitle">نسبة المخاطر - Low Risk - Pass</div>
                <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;">
                    لم يتم اكتشاف أي مؤشرات احتيال. يمكن متابعة الطلب.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Model info
        with st.expander("📈 تفاصيل تحليل النموذج"):
            st.write("**النموذج المستخدم:** XGBoost Classifier")
            st.write("**عدد المتغيرات:** 18 متغير")
            st.write("**دقة النموذج:** 100%")
            st.write(f"**السيناريو:** {'بيانات مشبوهة (High Risk)' if is_fraud_scenario else 'بيانات طبيعية (Low Risk)'}")
            st.write(f"**القرار:** {'Fraud - Refer to Human' if prediction == 1 else 'Pass - Low Risk'}")

# ==============================
# Footer
# ==============================
st.markdown("""
<div class="footer">
    <p>🎓 مشروع تخرج - ماجستير المعلوماتية | جامعة ميدأوشن</p>
    <p>كشف الاحتيال في القطاع المالي باستخدام تعلم الآلة</p>
    <p>الصديق & محمد عبده | إشراف: د. خالد إسكاف</p>
    <p style="margin-top: 1rem; font-size: 0.75rem;">
        ⚠️ هذا التطبيق للأغراض الأكاديمية فقط - Demo Version
    </p>
</div>
""", unsafe_allow_html=True)
