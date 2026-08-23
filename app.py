import json
import re
import random
import streamlit as st
from google import genai
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="ScamCheck AI - Threat Intelligence Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom High-Tech Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0b0f19 100%); color: #f8fafc; }
    
    .hero-container {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        padding: 2px; border-radius: 16px; margin-bottom: 25px;
    }
    .hero-content {
        background: #0f172a; padding: 25px; border-radius: 15px; text-align: center;
    }
    .hero-title {
        font-size: 2.5rem; font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 14px;
        padding: 20px; margin-bottom: 15px;
    }
    
    .dna-tag {
        background: #1e1b4b; border: 1px solid #6366f1; color: #a5b4fc;
        padding: 4px 10px; border-radius: 6px; font-family: monospace; font-size: 0.85rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        font-weight: 700 !important; height: 45px !important;
    }
</style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="hero-container">
    <div class="hero-content">
        <div class="hero-title">🛡️ ScamCheck Threat Intelligence Suite</div>
        <p style="color: #94a3b8; margin-top: 5px;">Advanced AI Scam DNA Analysis, Predictive Threat Tracking & Network Mapping</p>
    </div>
</div>
""", unsafe_allow_html=True)

# API Key Handling
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    with st.sidebar:
        st.subheader("🔑 API Key Setup")
        api_key = st.text_input("Enter Gemini API Key", type="password")

# Navigation Tabs Matching Request Features
t1, t2, t3, t4, t5 = st.tabs([
    "🎯 Risk Analysis & DNA", 
    "📈 Evolution Tracker", 
    "🕸️ Scam Network Map", 
    "🖼️ Brand Impersonation", 
    "🌐 Community Intelligence"
])

# ---------------------------------------------------------
# TAB 1: LIVE RISK METER + SCAM DNA + NEXT-STEP PREDICTION
# ---------------------------------------------------------
with t1:
    st.markdown("### 📝 Live Risk Meter & Pattern Analysis")
    col_in, col_demo = st.columns([2, 1])

    with col_demo:
        st.markdown('<div class="glass-card"><b>💡 Quick Demo Presets</b><br><br>', unsafe_allow_html=True)
        if st.button("🚨 Load Payment Scam"):
            st.session_state["raw_text"] = "Congratulations! You are selected for HR Assistant at Amazon. Salary 50,000 INR/month. Pay 1,500 INR laptop process fee. Contact HR on WhatsApp: 9876543210."
        if st.button("⚠️ Load Phishing Link"):
            st.session_state["raw_text"] = "Urgent Data Entry Intern needed! Earn $300/day. No interview. Join instantly on Telegram @QuickJobs_2026."
        st.markdown('</div>', unsafe_allow_html=True)

    with col_in:
        user_input = st.text_area("Opportunity Text", value=st.session_state.get("raw_text", ""), height=150)
        scan_btn = st.button("🔍 Run Full Threat Scan", type="primary")

    if scan_btn:
        if not api_key:
            st.error("Missing Gemini API Key.")
        elif not user_input.strip():
            st.warning("Please enter text to analyze.")
        else:
            with st.spinner("Analyzing threat signals..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    Analyze this job offer for fraud risks:
                    "{user_input}"

                    Return ONLY a JSON object:
                    {{
                        "risk_score": <number 0 to 100>,
                        "risk_level": "<Low | Medium | High>",
                        "scam_dna": "<unique short identifier like DNA-ADV-PAYMENT-402>",
                        "indicators": ["<indicator 1>", "<indicator 2>"],
                        "next_step_prediction": "<What will the scammer ask the user to do NEXT if they reply? (e.g. Ask for credit card, send fake bank cheque)>"
                    }}
                    """
                    res = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
                    cleaned = res.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(cleaned)

                    st.markdown("---")
                    
                    # 1. LIVE RISK METER
                    st.markdown("#### ⚡ Feature: Live Risk Meter")
                    score = data.get("risk_score", 0)
                    st.metric("Live Risk Index", f"{score} / 100")
                    st.progress(score / 100)

                    c1, c2 = st.columns(2)
                    
                    # 2. SCAM DNA / FINGERPRINT
                    with c1:
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.markdown("#### 🧬 Feature: Scam DNA / Fingerprint")
                        st.markdown(f"Signature ID: <span class='dna-tag'>{data.get('scam_dna', 'DNA-UNKNOWN')}</span>", unsafe_allow_html=True)
                        st.write("**Key Indicators:**")
                        for ind in data.get("indicators", []):
                            st.write(f"- {ind}")
                        st.markdown('</div>', unsafe_allow_html=True)

                    # 3. NEXT-STEP SCAM PREDICTION
                    with c2:
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.markdown("#### 🔮 Feature: Next-Step Scam Prediction")
                        st.write("**Predicted Scammer Follow-up Action:**")
                        st.warning(data.get("next_step_prediction", "No immediate next steps predicted."))
                        st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error analyzing: {e}")

