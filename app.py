import json
import re
import streamlit as st
from google import genai
from PIL import Image

# Page setup
st.set_page_config(
    page_title="ScamCheck AI - Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CUSTOM CSS STYLING
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* Header Gradient Banner */
    .header-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .header-title { font-size: 2.2rem; font-weight: 700; margin: 0; color: #FFFFFF; }
    .header-subtitle { font-size: 1rem; color: #94A3B8; margin-top: 6px; }

    /* Custom Cards */
    .card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Status Badges */
    .badge-high {
        background-color: #FEF2F2; color: #DC2626; border: 1px solid #FCA5A5;
        padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; display: inline-block;
    }
    .badge-medium {
        background-color: #FFFBEB; color: #D97706; border: 1px solid #FCD34D;
        padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; display: inline-block;
    }
    .badge-low {
        background-color: #F0FDF4; color: #16A34A; border: 1px solid #86EFAC;
        padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; display: inline-block;
    }

    /* Custom Progress Bar Styling */
    .stProgress > div > div > div > div {
        border-radius: 10px;
    }

    /* Primary Action Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        height: 48px !important;
        transition: all 0.2s ease !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER SECTION
# ---------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div class="header-title">🛡️ ScamCheck AI</div>
    <div class="header-subtitle">Intelligent verification system for student job offers, internships, and company logos.</div>
</div>
""", unsafe_allow_html=True)

# API Key handling
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.text_input("Enter Gemini API Key to initialize system:", type="password")

# Local Pattern Matcher
def run_heuristic_check(text):
    flags = []
    t = text.lower()
    if re.search(r'\b(registration fee|security deposit|processing fee|laptop fee|pay for kit)\b', t):
        flags.append("Payment Demand: Explicitly asks for upfront fees.")
    if re.search(r'\b(telegram|whatsapp only|contact hr via whatsapp)\b', t):
        flags.append("Unofficial Channel: Restricts communication to instant messaging.")
    if re.search(r'\b(earn \$?\d+00|50000 per month for 2 hours)\b', t):
        flags.append("Irrealistic Compensation: Excessive salary for minimal effort.")
    return flags

# Main Navigation
tab_text, tab_logo = st.tabs(["📝 Verify Offer / Email", "🖼️ Verify Company Logo"])

# ---------------------------------------------------------
# TAB 1: TEXT OFFER ANALYZER
# ---------------------------------------------------------
with tab_text:
    col_main, col_presets = st.columns([2, 1])

    with col_presets:
        st.markdown("<div class='card'><b>💡 Preset Test Cases</b>", unsafe_allow_html=True)
        if st.button("🚨 Load Fake HR Scam"):
            st.session_state["text_input"] = "Congratulations! You are selected for HR Assistant at Amazon. Salary 50,000 INR/month. Work 2 hours daily from home. Pay 1,500 INR registration fee to process laptop kit. Contact HR on WhatsApp: 9876543210."
        if st.button("🟡 Load Telegram Offer"):
            st.session_state["text_input"] = "Urgent Hiring: Data Entry Operator needed. Pay: $200/day. No interview needed. Contact manager directly on Telegram @Jobs_HR_Fast."
        if st.button("✅ Load Official Internship"):
            st.session_state["text_input"] = "We are hiring a Software Engineer Intern at TechCorp. Requirements: Python, React. Apply through our official portal: https://techcorp.com/careers/intern-2026."
        st.markdown("</div>", unsafe_allow_html=True)

    with col_main:
        user_text = st.text_area(
            "Offer Details / Message Text", 
            value=st.session_state.get("text_input", ""), 
            height=180, 
            placeholder="Paste raw email header, WhatsApp message, or offer letter contents..."
        )
        analyze_btn = st.button("✨ Run Risk Analysis", type="primary")

    if analyze_btn:
        if not api_key:
            st.error("Missing Gemini API Key.")
        elif not user_text.strip():
            st.warning("Please paste some text to analyze.")
        else:
            local_flags = run_heuristic_check(user_text)
            
            with st.spinner("Processing analysis..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    Analyze this opportunity for scam indicators:
                    "{user_text}"

                    Return ONLY a JSON object:
                    {{
                        "risk_score": <number 0 to 100>,
                        "risk_level": "<Low | Medium | High>",
                        "warning_indicators": ["<warning 1>", "<warning 2>"],
                        "recommendation": "<practical instruction>"
                    }}
                    """
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt,
                    )
                    cleaned = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(cleaned)

                    # RESULTS CARD
                    score = data.get("risk_score", 0)
                    level = data.get("risk_level", "Unknown")

                    st.markdown("---")
                    st.subheader("Analysis Dashboard")

                    # Score Gauge and Level Badge
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.metric("Risk Score", f"{score} / 100")
                        st.progress(score / 100)
                    
                    with c2:
                        st.write("**Risk Classification:**")
                        if level == "High":
                            st.markdown('<span class="badge-high">🔴 HIGH RISK SCAM</span>', unsafe_allow_html=True)
                        elif level == "Medium":
                            st.markdown('<span class="badge-medium">🟡 MEDIUM RISK / CAUTION</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="badge-low">🟢 LOW RISK / APPEARS LEGIT</span>', unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Indicators Grid
                    col_flags, col_advice = st.columns(2)
                    with col_flags:
                        st.markdown("<div class='card'><b>⚠️ Identified Fraud Indicators</b>", unsafe_allow_html=True)
                        all_indicators = list(set(local_flags + data.get("warning_indicators", [])))
                        for ind in all_indicators:
                            st.markdown(f"• {ind}")
                        st.markdown("</div>", unsafe_allow_html=True)

                    with col_advice:
                        st.markdown("<div class='card'><b>💡 Recommended Next Steps</b>", unsafe_allow_html=True)
                        st.write(data.get("recommendation", "Always verify offers via official channels."))
                        st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error executing scan: {e}")

# ---------------------------------------------------------
# TAB 2: LOGO VERIFIER
# ---------------------------------------------------------
with tab_logo:
    col_up, col_preview = st.columns([1, 1])

    with col_up:
        uploaded_file = st.file_uploader("Upload Logo Image or Badge Header", type=["png", "jpg", "jpeg"])
        company_name = st.text_input("Claimed Company Name", placeholder="e.g. Amazon, Google, Microsoft")
        verify_logo_btn = st.button("🖼️ Inspect Logo Authenticity", type="primary")

    if verify_logo_btn:
        if not api_key:
            st.error("Missing API Key.")
        elif not uploaded_file:
            st.warning("Please upload an image first.")
        else:
            with st.spinner("Analyzing image..."):
                try:
                    img = Image.open(uploaded_file)
                    with col_preview:
                        st.image(img, caption="Uploaded Image Preview", width=220)

                    client = genai.Client(api_key=api_key)
                    logo_prompt = f"""
                    Inspect this image for brand authenticity claiming to be: "{company_name}".
                    Check for pixelation, edited text, missing trademarks, or unauthentic fonts.

                    Return ONLY a JSON object:
                    {{
                        "authenticity_score": <number 0 to 100>,
                        "visual_flaws": ["<flaw 1>", "<flaw 2>"],
                        "summary": "<brief summary>"
                    }}
                    """
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=[img, logo_prompt],
                    )
                    cleaned = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(cleaned)

                    st.markdown("---")
                    auth_score = data.get("authenticity_score", 0)

                    st.metric("Authenticity Score", f"{auth_score} / 100")
                    st.progress(auth_score / 100)

                    if auth_score >= 70:
                        st.markdown('<span class="badge-low">🟢 LIKELY AUTHENTIC LOGO</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="badge-high">🔴 HIGH LIKELIHOOD OF FAKE / ALTERED LOGO</span>', unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<div class='card'><b>🔍 Flaws Detected</b>", unsafe_allow_html=True)
                    for flaw in data.get("visual_flaws", []):
                        st.markdown(f"• {flaw}")
                    st.write(data.get("summary", ""))
                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error inspecting logo: {e}")
