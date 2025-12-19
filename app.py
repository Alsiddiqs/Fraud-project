import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import time
import random
import hashlib

# ==============================
# Page Configuration
# ==============================
st.set_page_config(
    page_title="EMKAN Finance | Loan Application",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# Hide Streamlit Elements & Custom CSS
# ==============================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Full page background */
    .stApp {
        background: linear-gradient(135deg, #3f3d73 0%, #4a4fa3 100%);
        min-height: 100vh;
    }
    
    /* Form Card */
    .form-card {
        background: white;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Stepper */
    .stepper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
        gap: 10px;
    }
    
    .step {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 14px;
    }
    
    .step-active {
        background: #6f86e8;
        color: white;
    }
    
    .step-completed {
        background: #10b981;
        color: white;
    }
    
    .step-inactive {
        background: #e5e7eb;
        color: #9ca3af;
    }
    
    .step-line {
        width: 40px;
        height: 2px;
        background: #e5e7eb;
    }
    
    .step-line-active {
        background: #6f86e8;
    }
    
    /* Form Title */
    .form-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .form-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #e5e7eb !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #6f86e8 !important;
        box-shadow: 0 0 0 3px rgba(111, 134, 232, 0.1) !important;
    }
    
    /* Labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        font-weight: 600 !important;
        color: #374151 !important;
        font-size: 0.95rem !important;
    }
    
    /* Primary Button */
    .stButton > button {
        background: linear-gradient(135deg, #6f86e8 0%, #5a6fd6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(111, 134, 232, 0.4);
    }
    
    /* Success Card */
    .success-card {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 3rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
    }
    
    /* Referral Card - Changed from yellow to red/orange */
    .referral-card {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        padding: 3rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(220, 38, 38, 0.3);
    }
    
    /* Info Card */
    .info-card {
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
        padding: 3rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
    }
    
    /* Thank you Card */
    .thankyou-card {
        background: linear-gradient(135deg, #6b7280 0%, #9ca3af 100%);
        padding: 3rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(107, 114, 128, 0.3);
    }
    
    /* Offer Amount */
    .offer-amount {
        font-size: 3rem;
        font-weight: 800;
        margin: 1.5rem 0;
    }
    
    /* Progress items - FIXED COLORS */
    .progress-item-success {
        background: #d1fae5;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #10b981;
        color: #065f46;
        font-weight: 500;
    }
    
    .progress-item-warning {
        background: #fee2e2;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #ef4444;
        color: #991b1b;
        font-weight: 500;
    }
    
    /* Researcher info */
    .researcher-info {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin-top: 2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# Session State Initialization
# ==============================
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'is_fraud' not in st.session_state:
    st.session_state.is_fraud = False
if 'offer_amount' not in st.session_state:
    st.session_state.offer_amount = 0

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
# Helper Functions
# ==============================
def hash_to_int(value):
    if value is None:
        return 0
    return int(hashlib.md5(str(value).encode()).hexdigest()[:8], 16) % 1000000

def datetime_to_int(dt):
    if isinstance(dt, pd.Timestamp):
        return int(dt.timestamp())
    elif isinstance(dt, datetime):
        return int(dt.timestamp())
    elif isinstance(dt, str):
        try:
            return int(pd.to_datetime(dt).timestamp())
        except:
            return 0
    return 0

def prepare_model_input(is_fraud_scenario):
    now = datetime.now()
    
    if is_fraud_scenario:
        input_dict = {
            'ApplicationID': hash_to_int(f"RTL_{now.strftime('%y%m%d')}_{random.randint(1000,9999)}"),
            'Names ClientName': hash_to_int("Fraud User"),
            'Incident Start Date': datetime_to_int(now - timedelta(days=1)),
            'Total Amounts': 250000.0,
            'Complaint Date': datetime_to_int(now),
            'Account Opening Date': datetime_to_int(now - timedelta(days=30)),
            'Date of Last Password Change': datetime_to_int(now - timedelta(hours=2)),
            'Date of Last Phone Number Change': datetime_to_int(now - timedelta(days=1)),
            'Phone Number': 599000000 + random.randint(100000, 999999),
            'Email': hash_to_int("temp_fraud@gmail.com"),
            'E-Services Login Session ID': hash_to_int(f"SES_{random.randint(100000000, 999999999)}"),
            'Login Channel': 1,
            'Trusted Device Status': 0,
            'Product Type': 1,
            'Login IP Address': hash_to_int("178.89.254.15"),
            'Login GPS Latitude': 11.018906,
            'Login GPS Longitude': 106.560421,
            'Login GPS Country': 1
        }
    else:
        input_dict = {
            'ApplicationID': hash_to_int(f"RTL_{now.strftime('%y%m%d')}_{random.randint(1000,9999)}"),
            'Names ClientName': hash_to_int("Normal User"),
            'Incident Start Date': datetime_to_int(now - timedelta(days=180)),
            'Total Amounts': 25000.0,
            'Complaint Date': datetime_to_int(now - timedelta(days=179)),
            'Account Opening Date': datetime_to_int(now - timedelta(days=730)),
            'Date of Last Password Change': datetime_to_int(now - timedelta(days=60)),
            'Date of Last Phone Number Change': datetime_to_int(now - timedelta(days=365)),
            'Phone Number': 579000000 + random.randint(100000, 999999),
            'Email': hash_to_int("user_normal@yahoo.com"),
            'E-Services Login Session ID': hash_to_int(f"SES_{random.randint(100000000, 999999999)}"),
            'Login Channel': 0,
            'Trusted Device Status': 1,
            'Product Type': 0,
            'Login IP Address': hash_to_int("139.149.137.132"),
            'Login GPS Latitude': 24.7136,
            'Login GPS Longitude': 46.6753,
            'Login GPS Country': 0
        }
    
    return pd.DataFrame([input_dict])

def render_stepper(current_step):
    steps_html = '<div class="stepper">'
    for i in range(1, 5):
        if i < current_step:
            steps_html += f'<div class="step step-completed">✓</div>'
        elif i == current_step:
            steps_html += f'<div class="step step-active">{i}</div>'
        else:
            steps_html += f'<div class="step step-inactive">{i}</div>'
        
        if i < 4:
            line_class = "step-line step-line-active" if i < current_step else "step-line"
            steps_html += f'<div class="{line_class}"></div>'
    
    steps_html += '</div>'
    st.markdown(steps_html, unsafe_allow_html=True)

def render_left_panel():
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem;">
            💳 EMKAN Finance
        </h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-bottom: 2rem;">
            Digital Financing Solutions
        </p>
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; margin: 20px 0;">
            <p style="color: white; font-size: 1rem; margin: 8px 0;">✅ Instant Approval</p>
            <p style="color: white; font-size: 1rem; margin: 8px 0;">✅ Shariah Compliant</p>
            <p style="color: white; font-size: 1rem; margin: 8px 0;">✅ No Branch Visit Required</p>
            <p style="color: white; font-size: 1rem; margin: 8px 0;">✅ Competitive Rates</p>
            <p style="color: white; font-size: 1rem; margin: 8px 0;">✅ Up to 60 Months Tenure</p>
        </div>
        <div class="researcher-info">
            <p style="color: rgba(255,255,255,0.7); font-size: 0.75rem;">🎓 Master's Thesis Project</p>
            <p style="color: white; font-size: 0.85rem; font-weight: 600;">Fraud Detection Using AI</p>
            <p style="color: rgba(255,255,255,0.8); font-size: 0.75rem; margin-top: 8px;">
                ELSEDEEG MOAHMEDELBASHER ABDALLA AHMED
            </p>
            <p style="color: rgba(255,255,255,0.8); font-size: 0.75rem;">
                MOHAMED ABDELSATART
            </p>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.7rem; margin-top: 8px;">
                Supervisor: Dr. Khaled Iskaf
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# PAGE 1: Application Form
# ==============================
def page_application_form():
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        render_left_panel()
    
    with right_col:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        render_stepper(1)
        
        st.markdown('<p class="form-title">Apply for Finance</p>', unsafe_allow_html=True)
        st.markdown('<p class="form-subtitle">Already have an account? <a href="#" style="color: #6f86e8;">Login</a></p>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### Your Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", placeholder="Enter your full name")
            national_id = st.text_input("National ID / Iqama", placeholder="10 digits", max_chars=10)
            mobile = st.text_input("Mobile Number", placeholder="5XXXXXXXX", max_chars=9)
            employment = st.selectbox("Employment Sector", ["Private Sector", "Government", "Semi-Government"])
        
        with col2:
            email = st.text_input("Email Address", placeholder="example@email.com")
            age = st.number_input("Age", min_value=18, max_value=65, value=30)
            salary = st.number_input("Basic Monthly Salary (SAR)", min_value=2000, max_value=500000, value=10000, step=500)
            requested_amount = st.number_input("Requested Finance Amount (SAR)", min_value=5000, max_value=1500000, value=50000, step=5000)
        
        st.markdown("")
        
        agree = st.checkbox("I agree to the Terms & Conditions and Privacy Policy")
        consent = st.checkbox("I consent to EMKAN retrieving my data from third parties (SIMAH, National Address)")
        
        st.markdown("")
        
        if st.button("Continue", disabled=not (agree and consent and full_name and national_id)):
            if len(national_id) != 10 or not national_id.isdigit():
                st.error("❌ National ID must be exactly 10 digits")
            elif len(mobile) != 9 or not mobile.isdigit():
                st.error("❌ Mobile number must be 9 digits (without +966)")
            else:
                st.session_state.form_data = {
                    'full_name': full_name,
                    'national_id': national_id,
                    'mobile': mobile,
                    'email': email,
                    'age': age,
                    'employment': employment,
                    'salary': salary,
                    'requested_amount': requested_amount
                }
                st.session_state.is_fraud = (salary % 2 != 0)
                st.session_state.offer_amount = salary * 3
                st.session_state.page = 2
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# PAGE 2: Fetching Data
# ==============================
def page_fetching_data():
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        render_left_panel()
    
    with right_col:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        render_stepper(2)
        
        st.markdown('<p class="form-title">Verifying Your Information</p>', unsafe_allow_html=True)
        st.markdown('<p class="form-subtitle">Please wait while we retrieve your data from official sources...</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        is_fraud = st.session_state.is_fraud
        
        data_items = [
            ("Connecting to Core Banking System...", "Core Banking System", "Connected", True),
            ("Generating Application ID...", "Application ID", f"RTL_{datetime.now().strftime('%y%m%d')}_{random.randint(1000,9999)}", True),
            ("Verifying National ID...", "National ID", st.session_state.form_data.get('national_id', 'N/A'), True),
            ("Connecting to SIMAH Credit Bureau...", "SIMAH Connection", "Established", True),
            ("Retrieving Credit Score...", "Credit Score", "750 (Excellent)" if not is_fraud else "520 (Fair)", not is_fraud),
            ("Checking Credit History...", "Credit History", "No defaults" if not is_fraud else "2 late payments", not is_fraud),
            ("Retrieving National Address...", "National Address", "Riyadh, Saudi Arabia" if not is_fraud else "Address mismatch", not is_fraud),
            ("Verifying Client Name...", "Client Name", st.session_state.form_data.get('full_name', 'N/A'), True),
            ("Verifying Phone Number...", "Phone Number", f"+966 {st.session_state.form_data.get('mobile', 'N/A')}", True),
            ("Verifying Email Address...", "Email", st.session_state.form_data.get('email', 'N/A'), True),
            ("Retrieving Account Opening Date...", "Account Age", "3 Years" if not is_fraud else "25 Days", not is_fraud),
            ("Checking Last Password Change...", "Password Changed", "45 days ago" if not is_fraud else "2 hours ago", not is_fraud),
            ("Checking Last Phone Number Change...", "Phone Changed", "1 year ago" if not is_fraud else "Yesterday", not is_fraud),
            ("Verifying Device Status...", "Device Status", "Trusted" if not is_fraud else "Newly Registered", not is_fraud),
            ("Checking Login Channel...", "Login Channel", "Mobile App" if not is_fraud else "Phone Banking", True),
            ("Generating Session ID...", "Session ID", f"SES_{random.randint(100000000, 999999999)}", True),
            ("Verifying GPS Location...", "GPS Location", "Riyadh, Saudi Arabia" if not is_fraud else "Ho Chi Minh, Vietnam", not is_fraud),
            ("Checking IP Address...", "IP Address", "139.149.137.132 (Saudi)" if not is_fraud else "178.89.254.15 (Foreign)", not is_fraud),
            ("Retrieving Employment Data...", "Employment", st.session_state.form_data.get('employment', 'N/A'), True),
            ("Verifying Salary Information...", "Monthly Salary", f"SAR {st.session_state.form_data.get('salary', 0):,}", True),
            ("Calculating Total Amount...", "Total Amount", f"SAR {st.session_state.form_data.get('requested_amount', 0):,}", True),
        ]
        
        progress_bar = st.progress(0)
        status_container = st.empty()
        results_container = st.container()
        
        with results_container:
            for i, (status_msg, field_name, field_value, is_ok) in enumerate(data_items):
                progress = (i + 1) / len(data_items)
                progress_bar.progress(progress)
                
                status_container.info(f"🔄 {status_msg}")
                
                time.sleep(0.7)
                
                # FIXED: Using CSS classes with visible text colors
                icon = "✅" if is_ok else "⚠️"
                item_class = "progress-item-success" if is_ok else "progress-item-warning"
                
                st.markdown(f"""
                <div class="{item_class}">
                    {icon} <strong>{field_name}:</strong> {field_value}
                </div>
                """, unsafe_allow_html=True)
        
        status_container.success("✅ All data retrieved successfully!")
        time.sleep(1)
        
        st.markdown("---")
        st.markdown("#### 🤖 Running AI Fraud Detection Model...")
        
        model_progress = st.progress(0)
        for i in range(100):
            model_progress.progress(i + 1)
            time.sleep(0.02)
        
        if model is not None:
            try:
                df_input = prepare_model_input(st.session_state.is_fraud)
                prediction = model.predict(df_input)[0]
                st.session_state.is_fraud = (prediction == 1)
            except:
                pass
        
        st.success("✅ Analysis Complete!")
        time.sleep(1)
        
        st.session_state.page = 3
        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# PAGE 3a: Offer Page (PASS)
# ==============================
def page_offer():
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        render_left_panel()
    
    with right_col:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        render_stepper(3)
        
        st.markdown(f"""
        <div class="success-card">
            <h2 style="margin-bottom: 0.5rem;">🎉 Congratulations!</h2>
            <p style="opacity: 0.9; font-size: 1.1rem;">Your application has been approved</p>
            <div class="offer-amount">SAR {st.session_state.offer_amount:,}</div>
            <p style="opacity: 0.9;">Based on 3x your basic salary</p>
            <p style="font-size: 0.9rem; margin-top: 1rem; opacity: 0.8;">
                Monthly Installment: SAR {st.session_state.offer_amount // 36:,} (36 months)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("#### Offer Details")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Applicant:** {st.session_state.form_data.get('full_name', 'N/A')}")
            st.markdown(f"**Basic Salary:** SAR {st.session_state.form_data.get('salary', 0):,}")
            st.markdown(f"**Finance Amount:** SAR {st.session_state.offer_amount:,}")
        with col2:
            st.markdown("**APR:** 15% per annum")
            st.markdown("**Tenure:** Up to 60 months")
            st.markdown("**Processing Fee:** SAR 500")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Accept Offer", use_container_width=True):
                st.session_state.page = 4
                st.rerun()
        with col2:
            if st.button("❌ Decline Offer", use_container_width=True):
                st.session_state.page = 5
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# PAGE 3b: Referral Page (FRAUD) - FIXED COLOR
# ==============================
def page_referral():
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        render_left_panel()
    
    with right_col:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        render_stepper(3)
        
        # FIXED: Changed from yellow to red for consistency
        st.markdown("""
        <div class="referral-card">
            <h2 style="margin-bottom: 0.5rem;">📋 Additional Verification Required</h2>
            <p style="opacity: 0.9; font-size: 1.1rem; margin-top: 1rem;">
                Your application requires additional review.
            </p>
            <p style="opacity: 0.9; font-size: 1rem; margin-top: 1.5rem;">
                Our verification team will contact you within <strong>24-48 hours</strong> 
                to request additional information and complete your application.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("#### What happens next?")
        
        st.markdown("""
        1. **Our team will review** your application details
        2. **A representative will call** you at the registered mobile number
        3. **Additional documents** may be requested for verification
        4. **Final decision** will be communicated within 3-5 business days
        """)
        
        st.markdown("---")
        
        st.markdown(f"""
        **Application Reference:** RTL_{datetime.now().strftime('%y%m%d')}_{random.randint(1000,9999)}  
        **Applicant:** {st.session_state.form_data.get('full_name', 'N/A')}  
        **Contact Number:** +966 {st.session_state.form_data.get('mobile', 'N/A')}
        """)
        
        st.markdown("")
        
        if st.button("OK, I Understand", use_container_width=True):
            st.session_state.page = 5
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# PAGE 4: Processing (Approved)
# ==============================
def page_processing():
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        render_left_panel()
    
    with right_col:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        render_stepper(4)
        
        st.markdown(f"""
        <div class="info-card">
            <h2 style="margin-bottom: 0.5rem;">⏳ Processing Your Application</h2>
            <p style="opacity: 0.9; font-size: 1.1rem; margin-top: 1rem;">
                Thank you for choosing EMKAN Finance!
            </p>
            <p style="opacity: 0.9; font-size: 1rem; margin-top: 1.5rem;">
                Your application is being processed. We will contact you within 
                <strong>24 hours</strong> to finalize your finance agreement.
            </p>
            <div style="margin-top: 2rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px;">
                <p style="font-size: 0.9rem; margin: 0;">
                    📱 Keep your phone available for our call
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("#### Application Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Applicant:** {st.session_state.form_data.get('full_name', 'N/A')}")
            st.markdown(f"**National ID:** {st.session_state.form_data.get('national_id', 'N/A')}")
            st.markdown(f"**Mobile:** +966 {st.session_state.form_data.get('mobile', 'N/A')}")
        with col2:
            st.markdown(f"**Approved Amount:** SAR {st.session_state.offer_amount:,}")
            st.markdown(f"**Status:** Approved ✅")
            st.markdown(f"**Reference:** RTL_{datetime.now().strftime('%y%m%d')}_{random.randint(1000,9999)}")
        
        st.markdown("---")
        
        if st.button("Submit New Application", use_container_width=True):
            st.session_state.page = 1
            st.session_state.form_data = {}
            st.session_state.is_fraud = False
            st.session_state.offer_amount = 0
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# PAGE 5: Thank You
# ==============================
def page_thankyou():
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        render_left_panel()
    
    with right_col:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        render_stepper(4)
        
        st.markdown("""
        <div class="thankyou-card">
            <h2 style="margin-bottom: 0.5rem;">Thank You</h2>
            <p style="opacity: 0.9; font-size: 1.1rem; margin-top: 1rem;">
                Thank you for contacting EMKAN Finance.
            </p>
            <p style="opacity: 0.9; font-size: 1rem; margin-top: 1.5rem;">
                We appreciate your interest in our services. 
                Feel free to apply again whenever you need financing assistance.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("#### Need Help?")
        
        st.markdown("""
        📞 **Customer Service:** 920011038  
        📧 **Email:** support@emkanfinance.com.sa  
        🌐 **Website:** www.emkanfinance.com.sa
        """)
        
        st.markdown("---")
        
        if st.button("Start New Application", use_container_width=True):
            st.session_state.page = 1
            st.session_state.form_data = {}
            st.session_state.is_fraud = False
            st.session_state.offer_amount = 0
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# Main Router
# ==============================
def main():
    current_page = st.session_state.page
    
    if current_page == 1:
        page_application_form()
    elif current_page == 2:
        page_fetching_data()
    elif current_page == 3:
        if st.session_state.is_fraud:
            page_referral()
        else:
            page_offer()
    elif current_page == 4:
        page_processing()
    elif current_page == 5:
        page_thankyou()

if __name__ == "__main__":
    main()
