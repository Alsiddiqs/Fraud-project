# =============================================================================
# FRAUD DETECTION WEB APPLICATION
# Master's Thesis Project - Midocean University
# Authors: Alsiddiq & Mohammed Abdu
# Supervisor: Dr. Khaled Eskaf
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, date
from pathlib import Path

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================

st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    /* Result boxes */
    .result-pass {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    
    .result-refer {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
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
        st.error("Model file not found. Please upload Final_model.pkl")
        return None

model = load_model()

# =============================================================================
# HEADER
# =============================================================================

st.markdown("""
<div class="header-container">
    <h1>🔍 Fraud Detection System</h1>
    <p>AI-Powered Loan Application Screening</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">Midocean University | Master's Thesis Project</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - SYSTEM INFO
# =============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/bank-building.png", width=150)
    st.markdown("### 🏦 System Information")
    st.markdown("""
    <div class="info-box">
        <b>Model:</b> XGBoost Pipeline<br>
        <b>Accuracy:</b> 100%<br>
        <b>ROC-AUC:</b> 1.000<br>
        <b>Features:</b> 18
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Decision Logic")
    st.markdown("""
    - **Pass**: Probability ≤ 50%
    - **Refer to Human**: Probability > 50%
    """)
    
    st.markdown("### 👥 Project Team")
    st.markdown("""
    - Alsiddiq
    - Mohammed Abdu
    - **Supervisor:** Dr. Khaled Eskaf
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    threshold = st.slider("Decision Threshold", 0.0, 1.0, 0.5, 0.05)

# =============================================================================
# MAIN FORM
# =============================================================================

st.markdown("## 📝 Loan Application Form")
st.markdown("Please fill in the application details below:")

# Create tabs for organized input
tab1, tab2, tab3, tab4 = st.tabs(["👤 Client Info", "📅 Dates", "🔐 Security", "📍 Location"])

# Initialize data dictionary
input_data = {}

# -----------------------------------------------------------------------------
# TAB 1: Client Information
# -----------------------------------------------------------------------------
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        input_data["ApplicationID"] = st.text_input(
            "Application ID",
            value=f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            help="Unique application identifier"
        )
        
        input_data["Names ClientName"] = st.text_input(
            "Client Name",
            placeholder="Enter full name",
            help="Full name of the applicant"
        )
        
        input_data["Phone Number"] = st.text_input(
            "Phone Number",
            placeholder="+966 5XX XXX XXXX",
            help="Saudi mobile number"
        )
    
    with col2:
        input_data["Email"] = st.text_input(
            "Email Address",
            placeholder="example@email.com",
            help="Valid email address"
        )
        
        input_data["Total Amounts"] = st.number_input(
            "Loan Amount (SAR)",
            min_value=0,
            max_value=10000000,
            value=50000,
            step=1000,
            help="Requested loan amount in Saudi Riyal"
        )
        
        input_data["Product Type"] = st.selectbox(
            "Product Type",
            options=["Personal Loan", "Auto Loan", "Mortgage", "Business Loan", "Credit Card"],
            help="Type of financial product"
        )

# -----------------------------------------------------------------------------
# TAB 2: Dates
# -----------------------------------------------------------------------------
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        input_data["Incident Start Date"] = st.date_input(
            "Application Date",
            value=date.today(),
            help="Date of application submission"
        )
        
        input_data["Complaint Date"] = st.date_input(
            "Complaint Date (if any)",
            value=date.today(),
            help="Date of complaint (if applicable)"
        )
        
        input_data["Account Opening Date"] = st.date_input(
            "Account Opening Date",
            value=date(2020, 1, 1),
            help="When the account was first opened"
        )
    
    with col2:
        input_data["Date of Last Password Change"] = st.date_input(
            "Last Password Change",
            value=date.today(),
            help="Date of most recent password change"
        )
        
        input_data["Date of Last Phone Number Change"] = st.date_input(
            "Last Phone Number Change",
            value=date.today(),
            help="Date of most recent phone number update"
        )

# -----------------------------------------------------------------------------
# TAB 3: Security Information
# -----------------------------------------------------------------------------
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        input_data["E-Services Login Session ID"] = st.text_input(
            "Session ID",
            value=f"SID-{np.random.randint(100000, 999999)}",
            help="Current login session identifier"
        )
        
        input_data["Login Channel"] = st.selectbox(
            "Login Channel",
            options=["Mobile App", "Web Browser", "ATM", "Branch", "Phone Banking"],
            help="Channel used for login"
        )
    
    with col2:
        input_data["Trusted Device Status"] = st.selectbox(
            "Trusted Device",
            options=["Yes", "No"],
            help="Is this a registered trusted device?"
        )
        
        input_data["Login IP Address"] = st.text_input(
            "IP Address",
            value="192.168.1.1",
            help="Client's IP address"
        )

# -----------------------------------------------------------------------------
# TAB 4: Location Information
# -----------------------------------------------------------------------------
with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        input_data["Login GPS Latitude"] = st.number_input(
            "GPS Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=24.7136,
            format="%.6f",
            help="Latitude coordinate"
        )
        
        input_data["Login GPS Longitude"] = st.number_input(
            "GPS Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=46.6753,
            format="%.6f",
            help="Longitude coordinate"
        )
    
    with col2:
        input_data["Login GPS Country"] = st.selectbox(
            "Country",
            options=["Saudi Arabia", "United Arab Emirates", "Kuwait", "Bahrain", 
                     "Qatar", "Oman", "Egypt", "Jordan", "Other"],
            help="Country of login"
        )
    
    # Show map
    st.markdown("#### 📍 Location Preview")
    map_data = pd.DataFrame({
        'lat': [input_data["Login GPS Latitude"]],
        'lon': [input_data["Login GPS Longitude"]]
    })
    st.map(map_data, zoom=5)

# =============================================================================
# PREDICTION
# =============================================================================

st.markdown("---")
st.markdown("## 🔍 Application Screening")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    predict_button = st.button("🚀 Screen Application", use_container_width=True, type="primary")

if predict_button:
    if model is None:
        st.error("❌ Model not loaded. Please check the model file.")
    else:
        with st.spinner("Analyzing application..."):
            try:
                # Prepare input data
                input_df = pd.DataFrame([input_data])
                
                # Convert date columns to datetime
                date_columns = [
                    "Incident Start Date", "Complaint Date", "Account Opening Date",
                    "Date of Last Password Change", "Date of Last Phone Number Change"
                ]
                for col in date_columns:
                    if col in input_df.columns:
                        input_df[col] = pd.to_datetime(input_df[col])
                
                # Get prediction
                proba = model.predict_proba(input_df)[:, 1][0]
                fraud_percentage = proba * 100
                
                # Display results
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Risk Score", f"{fraud_percentage:.1f}%")
                
                with col2:
                    st.metric("Threshold", f"{threshold * 100:.0f}%")
                
                with col3:
                    confidence = max(proba, 1-proba) * 100
                    st.metric("Confidence", f"{confidence:.1f}%")
                
                # Decision
                st.markdown("### 📋 Decision")
                
                if proba > threshold:
                    st.markdown("""
                    <div class="result-refer">
                        <h2>⚠️ REFER TO HUMAN</h2>
                        <p>This application requires manual review by the fraud team.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.warning("""
                    **Recommended Actions:**
                    - Verify client identity through additional documentation
                    - Contact client via registered phone number
                    - Review transaction history for anomalies
                    - Escalate to fraud investigation team if necessary
                    """)
                else:
                    st.markdown("""
                    <div class="result-pass">
                        <h2>✅ PASS</h2>
                        <p>This application has passed the automated screening.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.success("""
                    **Next Steps:**
                    - Proceed with standard credit assessment
                    - Verify income documentation
                    - Complete KYC requirements
                    - Issue final approval decision
                    """)
                
                # Application Summary
                with st.expander("📄 Application Summary"):
                    st.json(input_data)
                    
            except Exception as e:
                st.error(f"❌ Error during prediction: {str(e)}")
                st.info("Please ensure all fields are filled correctly.")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🎓 Master's Thesis Project | Midocean University | 2025</p>
    <p>Fraud Detection in Saudi Financial Institutions Using Machine Learning</p>
    <p style="font-size: 0.8rem;">Supervised by Dr. Khaled Eskaf</p>
</div>
""", unsafe_allow_html=True)
