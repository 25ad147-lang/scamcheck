import os
import json
import streamlit as st
from google import genai

# Page configuration
st.set_page_config(page_title="ScamCheck", page_icon="🛡️")

st.title("🛡️ ScamCheck: Opportunity Verifier")
st.write("Paste suspicious job, internship, or offer details below to generate a instant risk evaluation.")

# Sample buttons for quick live demos
st.markdown("### Quick Demo Presets")
col1, col2 = st.columns(2)

sample_text = ""
if col1.button("🚨 Load Fake WhatsApp Job Scam"):
    sample_text = "Congratulations! You are selected for HR Assistant at Amazon. Salary 50,000 INR/month. Work 2 hours daily from home. Pay 1,500 INR registration fee to process laptop kit. Contact HR on WhatsApp: 9876543210."
if col2.button("✅ Load Legitimate Internship"):
    sample_text = "We are hiring a Software Engineer Intern at TechCorp. Requirements: Python, React. Apply through our official portal: https://techcorp.com/careers/intern-2026. Official interviews will be conducted via Google Meet."

# Input Text Area
user_input = st.text_area("Offer Text / Email / Message", value=sample_text, height=180, placeholder="Paste email, WhatsApp message, or job post here...")

# Updated Line 28:
api_key = st.secrets.get("GEMINI_API_KEY", "")

if st.button("🔍 Analyze Opportunity", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key to proceed.")
    elif not user_input.strip():
        st.warning("Please paste some text to analyze.")
    else:
        with st.spinner("Analyzing opportunity for fraud indicators..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                You are a fraud detection assistant analyzing job and internship offers for students.
                Analyze the following text for scam risks (e.g., registration fees, WhatsApp/Telegram-only contact, unrealistic salary, unverified links).
                
                Text to analyze:
                "{user_input}"
                
                Return ONLY a JSON object with this exact structure:
                {{
                    "risk_score": <number between 0 and 100>,
                    "risk_level": "<Low | Medium | High>",
                    "warning_indicators": ["<warning 1>", "<warning 2>"],
                    "recommendation": "<brief advice for student>"
                }}
                """

                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                )
                
                # Parse JSON output
                cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(cleaned_response)

                st.markdown("---")
                st.subheader("Analysis Results")

                # Visual Risk Indicator
                score = data.get("risk_score", 0)
                level = data.get("risk_level", "Unknown")

                if level == "High":
                    st.error(f"🔴 **HIGH RISK DETECTED** (Score: {score}/100)")
                elif level == "Medium":
                    st.warning(f"🟡 **MEDIUM RISK / CAUTION** (Score: {score}/100)")
                else:
                    st.success(f"🟢 **LOW RISK / APPEARS LEGIT** (Score: {score}/100)")

                # Warning Indicators
                st.markdown("### ⚠️ Key Indicators")
                for warning in data.get("warning_indicators", []):
                    st.write(f"- {warning}")

                # Recommendation
                st.markdown("### 💡 Guidance")
                st.info(data.get("recommendation", "Verify company details on official channels before responding."))

            except Exception as e:
                st.error(f"An error occurred: {e}")