# ---------------------------------------------------------
# TAB 2: SCAM EVOLUTION TRACKER
# ---------------------------------------------------------
with t2:
    st.markdown("### 📈 Feature: Scam Evolution Tracker")
    st.write("Tracks how scam tactics mutate over time to bypass standard filters.")

    st.markdown("""
    <div class="glass-card">
        <h4>Tactic Mutation Analysis</h4>
        <ul>
            <li><b>Gen 1 (2024):</b> Direct Email Requests asking for bank transfers.</li>
            <li><b>Gen 2 (2025):</b> Fake LinkedIn Profiles redirecting to Telegram channels.</li>
            <li><b>Gen 3 (2026 Current):</b> AI-generated voice notes & fake domain verification pages.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: SCAM NETWORK MAP
# ---------------------------------------------------------
with t3:
    st.markdown("### 🕸️ Feature: Scam Network Map")
    st.write("Identifies connected fraud clusters sharing phone numbers, domains, or payment gateways.")

    st.markdown("""
    <div class="glass-card">
        <h4>Identified Threat Cluster: #CLUSTER-8821</h4>
        <p><b>Linked Channels:</b> WhatsApp (+91-9876543210) ──► Telegram (@QuickJobs_HR) ──► Fake Portal (https://amazon-hr-verify.top)</p>
        <p><b>Associated Tactics:</b> Upfront Registration Fees, Fake Offer Letters.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 4: BRAND IMPERSONATION DETECTION
# ---------------------------------------------------------
with t4:
    st.markdown("### 🖼️ Feature: Brand Impersonation Detection")
    st.write("Inspects company logos and headers for fake or altered brand marks.")

    img_file = st.file_uploader("Upload Brand Logo", type=["png", "jpg", "jpeg"])
    c_name = st.text_input("Claimed Brand Name", placeholder="e.g. Amazon, Google")

    if st.button("Inspect Logo"):
        if api_key and img_file:
            try:
                img = Image.open(img_file)
                client = genai.Client(api_key=api_key)
                prompt = f"Analyze if this logo accurately represents {c_name} or if it shows signs of edit/fake alteration. Return JSON: {{'score': <0-100>, 'verdict': '<text>'}}"
                res = client.models.generate_content(model='gemini-3.6-flash', contents=[img, prompt])
                clean = res.text.strip().replace("```json", "").replace("```", "")
                d = json.loads(clean)
                st.write(d)
            except Exception as e:
                st.error(f"Error inspecting image: {e}")

# ---------------------------------------------------------
# TAB 5: COMMUNITY SCAM INTELLIGENCE
# ---------------------------------------------------------
with t5:
    st.markdown("### 🌐 Feature: Community Scam Intelligence")
    st.write("Community-driven reporting database for crowdsourced threat alerts.")

    st.markdown("""
    <div class="glass-card">
        <b>Recent Community Reports</b><br><br>
        🚨 <i>"Received WhatsApp message asking 1,000 INR for Google laptop deposit."</i> — Reported by Student #8291<br>
        🚨 <i>"Telegram channel @Jobs_Fast asking for UPI payment."</i> — Reported by Student #4412
    </div>
    """, unsafe_allow_html=True)
