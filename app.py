import os
import json
import streamlit as st
from google import genai
from PIL import Image

# Page configuration
st.set_page_config(page_title="ScamCheck", page_icon="🛡️")

st.title("🛡️ ScamCheck: Opportunity & Logo Verifier")
st.write("Analyze suspicious offer messages, emails, or company logos to detect scams.")

# Retrieve API Key (From Secrets or Manual Input)

api_key = st.secrets.get("GEMINI_API_KEY", "")

# Tabs for dual features
tab1, tab2 = st.tabs(["📝 Text Offer Verification", "🖼️ Logo Verification"])

# ---------------------------------------------------------
# TAB 1: TEXT OFFER VERIFICATION
# ---------------------------------------------------------
with tab1:
    st.markdown("### Quick Demo Presets")
    col1, col2 = st.columns(2)

    sample_text = ""
    if col1.button("🚨 Load Fake WhatsApp Job Scam"):
        sample_text = "Congratulations! You are selected for HR Assistant at Amazon. Salary 50,000 INR/month. Work 2 hours daily from home. Pay 1,500 INR registration fee to process laptop kit. Contact HR on WhatsApp: 9876543210."
    if col2.button("✅ Load Legitimate Internship"):
        sample_text = "We are hiring a Software Engineer Intern at TechCorp. Requirements: Python, React. Apply through our official portal: https://techcorp.com/careers/intern-2026. Official interviews will be conducted via Google Meet."

    user_input = st.text_area("Offer Text / Email / Message", value=sample_text, height=150, placeholder="Paste email or message here...")

    if st.button("🔍 Analyze Text Opportunity", type="primary"):
        if not api_key:
            st.error("Please provide a Gemini API Key.")
        elif not user_input.strip():
            st.warning("Please paste some text to analyze.")
        else:
            with st.spinner("Analyzing text for scam indicators..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    Analyze this job offer text for fraud risks (e.g., registration fees, WhatsApp-only contacts, unrealistic salary).
                    Text: "{user_input}"
                    
                    Return ONLY a JSON object:
                    {{
                        "risk_score": <0-100>,
                        "risk_level": "<Low | Medium | High>",
                        "warning_indicators": ["<warning 1>", "<warning 2>"],
                        "recommendation": "<advice>"
                    }}
                    """
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    
                    cleaned = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(cleaned)

                    st.markdown("---")
                    score = data.get("risk_score", 0)
                    level = data.get("risk_level", "Unknown")

                    if level == "High":
                        st.error(f"🔴 **HIGH RISK DETECTED** (Score: {score}/100)")
                    elif level == "Medium":
                        st.warning(f"🟡 **MEDIUM RISK / CAUTION** (Score: {score}/100)")
                    else:
                        st.success(f"🟢 **LOW RISK / APPEARS LEGIT** (Score: {score}/100)")

                    st.markdown("### ⚠️ Key Indicators")
                    for warning in data.get("warning_indicators", []):
                        st.write(f"- {warning}")

                    st.markdown("### 💡 Guidance")
                    st.info(data.get("recommendation", ""))

                except Exception as e:
                    st.error(f"Error: {e}")

# ---------------------------------------------------------
# TAB 2: LOGO VERIFICATION (NEW EXTRA FEATURE)
# ---------------------------------------------------------
with tab2:
    st.subheader("🖼️ Upload Logo or ID Badge to Verify Authenticity")
    st.write("Scammers often use fake, altered, or poorly cropped logos on fake offer letters.")
    
    uploaded_file = st.file_uploader("Upload Company Logo / Offer Letter Header", type=["png", "jpg", "jpeg"])
    company_name = st.text_input("Claimed Company Name (e.g., Google, Amazon, Microsoft)", placeholder="Google")

    if st.button("🔍 Check Logo Authenticity", type="primary"):
        if not api_key:
            st.error("Please provide a Gemini API Key.")
        elif not uploaded_file:
            st.warning("Please upload a logo image first.")
        else:
            with st.spinner("Analyzing image visual authenticity..."):
                try:
                    # Open uploaded image using PIL
                    img = Image.open(uploaded_file)
                    st.image(img, caption="Uploaded Image", width=250)

                    client = genai.Client(api_key=api_key)
                    logo_prompt = f"""
                    You are a brand visual verification expert inspecting a company logo/brand image for fraud detection.
                    The sender claims this image belongs to the company: "{company_name if company_name else 'Unknown Company'}".

                    Inspect the image for:
                    1. Brand matching (Does this look like the official logo of {company_name}?).
                    2. Visual artifacts (Is it blurry, stretched, pixelated, edited using basic tools, or missing signature brand elements?).
                    3. Misspellings or fake elements overlaid on the logo.

                    Return ONLY a JSON object:
                    {{
                        "is_authentic_looking": <true or false>,
                        "authenticity_score": <number between 0 and 100 where 100 is authentic and 0 is fake>,
                        "visual_flaws": ["<flaw 1>", "<flaw 2>"],
                        "verdict": "<detailed visual inspection summary>"
                    }}
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[img, logo_prompt],
                    )

                    cleaned = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(cleaned)

                    st.markdown("---")
                    st.subheader("Logo Inspection Report")

                    auth_score = data.get("authenticity_score", 0)
                    if auth_score >= 70:
                        st.success(f"🟢 **LIKELY AUTHENTIC LOGO** (Confidence: {auth_score}/100)")
                    elif auth_score >= 40:
                        st.warning(f"🟡 **SUSPICIOUS / LOW QUALITY LOGO** (Confidence: {auth_score}/100)")
                    else:
                        st.error(f"🔴 **LIKELY FAKE / ALTERED LOGO** (Confidence: {auth_score}/100)")

                    st.markdown("### 🔍 Visual Flaws Detected")
                    for flaw in data.get("visual_flaws", []):
                        st.write(f"- {flaw}")

                    st.markdown("### 📋 AI Verdict")
                    st.info(data.get("verdict", ""))

                except Exception as e:
                    st.error(f"Error analyzing image: {e}")
