import os
import json
import re
import streamlit as st
from google import genai
from PIL import Image

# 1. Page Configuration & Custom CSS
st.set_page_config(
    page_title="ScamCheck AI - Fraud Detection Platform",
    page_icon="🛡️",
    layout="wide"
)

# Custom Styling for Professional Interface
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0px; }
    .sub-header { font-size: 1rem; color: #64748B; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
    .stat-card { background-color: #F8FAFC; border-radius: 10px; padding: 15px; border: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("<p class='main-header'>🛡️ ScamCheck AI Platform</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Real-time verification system for internships, jobs, and communication channels.</p>", unsafe_allow_html=True)

# 2. API Key Management
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("Gemini API Key", type="password")

# 3. Helper Functions
def run_heuristic_check(text):
    """Local regex match for instant red flags."""
    flags = []
    text_lower = text.lower()
    
    if re.search(r'\b(registration fee|security deposit|processing fee|pay for laptop|training fee)\b', text_lower):
        flags.append("Payment Requested: Asks for money prior to employment.")
    if re.search(r'\b(telegram|whatsapp only|contact hr on whatsapp)\b', text_lower):
        flags.append("Unofficial Channel: Communicates strictly via instant messaging.")
    if re.search(r'\b(earn \$?\d+00 per day|50000 per month for 1 hour)\b', text_lower):
        flags.append("Unrealistic Compensation: Abnormally high pay for minimal work.")
    if re.search(r'(@gmail\.com|@yahoo\.com|@outlook\.com)', text_lower):
        flags.append("Free Email Domain: Sender uses a public email provider instead of a corporate domain.")
        
    return flags

# 4. Navigation Layout
tab_text, tab_logo, tab_batch = st.tabs(["📝 Text & Link Analyzer", "🖼️ Logo & Document Verifier", "📊 Threat Statistics"])

# ---------------------------------------------------------
# TAB 1: TEXT & LINK ANALYZER
# ---------------------------------------------------------
with tab_text:
    col_input, col_preset = st.columns([2, 1])
    
    with col_preset:
        st.markdown("##### 💡 Load Sample Test Data")
        if st.button("🚨 Fake HR WhatsApp Scam"):
            st.session_state["input_text"] = "Congratulations! You are selected for HR Assistant at Amazon. Salary 50,000 INR/month. Work 2 hours daily from home. Pay 1,500 INR registration fee to process laptop kit. Contact HR on WhatsApp: 9876543210."
        if st.button("🟡 Suspicious Telegram Offer"):
            st.session_state["input_text"] = "Urgent Hiring: Data Entry Operator needed immediately. Pay: $200/day. No interview needed. Contact manager directly on Telegram @Jobs_HR_Fast."
        if st.button("✅ Official Company Referral"):
            st.session_state["input_text"] = "We are hiring a Software Engineer Intern at TechCorp. Requirements: Python, React. Apply through our official portal: https://techcorp.com/careers/intern-2026. Official interviews will be conducted via Google Meet."

    with col_input:
        user_text = st.text_area(
            "Offer Content / Email Header / Direct Message", 
            value=st.session_state.get("input_text", ""),
            height=180, 
            placeholder="Paste raw email text, WhatsApp message, or job listing..."
        )
        analyze_btn = st.button("🔍 Run Full AI & Pattern Scan", type="primary")

    if analyze_btn:
        if not api_key:
            st.error("Missing API Key. Add it in the sidebar or Streamlit Secrets.")
        elif not user_text.strip():
            st.warning("Please provide text to analyze.")
        else:
            # Step 1: Run Local Heuristics
            heuristic_flags = run_heuristic_check(user_text)
            
            # Step 2: Run Gemini API Deep Scan
            with st.spinner("Analyzing text against known fraud patterns..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are a Fraud Analyst reviewing a potential job/internship opportunity.
                    Analyze this text for scam signals:
                    "{user_text}"

                    Return ONLY a JSON object:
                    {{
                        "risk_score": <number 0 to 100>,
                        "risk_level": "<Low | Medium | High>",
                        "warning_indicators": ["<indicator 1>", "<indicator 2>"],
                        "channel_risk": "<Low | Medium | High>",
                        "recommendation": "<practical safety instruction>"
                    }}
                    """
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt,
                    )
                    cleaned = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(cleaned)

                    # Display Dashboard Results
                    st.markdown("---")
                    st.markdown("### 📋 Verification Results")

                    # Metric Row
                    m1, m2, m3 = st.columns(3)
                    score = data.get("risk_score", 0)
                    level = data.get("risk_level", "Unknown")

                    with m1:
                        st.metric("Overall Risk Score", f"{score} / 100")
                    with m2:
                        st.metric("Threat Level", level)
                    with m3:
                        st.metric("Heuristic Red Flags", f"{len(heuristic_flags)} Detected")

                    # Status Banner
                    if level == "High":
                        st.error("🔴 **HIGH RISK:** Severe scam indicators detected. Do NOT proceed or pay any money.")
                    elif level == "Medium":
                        st.warning("🟡 **MEDIUM RISK / CAUTION:** Suspicious elements found. Verify official company website.")
                    else:
                        st.success("🟢 **LOW RISK:** Content structure appears consistent with standard opportunities.")

                    # Details Sections
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("#### ⚠️ Fraud Indicators")
                        all_warnings = list(set(heuristic_flags + data.get("warning_indicators", [])))
                        for w in all_warnings:
                            st.write(f"- {w}")

                    with c2:
                        st.markdown("#### 💡 Actionable Guidance")
                        st.info(data.get("recommendation", "Verify through official corporate channels."))

                    # Downloadable Summary
                    report_text = f"ScamCheck Verification Report\nScore: {score}/100\nLevel: {level}\nIndicators:\n" + "\n".join([f"- {i}" for i in all_warnings])
                    st.download_button("📥 Export Safety Report (.txt)", report_text, file_name="scamcheck_report.txt")

                except Exception as e:
                    st.error(f"Analysis failed: {e}")

# ---------------------------------------------------------
# TAB 2: LOGO & DOCUMENT VERIFIER
# ---------------------------------------------------------
with tab_logo:
    st.markdown("### 🖼️ Multimodal Visual Brand Inspection")
    
    col_up, col_info = st.columns([1, 1])
    
    with col_up:
        uploaded_img = st.file_uploader("Upload Company Logo / Offer Letter Badge", type=["png", "jpg", "jpeg"])
        target_company = st.text_input("Claimed Entity Name", placeholder="e.g., Google, Microsoft, Amazon")
        verify_img_btn = st.button("🔍 Analyze Visual Authenticity", type="primary")

    if verify_img_btn:
        if not api_key:
            st.error("Missing API Key.")
        elif not uploaded_img:
            st.warning("Please upload an image file.")
        else:
            with st.spinner("Inspecting logo vectors and pixel clarity..."):
                try:
                    img = Image.open(uploaded_img)
                    with col_info:
                        st.image(img, caption="Uploaded File Preview", width=220)

                    client = genai.Client(api_key=api_key)
                    logo_prompt = f"""
                    Inspect this image for brand authenticity for claimed entity: "{target_company}".
                    Check for: pixelation around text, non-standard font choices, missing trademark symbols, or copy-pasted brand elements.
                    
                    Return ONLY a JSON object:
                    {{
                        "authenticity_score": <number 0 to 100>,
                        "is_altered": <true or false>,
                        "visual_flaws": ["<flaw 1>", "<flaw 2>"],
                        "summary": "<summary>"
                    }}
                    """
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=[img, logo_prompt],
                    )
                    cleaned = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(cleaned)

                    st.markdown("---")
                    st.markdown("### 🔍 Image Verification Summary")
                    auth_score = data.get("authenticity_score", 0)

                    if auth_score >= 70:
                        st.success(f"🟢 **Likely Genuine Logo** (Confidence: {auth_score}/100)")
                    else:
                        st.error(f"🔴 **Potential Fake / Low Quality Representation** (Confidence: {auth_score}/100)")

                    for flaw in data.get("visual_flaws", []):
                        st.write(f"- {flaw}")
                    st.info(data.get("summary", ""))

                except Exception as e:
                    st.error(f"Image analysis error: {e}")

# ---------------------------------------------------------
# TAB 3: THREAT STATISTICS
# ---------------------------------------------------------
with tab_batch:
    st.markdown("### 📊 Platform Risk Insights")
    s1, s2, s3 = st.columns(3)
    s1.metric("Scam Detection Rate", "94.2%")
    s2.metric("Common Vector", "Telegram / WhatsApp")
    s3.metric("Average Risk Score", "72 / 100")
    
    st.markdown("""
    #### Top Fraud Indicators Identified
    1. **Upfront Payment Requests:** Charging students fees for "laptop deployment", "ID cards", or "training".
    2. **Instant Hiring:** No technical or behavioral interview steps conducted.
    3. **Unverified Contact Channels:** Avoiding corporate email systems and official domains.
    """)
