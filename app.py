import json
import re
import streamlit as st
from google import genai
from PIL import Image

# Page setup
st.set_page_config(
    page_title="ScamCheck AI - CyberShield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# HIGH-ENERGY COLORFUL CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* App Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }

    /* Gradient Hero Banner */
    .hero-container {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        padding: 3px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px -10px rgba(168, 85, 247, 0.5);
    }
    .hero-content {
        background: #0f172a;
        padding: 30px;
        border-radius: 17px;
        text-align: center;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(168, 85, 247, 0.4);
    }

    /* Glowing Status Badges */
    .badge-danger {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid #ef4444;
        padding: 8px 18px;
        border-radius: 30px;
        font-weight: 700;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
        display: inline-block;
    }
    .badge-warning {
        background: rgba(245, 158, 11, 0.2);
        color: #fde047;
        border: 1px solid #f59e0b;
        padding: 8px 18px;
        border-radius: 30px;
        font-weight: 700;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
        display: inline-block;
    }
    .badge-success {
        background: rgba(34, 197, 94, 0.2);
        color: #86efac;
        border: 1px solid #22c55e;
        padding: 8px 18px;
        border-radius: 30px;
        font-weight: 700;
        box-shadow: 0 0 15px rgba(34, 197, 94, 0.4);
        display: inline-block;
    }

    /* Stylish Input Areas */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
    }
    .stTextArea textarea:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.5) !important;
    }

    /* Vibrant Gradient Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 50px !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LANGUAGE SELECTION — FIRST SCREEN
# ---------------------------------------------------------
LANGUAGES = {
    "English": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "Next-Generation Verification Platform for Internship & Job Offers",
        "select": "🌐 Select your language",
        "continue": "🚀 Continue",
    },
    "தமிழ்": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "இன்டர்ன்ஷிப் மற்றும் வேலை வாய்ப்புகளை சரிபார்க்கும் தளம்",
        "select": "🌐 உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்",
        "continue": "🚀 தொடரவும்",
    },
    "हिन्दी": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "इंटर्नशिप और नौकरी के प्रस्तावों की जाँच करने वाला प्लेटफ़ॉर्म",
        "select": "🌐 अपनी भाषा चुनें",
        "continue": "🚀 जारी रखें",
    },
    "മലയാളം": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "ഇന്റേൺഷിപ്പ്, ജോലി ഓഫറുകൾ എന്നിവ പരിശോധിക്കുന്ന പ്ലാറ്റ്ഫോം",
        "select": "🌐 നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക",
        "continue": "🚀 തുടരുക",
    },
    "ಕನ್ನಡ": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "ಇಂಟರ್ನ್‌ಶಿಪ್ ಮತ್ತು ಉದ್ಯೋಗ ಆಫರ್‌ಗಳನ್ನು ಪರಿಶೀಲಿಸುವ ವೇದಿಕೆ",
        "select": "🌐 ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "continue": "🚀 ಮುಂದುವರಿಸಿ",
    },
    "తెలుగు": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "ఇంటర్న్‌షిప్ మరియు ఉద్యోగ ఆఫర్లను ధృవీకరించే ప్లాట్‌ఫారమ్",
        "select": "🌐 మీ భాషను ఎంచుకోండి",
        "continue": "🚀 కొనసాగించండి",
    },
}

if "language_selected" not in st.session_state:
    st.session_state["language_selected"] = False

if not st.session_state["language_selected"]:
    st.markdown("""
    <style>
    .language-screen {
        max-width: 760px;
        margin: 80px auto;
        padding: 45px;
        text-align: center;
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(168,85,247,.35);
        border-radius: 24px;
        box-shadow: 0 15px 50px rgba(0,0,0,.4);
    }
    .language-logo {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(90deg,#38bdf8,#818cf8,#c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .language-sub {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 28px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="language-screen">
        <div class="language-logo">🛡️ ScamCheck AI</div>
        <div class="language-sub">
            Choose your preferred language before entering the application
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_language = st.selectbox(
        "🌐 Select your language / மொழியைத் தேர்ந்தெடுக்கவும்",
        list(LANGUAGES.keys()),
        index=0
    )

    if st.button(LANGUAGES[selected_language]["continue"], type="primary"):
        st.session_state["selected_language"] = selected_language
        st.session_state["language_selected"] = True
        st.rerun()

    st.stop()

selected_language = st.session_state.get("selected_language", "English")
UI = LANGUAGES[selected_language]

# Language can be changed later from the sidebar
with st.sidebar:
    st.markdown("### 🌐 Language")
    new_language = st.selectbox(
        "Change language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(selected_language)
    )
    if new_language != selected_language:
        st.session_state["selected_language"] = new_language
        st.rerun()

# HERO BANNER
st.markdown(f"""
<div class="hero-container">
    <div class="hero-content">
        <div class="hero-title">{UI["title"]}</div>
        <div class="hero-subtitle">{UI["subtitle"]}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# API Key Check
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    with st.sidebar:
        st.subheader("🔑 Security Key")
        api_key = st.text_input("Enter Gemini API Key", type="password")

# =========================================================
# EXTRA FEATURES & HEURISTICS
# =========================================================

if "scan_history" not in st.session_state:
    st.session_state["scan_history"] = []

def save_scan(text, score, level, indicators, recommendation):
    st.session_state["scan_history"].insert(0, {
        "text": text[:120],
        "score": int(score),
        "level": level,
        "indicators": len(indicators),
        "recommendation": recommendation
    })
    st.session_state["scan_history"] = st.session_state["scan_history"][:20]

# Advanced Local Heuristic Engine
def advanced_heuristic_check(text):
    t = text.lower()
    flags = []
    score = 0

    rules = [
        (r'\b(registration fee|security deposit|processing fee|laptop fee|pay for kit|joining fee|confirm your internship seat)\b',
         30, "💳 Payment Demand: Requests money before employment or onboarding."),
        (r'\b(telegram|whatsapp|signal)\b',
         15, "📱 Unverified Communication: Directing recruitment to personal messaging apps."),
        (r'\b(no interview|without interview|selected immediately|instant selection|you have been selected)\b',
         20, "⚠️ Immediate Selection: Claims candidate selection without proper screening."),
        (r'\b(guaranteed job|100% job|guaranteed income|easy money)\b',
         15, "🎯 Guaranteed Job Claim: Promises certainty or unusually easy income."),
        (r'\b(aadhaar|pan card|passport|bank details|otp|cvv|upi pin)\b',
         25, "🔐 Sensitive ID/Data Request: Asks for identity or financial credentials via unverified channels."),
        (r'\b(bit\.ly|tinyurl|t\.co|goo\.gl)\b',
         10, "🔗 Shortened URL: Link destination is obfuscated."),
        (r'\b(\d+\s*hours?|today|urgent|limited time|act now|immediately)\b',
         15, "⏰ Extreme Urgency: Creates artificial pressure to bypass verification."),
        (r'\b(crypto|bitcoin|usdt|investment required)\b',
         18, "🪙 Financial Scheme Indicator: Links employment with cryptocurrency or investment."),
        (r'@gmail\.com|@yahoo\.com|@hotmail\.com|@outlook\.com',
         15, "📧 Public Email Domain: Official recruitment uses generic webmail instead of a company domain.")
    ]

    for pattern, points, message in rules:
        if re.search(pattern, t):
            flags.append(message)
            score += points

    # Lower threshold to flag high stipends (e.g. ₹30,000+ per month for work-from-home internships)
    money_matches = re.findall(r'(?:₹|rs\.?|inr|\$)\s?([\d,]+)', t, flags=re.I)
    for amount in money_matches:
        try:
            value = int(amount.replace(",", ""))
            if value >= 30000:
                flags.append("💰 Salary Anomaly: Compensation is unusually inflated for entry-level work.")
                score += 15
                break
        except ValueError:
            pass

    return min(score, 100), flags

def extract_links_and_contacts(text):
    urls = re.findall(r'https?://[^\s<>"\']+', text)
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    phones = re.findall(r'(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)', text)
    return urls, emails, phones

def show_safety_checklist(score):
    st.markdown("### 🛡️ Recommended Safety Actions")
    actions = [
        "Do not pay registration, security, training, equipment, or processing fees.",
        "Verify the vacancy on the company's official careers website.",
        "Do not share OTP, UPI PIN, CVV, passwords, or banking credentials.",
        "Check the sender's email domain carefully for impersonation.",
        "Avoid opening unknown shortened links or attachments.",
        "Contact the company using a phone number or email obtained independently."
    ]
    for action in actions:
        st.markdown(f"- {action}")

# Extra Dashboard Tabs
tab_dashboard, tab_history = st.tabs(["📈 Security Dashboard", "🧾 Scan History"])

with tab_dashboard:
    st.markdown("""
    <div class="glass-card">
        <h2>🛡️ CyberShield Security Center</h2>
        <p>Use this dashboard to inspect suspicious recruitment messages,
        URLs, contact information, and previous scan results.</p>
    </div>
    """, unsafe_allow_html=True)

    h1, h2, h3 = st.columns(3)
    history = st.session_state.get("scan_history", [])

    with h1:
        st.metric("Total Scans", len(history))
    with h2:
        high_count = sum(1 for x in history if x["level"] == "High")
        st.metric("High Risk Scans", high_count)
    with h3:
        avg_score = (
            round(sum(x["score"] for x in history) / len(history), 1)
            if history else 0
        )
        st.metric("Average Risk", avg_score)

    st.markdown("### 🔎 Quick Message Inspector")
    quick_text = st.text_area(
        "Paste a suspicious message for instant local checks",
        height=150,
        key="quick_inspector"
    )

    if st.button("⚡ Run Quick Security Check"):
        if not quick_text.strip():
            st.warning("Enter a message first.")
        else:
            extra_score, extra_flags = advanced_heuristic_check(quick_text)
            urls, emails, phones = extract_links_and_contacts(quick_text)

            st.metric("Local Risk Score", f"{extra_score}/100")

            if extra_score >= 60:
                st.error("🔴 High-risk indicators detected.")
            elif extra_score >= 30:
                st.warning("🟡 Suspicious indicators detected.")
            else:
                st.success("🟢 No major local red flags detected.")

            if extra_flags:
                st.markdown("#### 🚩 Red Flags")
                for flag in extra_flags:
                    st.write(flag)

            with st.expander("🌐 Extracted Links / Contact Details"):
                st.write("**URLs:**", urls if urls else "None found")
                st.write("**Emails:**", emails if emails else "None found")
                st.write("**Phone numbers:**", phones if phones else "None found")

            show_safety_checklist(extra_score)

with tab_history:
    st.markdown("### 🧾 Previous Scan Results")

    if not history:
        st.info("No scans recorded in this session yet.")
    else:
        for i, item in enumerate(history):
            with st.expander(
                f"{'🔴' if item['level']=='High' else '🟡' if item['level']=='Medium' else '🟢'} "
                f"{item['level']} Risk — Score {item['score']}/100"
            ):
                st.write("**Message:**", item["text"])
                st.write("**Indicators:**", item["indicators"])
                st.write("**Recommendation:**", item["recommendation"])

    if st.button("🗑️ Clear Scan History"):
        st.session_state["scan_history"] = []
        st.rerun()

if st.session_state.get("scan_history"):
    import csv
    import io

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["text", "score", "level", "indicators", "recommendation"]
    )
    writer.writeheader()
    writer.writerows(st.session_state["scan_history"])

    st.sidebar.download_button(
        "⬇️ Download Scan History CSV",
        data=output.getvalue(),
        file_name="scamcheck_scan_history.csv",
        mime="text/csv"
    )

# Primary App Tabs
tab_offer, tab_brand = st.tabs(["🚀 Verify Text / Offer", "🔍 Inspect Logo Authenticity"])

# ---------------------------------------------------------
# TAB 1: OFFER ANALYZER (WITH FALLBACK FOR 429 ERRORS)
# ---------------------------------------------------------
with tab_offer:
    col_input, col_presets = st.columns([2, 1])

    with col_presets:
        st.markdown('<div class="glass-card"><b>⚡ Quick Test Presets</b><br><br>', unsafe_allow_html=True)
        if st.button("🚨 Load Fake HR Scam"):
            st.session_state["text_input"] = "Congratulations! You are selected for HR Assistant at Amazon. Salary 50,000 INR/month. Work 2 hours daily from home. Pay 1,500 INR registration fee to process laptop kit. Contact HR on WhatsApp: 9876543210."
        if st.button("🟡 Load Telegram Offer"):
            st.session_state["text_input"] = "Urgent Hiring: Data Entry Operator needed. Pay: $200/day. No interview needed. Contact manager directly on Telegram @Jobs_HR_Fast."
        if st.button("✅ Load Legit Opportunity"):
            st.session_state["text_input"] = "We are hiring a Software Engineer Intern at TechCorp. Requirements: Python, React. Apply through our official portal: https://techcorp.com/careers/intern-2026."
        st.markdown('</div>', unsafe_allow_html=True)

    with col_input:
        user_text = st.text_area(
            "Paste Offer / Email / Message Here", 
            value=st.session_state.get("text_input", ""), 
            height=180, 
            placeholder="Paste raw email header, WhatsApp message, or job text..."
        )
        analyze_btn = st.button("🔥 Scan Opportunity", type="primary")

    if analyze_btn:
        if not api_key:
            st.error("Please configure your Gemini API Key in the sidebar or Secrets.")
        elif not user_text.strip():
            st.warning("Please paste offer details first.")
        else:
            with st.spinner("Analyzing opportunity..."):
                local_score, local_flags = advanced_heuristic_check(user_text)
                
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    Analyze this opportunity for scam risk:
                    "{user_text}"

                    Return ONLY a JSON object:
                    {{
                        "risk_score": <number 0 to 100>,
                        "risk_level": "<Low | Medium | High>",
                        "warning_indicators": ["<indicator 1>", "<indicator 2>"],
                        "recommendation": "<advice>"
                    }}
                    """
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt,
                    )
                    cleaned = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(cleaned)

                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        st.warning("⚠️ Gemini API quota limit reached. Switched to local rule-based analysis engine.")
                        level = "High" if local_score >= 60 else "Medium" if local_score >= 30 else "Low"
                        data = {
                            "risk_score": local_score,
                            "risk_level": level,
                            "warning_indicators": local_flags,
                            "recommendation": "Analysis compiled by offline engine due to API quota limits. Verify company credentials manually."
                        }
                    else:
                        st.error(f"Analysis error: {e}")
                        st.stop()

                score = data.get("risk_score", 0)
                level = data.get("risk_level", "Unknown")

                st.markdown("---")
                st.markdown("### 📊 Threat Intelligence Report")

                m1, m2 = st.columns([1, 2])
                
                with m1:
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <span style="font-size: 0.9rem; color: #94a3b8;">RISK SCORE</span>
                        <h1 style="font-size: 3.5rem; margin: 0; color: #c084fc;">{score}</h1>
                        <span style="font-size: 0.8rem; color: #64748b;">out of 100</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(score / 100)

                with m2:
                    st.markdown("<div class='glass-card'><b>Threat Level Status</b><br><br>", unsafe_allow_html=True)
                    if level == "High":
                        st.markdown('<span class="badge-danger">🔴 HIGH RISK THREAT DETECTED</span>', unsafe_allow_html=True)
                    elif level == "Medium":
                        st.markdown('<span class="badge-warning">🟡 MEDIUM RISK / EXTREME CAUTION</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="badge-success">🟢 LOW RISK / VERIFIED PROFILE</span>', unsafe_allow_html=True)
                    
                    st.markdown(f"<br><br><b>Verdict:</b> {data.get('recommendation', '')}", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='glass-card'><b>🚩 Identified Risk Indicators</b><br><br>", unsafe_allow_html=True)
                all_indicators = list(set(local_flags + data.get("warning_indicators", [])))
                for ind in all_indicators:
                    st.markdown(f"- {ind}")
                st.markdown("</div>", unsafe_allow_html=True)

                save_scan(user_text, score, level, all_indicators, data.get('recommendation', ''))

# ---------------------------------------------------------
# TAB 2: BRAND LOGO INSPECTION
# ---------------------------------------------------------
with tab_brand:
    col_upload, col_preview = st.columns([1, 1])

    with col_upload:
        uploaded_file = st.file_uploader("Upload Brand Logo or Offer Header", type=["png", "jpg", "jpeg"])
        company_name = st.text_input("Claimed Company Name", placeholder="e.g. Google, Amazon, Microsoft")
        verify_logo_btn = st.button("👁️ Verify Brand Authenticity", type="primary")

    if verify_logo_btn:
        if not api_key:
            st.error("Missing API Key.")
        elif not uploaded_file:
            st.warning("Please upload a logo image.")
        else:
            with st.spinner("Analyzing image..."):
                try:
                    img = Image.open(uploaded_file)
                    with col_preview:
                        st.image(img, caption="Uploaded File Preview", width=220)

                    client = genai.Client(api_key=api_key)
                    logo_prompt = f"""
                    Inspect this image claiming to be the logo of "{company_name}".
                    Look for pixelation, edited text, stretched artifacts, or missing brand features.

                    Return ONLY a JSON object:
                    {{
                        "authenticity_score": <number 0 to 100>,
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

                    auth_score = data.get("authenticity_score", 0)

                    st.markdown("---")
                    st.markdown(f"""
                    <div class="glass-card">
                        <h3>Visual Analysis Report</h3>
                        <h2 style="color: #38bdf8;">Authenticity Index: {auth_score}/100</h2>
                    </div>
                    """, unsafe_allow_html=True)

                    if auth_score >= 70:
                        st.markdown('<span class="badge-success">🟢 AUTHENTIC BRAND IMAGE</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="badge-danger">🔴 HIGH CHANCE OF FRAUDULENT / ALTERED LOGO</span>', unsafe_allow_html=True)

                    st.markdown("<br><div class='glass-card'><b>🔍 Image Flaws Detected</b><br>", unsafe_allow_html=True)
                    for flaw in data.get("visual_flaws", []):
                        st.markdown(f"- {flaw}")
                    st.write(data.get("summary", ""))
                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        st.error("⚠️ API quota exceeded. Logo inspection requires active Gemini vision access.")
                    else:
                        st.error(f"Image analysis error: {e}")
