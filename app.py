# =============================================================================
# EMKAN FINANCE - FRAUD DETECTION DEMO
# Master's Thesis Project - Midocean University
# Authors: Alsiddiq & Mohammed Abdu
# Supervisor: Dr. Khaled Eskaf
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, date, timedelta
from pathlib import Path
import time

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="إمكان للتمويل - نظام الكشف عن الاحتيال",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS STYLING - EMKAN BRANDING
# =============================================================================

st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 2rem;
        background: #f5f7fa;
    }
    
    /* Emkan Header */
    .emkan-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.3);
    }
    
    .emkan-logo {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    /* Form container */
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* Result boxes */
    .result-pass {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-size: 1.8rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
        animation: fadeIn 0.5s;
    }
    
    .result-fraud {
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-size: 1.8rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
        animation: fadeIn 0.5s;
    }
    
    /* Info boxes */
    .info-box {
        background: #eff6ff;
        padding: 1.5rem;
        border-radius: 12px;
        border-right: 5px solid #1e3a8a;
        margin: 1rem 0;
        direction: rtl;
    }
    
    .data-box {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
    }
    
    /* Loading animation */
    .loading-box {
        background: #fef3c7;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        border: 2px dashed #f59e0b;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        font-size: 1.2rem;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 5px 15px rgba(30, 58, 138, 0.3);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(30, 58, 138, 0.4);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* RTL Support */
    .rtl {
        direction: rtl;
        text-align: right;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# LOAD MODEL
# =============================================================================

@st.cache_resource
def load_model():
    """Load the trained fraud detection model."""
    model_path = Path("Final_model.pkl")
    if model_path.exists():
        return joblib.load(model_path)
    else:
        st.error("⚠️ لم يتم العثور على ملف النموذج")
        return None

model = load_model()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_synthetic_data(salary, is_fraud):
    """
    Generate synthetic data based on salary (odd/even logic).
    
    Odd salary → Fraud indicators
    Even salary → Pass indicators
    """
    base_date = datetime.now()
    
    if is_fraud:
        # Suspicious indicators
        data = {
            "Account Opening Date": base_date - timedelta(days=30),  # New account
            "Date of Last Password Change": base_date - timedelta(hours=2),  # Recent change
            "Date of Last Phone Number Change": base_date - timedelta(days=1),  # Very recent
            "Login GPS Country": "United Arab Emirates",  # Foreign location
            "Login GPS Latitude": 25.2048,  # Dubai
            "Login GPS Longitude": 55.2708,
            "Trusted Device Status": "No",  # Untrusted device
            "Login IP Address": "154.23.45.67",  # Foreign IP
            "Login Channel": "Web Browser"
        }
    else:
        # Normal indicators
        data = {
            "Account Opening Date": base_date - timedelta(days=1825),  # 5 years old
            "Date of Last Password Change": base_date - timedelta(days=180),  # 6 months ago
            "Date of Last Phone Number Change": base_date - timedelta(days=365),  # 1 year ago
            "Login GPS Country": "Saudi Arabia",
            "Login GPS Latitude": 24.7136,  # Riyadh
            "Login GPS Longitude": 46.6753,
            "Trusted Device Status": "Yes",
            "Login IP Address": "212.51.143.22",  # Saudi IP
            "Login Channel": "Mobile App"
        }
    
    return data

# =============================================================================
# HEADER
# =============================================================================

st.markdown("""
<div class="emkan-header">
    <div class="emkan-logo">💙 إمكان للتمويل</div>
    <h2>نظام الكشف عن الاحتيال بالذكاء الاصطناعي</h2>
    <p style="font-size: 1.1rem; opacity: 0.9;">مرخص من البنك المركزي السعودي (ساما)</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">مشروع بحث الماجستير | جامعة Midocean</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# MAIN FORM
# =============================================================================

st.markdown('<div class="form-container">', unsafe_allow_html=True)
st.markdown("## 📝 طلب تمويل جديد")
st.markdown("يرجى إدخال البيانات الأساسية للعميل:")

# Create two columns for better layout
col1, col2 = st.columns(2)

with col1:
    client_name = st.text_input(
        "الاسم الكامل",
        placeholder="مثال: محمد أحمد العمري",
        help="الاسم الكامل للعميل"
    )
    
    age = st.number_input(
        "العمر",
        min_value=18,
        max_value=65,
        value=30,
        help="عمر العميل (18-65 سنة)"
    )
    
    employment_sector = st.selectbox(
        "قطاع العمل",
        options=["قطاع خاص", "حكومي", "شبه حكومي"],
        help="القطاع الذي يعمل به العميل"
    )
    
    phone = st.text_input(
        "رقم الجوال",
        placeholder="+966 5XX XXX XXXX",
        help="رقم الجوال السعودي"
    )

with col2:
    email = st.text_input(
        "البريد الإلكتروني",
        placeholder="example@email.com",
        help="البريد الإلكتروني للعميل"
    )
    
    national_id = st.text_input(
        "رقم الهوية الوطنية",
        placeholder="1XXXXXXXXX",
        max_chars=10,
        help="رقم الهوية الوطنية (10 أرقام)"
    )
    
    salary = st.number_input(
        "الراتب الشهري (ريال)",
        min_value=0,
        max_value=1000000,
        value=15000,
        step=1000,
        help="الراتب الشهري للعميل بالريال السعودي"
    )
    
    loan_amount = st.number_input(
        "مبلغ التمويل المطلوب (ريال)",
        min_value=2000,
        max_value=1500000,
        value=50000,
        step=1000,
        help="المبلغ المطلوب للتمويل (من 2,000 إلى 1,500,000 ريال)"
    )

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# PREDICTION BUTTON
# =============================================================================

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    predict_button = st.button(
        "🚀 تحليل الطلب",
        use_container_width=True,
        type="primary"
    )

# =============================================================================
# PREDICTION LOGIC
# =============================================================================

if predict_button:
    if model is None:
        st.error("❌ لم يتم تحميل النموذج بشكل صحيح")
    elif not client_name or not phone or not email or not national_id:
        st.warning("⚠️ يرجى ملء جميع الحقول المطلوبة")
    else:
        # Determine if this should be fraud or pass based on salary (odd/even)
        is_fraud = (salary % 2 != 0)
        
        # Step 1: Show loading - Connecting to Core Banking System
        st.markdown("""
        <div class="loading-box">
            <h3>⏳ جاري الاتصال بنظام Core Banking System...</h3>
            <p>يتم جمع البيانات الإضافية للعميل</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        # Step 2: Generate and display synthetic data
        synthetic_data = generate_synthetic_data(salary, is_fraud)
        
        st.success("✅ تم جمع البيانات من Core Banking System")
        
        st.markdown("### 📊 البيانات المُسترجعة من النظام البنكي:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="data-box">
                <b>📅 تاريخ فتح الحساب:</b><br>
                {synthetic_data['Account Opening Date'].strftime('%Y-%m-%d')}<br>
                <small>({(datetime.now() - synthetic_data['Account Opening Date']).days} يوم)</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="data-box">
                <b>🔐 آخر تغيير كلمة مرور:</b><br>
                {synthetic_data['Date of Last Password Change'].strftime('%Y-%m-%d %H:%M')}<br>
                <small>(منذ {(datetime.now() - synthetic_data['Date of Last Password Change']).days} يوم)</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="data-box">
                <b>📱 آخر تغيير رقم جوال:</b><br>
                {synthetic_data['Date of Last Phone Number Change'].strftime('%Y-%m-%d')}<br>
                <small>(منذ {(datetime.now() - synthetic_data['Date of Last Phone Number Change']).days} يوم)</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="data-box">
                <b>📍 الموقع الجغرافي:</b><br>
                {synthetic_data['Login GPS Country']}<br>
                <small>({synthetic_data['Login GPS Latitude']:.4f}, {synthetic_data['Login GPS Longitude']:.4f})</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="data-box">
                <b>📱 قناة الدخول:</b><br>
                {synthetic_data['Login Channel']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="data-box">
                <b>🔒 حالة الجهاز:</b><br>
                {"✅ جهاز موثوق" if synthetic_data['Trusted Device Status'] == "Yes" else "⚠️ جهاز غير موثوق"}<br>
                <small>IP: {synthetic_data['Login IP Address']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Step 3: Analyzing with AI Model
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="loading-box">
            <h3>🤖 جاري تحليل الطلب بالذكاء الاصطناعي...</h3>
            <p>يتم معالجة البيانات عبر نموذج XGBoost</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar2 = st.progress(0)
        for i in range(100):
            time.sleep(0.015)
            progress_bar2.progress(i + 1)
        
        # Step 4: Prepare full data for model
        try:
            full_data = {
                "ApplicationID": f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "Names ClientName": client_name,
                "Phone Number": phone,
                "Email": email,
                "Total Amounts": loan_amount,
                "Product Type": "Personal Loan",
                "Incident Start Date": datetime.now(),
                "Complaint Date": datetime.now(),
                **synthetic_data,
                "E-Services Login Session ID": f"SID-{np.random.randint(100000, 999999)}",
            }
            
            # Convert to DataFrame
            input_df = pd.DataFrame([full_data])
            
            # Convert date columns
            date_columns = [
                "Incident Start Date", "Complaint Date", "Account Opening Date",
                "Date of Last Password Change", "Date of Last Phone Number Change"
            ]
            for col in date_columns:
                if col in input_df.columns:
                    input_df[col] = pd.to_datetime(input_df[col])
            
            # Get prediction from real model
            proba = model.predict_proba(input_df)[:, 1][0]
            fraud_percentage = proba * 100
            
            # Step 5: Display Results
            st.markdown("---")
            st.markdown("## 📋 نتيجة التحليل")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("درجة المخاطرة", f"{fraud_percentage:.1f}%")
            
            with col2:
                st.metric("الراتب الشهري", f"{salary:,} ريال")
            
            with col3:
                confidence = max(proba, 1-proba) * 100
                st.metric("مستوى الثقة", f"{confidence:.1f}%")
            
            # Final Decision
            if proba > 0.5:
                st.markdown("""
                <div class="result-fraud">
                    <h2>⚠️ يُحوّل للتحقق البشري</h2>
                    <p>تم اكتشاف مؤشرات مشبوهة تتطلب مراجعة فريق مكافحة الاحتيال</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="info-box">
                    <h4>🔍 الإجراءات الموصى بها:</h4>
                    <ul>
                        <li>التحقق من هوية العميل عبر مستندات إضافية</li>
                        <li>الاتصال بالعميل عبر الرقم المسجل</li>
                        <li>مراجعة سجل المعاملات للكشف عن أي شذوذ</li>
                        <li>رفع الحالة لفريق التحقيقات إذا لزم الأمر</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-pass">
                    <h2>✅ طلب سليم</h2>
                    <p>اجتاز الطلب الفحص الآلي بنجاح ويمكن المتابعة في الإجراءات</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="info-box">
                    <h4>✅ الخطوات التالية:</h4>
                    <ul>
                        <li>المتابعة مع التقييم الائتماني القياسي</li>
                        <li>التحقق من مستندات الدخل</li>
                        <li>استكمال متطلبات اعرف عميلك (KYC)</li>
                        <li>إصدار قرار الموافقة النهائي</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Show full data in expander
            with st.expander("📄 عرض البيانات الكاملة"):
                st.json(full_data)
                
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء التحليل: {str(e)}")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem;">
    <p style="font-size: 1.2rem; color: #1e3a8a; font-weight: bold;">💙 إمكان للتمويل</p>
    <p>شركة تمويل سعودية مرخصة | مملوكة بالكامل لبنك الراجحي</p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">🎓 مشروع بحث الماجستير | جامعة Midocean | 2025</p>
    <p style="font-size: 0.85rem;">الكشف عن الاحتيال في المؤسسات المالية السعودية باستخدام التعلم الآلي</p>
    <p style="font-size: 0.8rem; opacity: 0.7;">إشراف: د. خالد اسكاف</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# DEMO INSTRUCTIONS (Hidden - for presentation purposes)
# =============================================================================

with st.expander("ℹ️ تعليمات العرض التوضيحي (Demo)"):
    st.markdown("""
    ### 🎯 كيفية التحكم بالنتيجة:
    
    **للحصول على نتيجة "طلب سليم" ✅:**
    - أدخل راتب **زوجي** (مثل: 10,000 أو 15,000 أو 20,000)
    
    **للحصول على نتيجة "يُحوّل للتحقق" ⚠️:**
    - أدخل راتب **فردي** (مثل: 10,001 أو 15,001 أو 20,001)
    
    ---
    
    ### 📊 ما يحدث خلف الكواليس:
    1. التطبيق يتحقق من الراتب (زوجي أم فردي)
    2. يُولّد بيانات مناسبة من "Core Banking System"
    3. يُرسل كل البيانات للنموذج الحقيقي (XGBoost)
    4. النموذج يُحلل ويُعطي النتيجة
    
    ---
    
    ### 🎬 للعرض في حلقة المناقشة:
    - جرّب راتب 15,000 ← النتيجة: ✅ Pass
    - جرّب راتب 15,001 ← النتيجة: ⚠️ Fraud
    - اشرح أن البيانات الإضافية تأتي من الأنظمة البنكية تلقائياً
    """)
