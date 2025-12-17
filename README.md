# 🔍 Fraud Detection System

AI-Powered Loan Application Screening for Saudi Financial Institutions

## 📋 Project Information

- **University:** Midocean University
- **Program:** Master's in Informatics
- **Authors:** Alsiddiq & Mohammed Abdu
- **Supervisor:** Dr. Khaled Eskaf

## 🚀 Quick Start

### Local Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place `Final_model.pkl` in the root directory
4. Run the app:
   ```bash
   streamlit run app.py
   ```

### Deploy to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

## 📁 Project Structure

```
fraud_detection_app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── Final_model.pkl        # Trained XGBoost model
├── feature_names.json     # Feature names list
└── README.md              # This file
```

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| Accuracy | 100% |
| ROC-AUC | 1.000 |
| Precision | 100% |
| Recall | 100% |

## 🎯 Features

- **18 Input Features** for comprehensive fraud detection
- **Real-time Prediction** with XGBoost model
- **Interactive UI** with organized tabs
- **Location Visualization** with map integration
- **Professional Design** with custom styling

## 📝 Decision Logic

- **Pass**: Fraud probability ≤ 50%
- **Refer to Human**: Fraud probability > 50%

## 🔧 Configuration

Adjust the decision threshold in the sidebar (default: 50%)

## 📞 Support

For questions or issues, contact the project team.

---

© 2025 Midocean University | Master's Thesis Project
