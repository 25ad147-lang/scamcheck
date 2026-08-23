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

    /* Text Area Styling */
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

    /* Button Styling */
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
# COMPREHENSIVE TRANSLATIONS FOR ALL 6 LANGUAGES
# ---------------------------------------------------------
LANGUAGES = {
    "English": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "Next-Generation Verification Platform for Internship & Job Offers",
        "select": "🌐 Select your language",
        "continue": "🚀 Continue",
        "sec_dashboard": "📈 Security Dashboard",
        "scan_history_tab": "🧾 Scan History",
        "cyber_shield_title": "🛡️ CyberShield Security Center",
        "cyber_shield_desc": "Use this dashboard to inspect suspicious recruitment messages, URLs, contact information, and previous scan results.",
        "total_scans": "Total Scans",
        "high_risk_scans": "High Risk Scans",
        "avg_risk": "Average Risk",
        "quick_inspector_title": "🔎 Quick Message Inspector",
        "quick_inspector_label": "Paste a suspicious message for instant local checks",
        "run_quick_check": "⚡ Run Quick Security Check",
        "local_risk_score": "Local Risk Score",
        "no_red_flags": "🟢 No major local red flags detected.",
        "red_flags": "🚩 Red Flags",
        "extracted_details": "🌐 Extracted Links / Contact Details",
        "urls": "URLs:",
        "emails": "Emails:",
        "phones": "Phone numbers:",
        "safety_actions_title": "🛡️ Recommended Safety Actions",
        "safety_actions": [
            "Do not pay registration, security, training, equipment, or processing fees.",
            "Verify the vacancy on the company's official careers website.",
            "Do not share OTP, UPI PIN, CVV, passwords, or banking credentials.",
            "Check the sender's email domain carefully for impersonation.",
            "Avoid opening unknown shortened links or attachments.",
            "Contact the company using a phone number or email obtained independently."
        ],
        "prev_scan_title": "🧾 Previous Scan Results",
        "no_scans": "No scans recorded in this session yet.",
        "clear_history": "🗑️ Clear Scan History",
        "verify_tab": "🚀 Verify Text / Offer",
        "logo_tab": "🔍 Inspect Logo Authenticity",
        "presets_title": "⚡ Quick Test Presets",
        "preset_fake": "🚨 Load Fake HR Scam",
        "preset_telegram": "🟡 Load Telegram Offer",
        "preset_legit": "✅ Load Legit Opportunity",
        "text_area_label": "Paste Offer / Email / Message Here",
        "scan_btn": "🔥 Scan Opportunity",
        "threat_report": "📊 Threat Intelligence Report",
        "risk_score_card": "RISK SCORE",
        "threat_status": "Threat Level Status",
        "high_risk_badge": "🔴 HIGH RISK THREAT DETECTED",
        "med_risk_badge": "🟡 MEDIUM RISK / EXTREME CAUTION",
        "low_risk_badge": "🟢 LOW RISK / VERIFIED PROFILE",
        "verdict": "Verdict:",
        "identified_indicators": "🚩 Identified Risk Indicators",
        "logo_upload_label": "Upload Brand Logo or Offer Header",
        "company_name_label": "Claimed Company Name",
        "verify_logo_btn": "👁️ Verify Brand Authenticity",
        "visual_report": "Visual Analysis Report",
        "auth_index": "Authenticity Index:",
        "authentic_badge": "🟢 AUTHENTIC BRAND IMAGE",
        "fake_badge": "🔴 HIGH CHANCE OF FRAUDULENT / ALTERED LOGO",
        "flaws_title": "🔍 Image Flaws Detected"
    },
    "தமிழ்": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "இன்டர்ன்ஷிப் மற்றும் வேலை வாய்ப்புகளை சரிபார்க்கும் தளம்",
        "select": "🌐 உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்",
        "continue": "🚀 தொடரவும்",
        "sec_dashboard": "📈 பாதுகாப்பு டாஷ்போர்டு",
        "scan_history_tab": "🧾 ஸ்கேன் வரலாறு",
        "cyber_shield_title": "🛡️ சைபர்ஷீல்ட் பாதுகாப்பு மையம்",
        "cyber_shield_desc": "சந்தேகத்திற்குரிய குறுஞ்செய்திகள், உரலிகள் மற்றும் தொடர்புகளை சரிபார்க்க இந்த டாஷ்போர்டைப் பயன்படுத்தவும்.",
        "total_scans": "மொத்த ஸ்கேன்கள்",
        "high_risk_scans": "அதிக ஆபத்துள்ள ஸ்கேன்கள்",
        "avg_risk": "சராசரி ஆபத்து",
        "quick_inspector_title": "🔎 உடனடி செய்தி பரிசோதனையாளர்",
        "quick_inspector_label": "உடனடி உள்ளூர் சோதனைகளுக்கு சந்தேகத்திற்கிடமான செய்தியை ஒட்டவும்",
        "run_quick_check": "⚡ உடனடி பாதுகாப்பு சோதனை செய்க",
        "local_risk_score": "உள்ளூர் ஆபத்து மதிப்பெண்",
        "no_red_flags": "🟢 எந்த பெரிய ஆபத்து எச்சரிக்கையும் கண்டறியப்படவில்லை.",
        "red_flags": "🚩 ஆபத்து எச்சரிக்கைகள்",
        "extracted_details": "🌐 பிரித்தெடுக்கப்பட்ட இணைப்புகள் / தொடர்பு விவரங்கள்",
        "urls": "இணைப்புகள் (URLs):",
        "emails": "மின்னஞ்சல்கள்:",
        "phones": "தொலைபேசி எண்கள்:",
        "safety_actions_title": "🛡️ பரிந்துரைக்கப்பட்ட பாதுகாப்பு நடவடிக்கைகள்",
        "safety_actions": [
            "பதிவுக் கட்டணம், முன்பணம், பயிற்சி அல்லது செயலாக்கக் கட்டணங்களைச் செலுத்த வேண்டாம்.",
            "நிறுவனத்தின் அதிகாரப்பூர்வ இணையதளத்தில் காலியிடத்தை சரிபார்க்கவும்.",
            "OTP, UPI PIN, CVV அல்லது வங்கி விவரங்களைப் பகிர வேண்டாம்.",
            "அனுப்புநரின் மின்னஞ்சல் முகவரியை கவனமாகச் சரிபார்க்கவும்.",
            "தெரியாத குறுகிய இணைப்புகள் அல்லது இணைப்புகளைத் திறப்பதைத் தவிர்க்கவும்.",
            "நிறுவனத்தை நேரடி அதிகாரப்பூர்வ எண் மூலம் தொடர்பு கொள்ளவும்."
        ],
        "prev_scan_title": "🧾 முந்தைய ஸ்கேன் முடிவுகள்",
        "no_scans": "இந்த அமர்வில் இன்னும் ஸ்கேன்கள் பதிவு செய்யப்படவில்லை.",
        "clear_history": "🗑️ வரலாற்றை அழி",
        "verify_tab": "🚀 உரையைச் சரிபார்",
        "logo_tab": "🔍 சின்னத்தின் நம்பிக்கைத் தன்மையைச் சரிபார்",
        "presets_title": "⚡ மாதிரி சோதனைகள்",
        "preset_fake": "🚨 போலி HR மோசடி",
        "preset_telegram": "🟡 டெலிகிராம் சலுகை",
        "preset_legit": "✅ உண்மையான வேலை",
        "text_area_label": "சலுகை / மின்னஞ்சல் / செய்தியை இங்கே ஒட்டவும்",
        "scan_btn": "🔥 வாய்ப்பை ஸ்கேன் செய்க",
        "threat_report": "📊 அச்சுறுத்தல் பகுப்பாய்வு அறிக்கை",
        "risk_score_card": "ஆபத்து மதிப்பெண்",
        "threat_status": "அச்சுறுத்தல் நிலை",
        "high_risk_badge": "🔴 அதிக ஆபத்து கண்டறியப்பட்டது",
        "med_risk_badge": "🟡 நடுத்தர ஆபத்து / எச்சரிக்கை தேவை",
        "low_risk_badge": "🟢 குறைந்த ஆபத்து / சரிபார்க்கப்பட்டது",
        "verdict": "முடிவு:",
        "identified_indicators": "🚩 கண்டறியப்பட்ட ஆபத்து குறிகாட்டிகள்",
        "logo_upload_label": "நிறுவனத்தின் சின்னத்தைப் பதிவேற்றவும்",
        "company_name_label": "நிறுவனத்தின் பெயர்",
        "verify_logo_btn": "👁️ சின்னத்தைச் சரிபார்",
        "visual_report": "காட்சி பகுப்பாய்வு அறிக்கை",
        "auth_index": "நம்பகத்தன்மை குறியீடு:",
        "authentic_badge": "🟢 உண்மையான நிறுவனத்தின் படம்",
        "fake_badge": "🔴 போலி / மாற்றியமைக்கப்பட்ட படம்",
        "flaws_title": "🔍 கண்டறியப்பட்ட காட்சி தவறுகள்"
    },
    "हिन्दी": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "इंटर्नशिप और नौकरी के प्रस्तावों की जाँच करने वाला प्लेटफ़ॉर्म",
        "select": "🌐 अपनी भाषा चुनें",
        "continue": "🚀 जारी रखें",
        "sec_dashboard": "📈 सुरक्षा डैशबोर्ड",
        "scan_history_tab": "🧾 स्कैन इतिहास",
        "cyber_shield_title": "🛡️ साइबर-शील्ड सुरक्षा केंद्र",
        "cyber_shield_desc": "संदिग्ध संदेशों, लिंक और संपर्क जानकारी की जांच के लिए इस डैशबोर्ड का उपयोग करें।",
        "total_scans": "कुल स्कैन",
        "high_risk_scans": "उच्च जोखिम वाले स्कैन",
        "avg_risk": "औसत जोखिम",
        "quick_inspector_title": "🔎 त्वरित संदेश निरीक्षक",
        "quick_inspector_label": "त्वरित जांच के लिए एक संदिग्ध संदेश पेस्ट करें",
        "run_quick_check": "⚡ त्वरित सुरक्षा जांच चलाएं",
        "local_risk_score": "स्थानीय जोखिम स्कोर",
        "no_red_flags": "🟢 कोई प्रमुख जोखिम चेतावनी नहीं मिली।",
        "red_flags": "🚩 खतरे के संकेत",
        "extracted_details": "🌐 निकाले गए लिंक / संपर्क विवरण",
        "urls": "लिंक (URLs):",
        "emails": "ईमेल:",
        "phones": "फोन नंबर:",
        "safety_actions_title": "🛡️ अनुशंसित सुरक्षा कदम",
        "safety_actions": [
            "पंजीकरण, सुरक्षा या प्रशिक्षण शुल्क का भुगतान न करें।",
            "कंपनी की आधिकारिक वेबसाइट पर रिक्ति की पुष्टि करें।",
            "OTP, UPI PIN, या बैंक विवरण साझा न करें।",
            "प्रेषक के ईमेल डोमेन की ध्यान से जांच करें।",
            "अज्ञात छोटे लिंक या संलग्नक खोलने से बचें।",
            "कंपनी से स्वतंत्र रूप से प्राप्त संपर्क नंबर पर संपर्क करें।"
        ],
        "prev_scan_title": "🧾 पिछले स्कैन परिणाम",
        "no_scans": "इस सत्र में अभी तक कोई स्कैन दर्ज नहीं किया गया है।",
        "clear_history": "🗑️ इतिहास साफ़ करें",
        "verify_tab": "🚀 ऑफर संदेश की जांच करें",
        "logo_tab": "🔍 लोगो प्रमाणिकता की जांच करें",
        "presets_title": "⚡ त्वरित परीक्षण नमूने",
        "preset_fake": "🚨 नकली एचआर फ्रॉड",
        "preset_telegram": "🟡 टेलीग्राम ऑफर",
        "preset_legit": "✅ वास्तविक नौकरी",
        "text_area_label": "प्रस्ताव / ईमेल / संदेश यहां पेस्ट करें",
        "scan_btn": "🔥 अवसर को स्कैन करें",
        "threat_report": "📊 खतरा विश्लेषण रिपोर्ट",
        "risk_score_card": "जोखिम स्कोर",
        "threat_status": "खतरे का स्तर",
        "high_risk_badge": "🔴 उच्च जोखिम खतरा पाया गया",
        "med_risk_badge": "🟡 मध्यम जोखिम / सावधानी की आवश्यकता",
        "low_risk_badge": "🟢 कम जोखिम / सत्यापित प्रोफ़ाइल",
        "verdict": "निष्कर्ष:",
        "identified_indicators": "🚩 पहचाने गए जोखिम संकेतक",
        "logo_upload_label": "कंपनी का लोगो अपलोड करें",
        "company_name_label": "दावा की गई कंपनी का नाम",
        "verify_logo_btn": "👁️ लोगो की जांच करें",
        "visual_report": "विजुअल विश्लेषण रिपोर्ट",
        "auth_index": "प्रमाणिकता सूचकांक:",
        "authentic_badge": "🟢 प्रामाणिक ब्रांड छवि",
        "fake_badge": "🔴 नकली या परिवर्तित छवि की उच्च संभावना",
        "flaws_title": "🔍 पहचानी गई कमियां"
    },
    "മലയാളം": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "ഇന്റേൺഷിപ്പ്, ജോലി ഓഫറുകൾ എന്നിവ പരിശോധിക്കുന്ന പ്ലാറ്റ്ഫോം",
        "select": "🌐 നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക",
        "continue": "🚀 തുടരുക",
        "sec_dashboard": "📈 സുരക്ഷാ ഡാഷ്‌ബോർഡ്",
        "scan_history_tab": "🧾 സ്‌കാൻ ചരിത്രം",
        "cyber_shield_title": "🛡️ സൈബർ ഷീൽഡ് സുരക്ഷാ കേന്ദ്രം",
        "cyber_shield_desc": "സംശയാസ്പദമായ സന്ദേശങ്ങൾ, ലിങ്കുകൾ, വിവരങ്ങൾ എന്നിവ പരിശോധിക്കാൻ ഈ ഡാഷ്‌ബോർഡ് ഉപയോഗിക്കുക.",
        "total_scans": "ആകെ സ്‌കാനുകൾ",
        "high_risk_scans": "ഉയർന്ന അപകടസാധ്യതയുള്ള സ്‌കാനുകൾ",
        "avg_risk": "ശരാശരി അപകടസാധ്യത",
        "quick_inspector_title": "🔎 സന്ദേശ പരിശോധന",
        "quick_inspector_label": "ഉടൻ പരിശോധിക്കാൻ സംശയാസ്പദമായ സന്ദേശം ഇവിടെ നൽകുക",
        "run_quick_check": "⚡ സുരക്ഷാ പരിശോധന നടത്തുക",
        "local_risk_score": "അപകടസാധ്യത സ്കോർ",
        "no_red_flags": "🟢 അപകട സൂചനകളൊന്നും കണ്ടെത്തിയില്ല.",
        "red_flags": "🚩 അപകട മുന്നറിയിപ്പുകൾ",
        "extracted_details": "🌐 കണ്ടെത്തിയ ലിങ്കുകൾ / വിവരങ്ങൾ",
        "urls": "ലിങ്കുകൾ:",
        "emails": "ഇമെയിലുകൾ:",
        "phones": "ഫോൺ നമ്പറുകൾ:",
        "safety_actions_title": "🛡️ സുരക്ഷാ നിർദ്ദേശങ്ങൾ",
        "safety_actions": [
            "രജിസ്ട്രേഷൻ, പരിശീലനം എന്നിവയ്ക്കായി പണം നൽകരുത്.",
            "ഔദ്യോഗിക വെബ്സൈറ്റിൽ ജോലി വിവരങ്ങൾ ഉറപ്പാക്കുക.",
            "OTP, UPI PIN, ബാങ്ക് വിവരങ്ങൾ കൈമാറരുത്.",
            "ഇമെയിൽ വിലാസങ്ങൾ ശ്രദ്ധയോടെ പരിശോധിക്കുക."
        ],
        "prev_scan_title": "🧾 മുൻ സ്‌കാൻ ഫലങ്ങൾ",
        "no_scans": "ചരിത്രമൊന്നും ലഭ്യമല്ല.",
        "clear_history": "🗑️ ചരിത്രം മായ്ക്കുക",
        "verify_tab": "🚀 സന്ദേശം പരിശോധിക്കുക",
        "logo_tab": "🔍 ലോഗോ പരിശോധിക്കുക",
        "presets_title": "⚡ മാതൃകാ സന്ദേശങ്ങൾ",
        "preset_fake": "🚨 വ്യാജ HR സന്ദേശം",
        "preset_telegram": "🟡 ടെലിഗ്രാം ഓഫർ",
        "preset_legit": "✅ യഥാർത്ഥ ജോലി ഓഫർ",
        "text_area_label": "സന്ദേശം ഇവിടെ पेस्ट ചെയ്യുക",
        "scan_btn": "🔥 സ്‌കാൻ ചെയ്യുക",
        "threat_report": "📊 സുരക്ഷാ റിപ്പോർട്ട്",
        "risk_score_card": "അപകട സ്കോർ",
        "threat_status": "അപകട നില",
        "high_risk_badge": "🔴 വലിയ അപകടസാധ്യതയുള്ള സന്ദേശം",
        "med_risk_badge": "🟡 ശ്രദ്ധിക്കുക / ജാഗ്രത പാലിക്കുക",
        "low_risk_badge": "🟢 സുരക്ഷിതമായ സന്ദേശം",
        "verdict": "തീരുമാനം:",
        "identified_indicators": "🚩 കണ്ടെത്തിയ ലക്ഷണങ്ങൾ",
        "logo_upload_label": "ലോഗോ അപ്‌ലോഡ് ചെയ്യുക",
        "company_name_label": "കമ്പനിയുടെ പേര്",
        "verify_logo_btn": "👁️ ലോഗോ പരിശോധിക്കുക",
        "visual_report": "ചിത്ര പരിശോധനാ റിപ്പോർട്ട്",
        "auth_index": "വിശ്വാസ്യത:",
        "authentic_badge": "🟢 വ്യാജമല്ല",
        "fake_badge": "🔴 വ്യാജ ചിത്രമാകാൻ സാധ്യതയുണ്ട്",
        "flaws_title": "🔍 ചിത്രത്തിലെ പ്രശ്നങ്ങൾ"
    },
    "ಕನ್ನಡ": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "ಇಂಟರ್ನ್‌ಶಿಪ್ ಮತ್ತು ಉದ್ಯೋಗ ಆಫರ್‌ಗಳನ್ನು ಪರಿಶೀಲಿಸುವ ವೇದಿಕೆ",
        "select": "🌐 ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "continue": "🚀 ಮುಂದುವರಿಸಿ",
        "sec_dashboard": "📈 ಭದ್ರತಾ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "scan_history_tab": "🧾 ಸ್ಕ್ಯಾನ್ ಇತಿಹಾಸ",
        "cyber_shield_title": "🛡️ ಸೈಬರ್ ಶೀಲ್ಡ್ ಭದ್ರತಾ ಕೇಂದ್ರ",
        "cyber_shield_desc": "ಸಂದೇಹಾಸ್ಪದ ಸಂದೇಶಗಳು, ಲಿಂಕ್‌ಗಳು ಮತ್ತು ಸಂಪರ್ಕ ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಲು ಈ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಬಳಸಿ.",
        "total_scans": "ಒಟ್ಟು ಸ್ಕ್ಯಾನ್‌ಗಳು",
        "high_risk_scans": "ಹೆಚ್ಚಿನ ಅಪಾಯದ ಸ್ಕ್ಯಾನ್‌ಗಳು",
        "avg_risk": "ಸರಾಸರಿ ಅಪಾಯ",
        "quick_inspector_title": "🔎 ತ್ವರಿತ ಸಂದೇಶ ತಪಾಸಣೆ",
        "quick_inspector_label": "ತಕ್ಷಣ ಪರಿಶೀಲಿಸಲು ಸಂದೇಹಾಸ್ಪದ ಸಂದೇಶವನ್ನು ಪೇಸ್ಟ್ ಮಾಡಿ",
        "run_quick_check": "⚡ ಭದ್ರತಾ ತಪಾಸಣೆ ನಡೆಸಿ",
        "local_risk_score": "ಅಪಾಯದ ಸ್ಕೋರ್",
        "no_red_flags": "🟢 ಯಾವುದೇ ದೊಡ್ಡ ಅಪಾಯದ ಸೂಚನೆ ಕಂಡುಬಂದಿಲ್ಲ.",
        "red_flags": "🚩 ಅಪಾಯದ ಸೂಚನೆಗಳು",
        "extracted_details": "🌐 ಲಿಂಕ್‌ಗಳು ಮತ್ತು ಸಂಪರ್ಕ ವಿವರಗಳು",
        "urls": "ಲಿಂಕ್‌ಗಳು:",
        "emails": "ಇಮೇಲ್‌ಗಳು:",
        "phones": "ಫೋನ್ ಸಂಖ್ಯೆಗಳು:",
        "safety_actions_title": "🛡️ ಶಿಫಾರಸು ಮಾಡಲಾದ ಭದ್ರತಾ ಕ್ರಮಗಳು",
        "safety_actions": [
            "ನೋಂದಣಿ ಅಥವಾ ತರಬೇತಿ ಶುಲ್ಕವನ್ನು ಪಾವತಿಸಬೇಡಿ.",
            "ಅಧಿಕೃತ ವೆಬ್‌ಸೈಟ್‌ನಲ್ಲಿ ಕೆಲಸದ ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
            "OTP, UPI PIN ಅಥವಾ ಬ್ಯಾಂಕ್ ವಿವರಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಬೇಡಿ."
        ],
        "prev_scan_title": "🧾 ಹಿಂದಿನ ಸ್ಕ್ಯಾನ್ ಫಲಿತಾಂಶಗಳು",
        "no_scans": "ಯಾವುದೇ ಇತಿಹಾಸ ಲಭ್ಯವಿಲ್ಲ.",
        "clear_history": "🗑️ ಇತಿಹಾಸವನ್ನು ಅಳಿಸಿ",
        "verify_tab": "🚀 ಸಂದೇಶ ಪರಿಶೀಲಿಸಿ",
        "logo_tab": "🔍 ಲೋಗೋ ತಪಾಸಣೆ",
        "presets_title": "⚡ ಮಾದರಿ ಪರೀಕ್ಷೆಗಳು",
        "preset_fake": "🚨 ನಕಲಿ HR ಸಂದೇಶ",
        "preset_telegram": "🟡 ಟೆಲಿಗ್ರಾಂ ಆಫರ್",
        "preset_legit": "✅ ನೈಜ ಉದ್ಯೋಗ ಆಫರ್",
        "text_area_label": "ಸಂದೇಶವನ್ನು ಇಲ್ಲಿ ಪೇಸ್ಟ್ ಮಾಡಿ",
        "scan_btn": "🔥 ಸ್ಕ್ಯಾನ್ ಮಾಡಿ",
        "threat_report": "📊 ಅಪಾಯದ ವರದಿ",
        "risk_score_card": "ಅಪಾಯದ ಸ್ಕೋರ್",
        "threat_status": "ಅಪಾಯದ ಮಟ್ಟ",
        "high_risk_badge": "🔴 ಹೆಚ್ಚಿನ ಅಪಾಯ ಪತ್ತೆಯಾಗಿದೆ",
        "med_risk_badge": "🟡 ಮಧ್ಯಮ ಅಪಾಯ / ಎಚ್ಚರಿಕೆ ವಹಿಸಿ",
        "low_risk_badge": "🟢 ಸುರಕ್ಷಿತ ಸಂದೇಶ",
        "verdict": "ತೀರ್ಪು:",
        "identified_indicators": "🚩 ಪತ್ತೆಯಾದ ಅಪಾಯದ ಸೂಚಕಗಳು",
        "logo_upload_label": "ಲೋಗೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "company_name_label": "ಸಂಸ್ಥೆಯ ಹೆಸರು",
        "verify_logo_btn": "👁️ ಲೋಗೋ ಪರಿಶೀಲಿಸಿ",
        "visual_report": "ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆ ವರದಿ",
        "auth_index": "ವಿಶ್ವಾಸಾರ್ಹತೆ:",
        "authentic_badge": "🟢 ನೈಜ ಲೋಗೋ",
        "fake_badge": "🔴 ನಕಲಿ ಚಿತ್ರವಾಗಿರುವ ಸಾಧ್ಯತೆ ಹೆಚ್ಚು",
        "flaws_title": "🔍 ಪತ್ತೆಯಾದ ದೋಷಗಳು"
    },
    "తెలుగు": {
        "title": "⚡ ScamCheck AI",
        "subtitle": "ఇంటర్న్‌షిప్ మరియు ఉద్యోగ ఆఫర్లను ధృవీకరించే ప్లాట్‌ఫారమ్",
        "select": "🌐 మీ భాషను ఎంచుకోండి",
        "continue": "🚀 కొనసాగించండి",
        "sec_dashboard": "📈 సెక్యూరిటీ డాష్‌బోర్డ్",
        "scan_history_tab": "🧾 స్కాన్ హిస్టరీ",
        "cyber_shield_title": "🛡️ సైబర్ షీల్డ్ సెక్యూరిటీ సెంటర్",
        "cyber_shield_desc": "సందేహాస్పద సందేశాలు, లింకులు మరియు వివరాలను తనిఖీ చేయడానికి ఈ డాష్‌బోర్డ్‌ను ఉపయోగించండి.",
        "total_scans": "మొత్తం స్కాన్లు",
        "high_risk_scans": "హై రిస్క్ స్కాన్లు",
        "avg_risk": "సగటు రిస్క్",
        "quick_inspector_title": "🔎 మెసేజ్ ఇన్‌స్పెక్టర్",
        "quick_inspector_label": "తక్షణ తనిఖీ కోసం సందేహాస్పద సందేశాన్ని పేస్ట్ చేయండి",
        "run_quick_check": "⚡ సెక్యూరిటీ చెక్ చేయండి",
        "local_risk_score": "రిస్క్ స్కోర్",
        "no_red_flags": "🟢 ఎటువంటి పెద్ద ప్రమాద హెచ్చరికలు కనుగొనబడలేదు.",
        "red_flags": "🚩 ప్రమాద సూచికలు",
        "extracted_details": "🌐 లింకులు / సంప్రదింపు వివరాలు",
        "urls": "లింకులు:",
        "emails": "ఇమెయిళ్ళు:",
        "phones": "ఫోన్ నంబర్లు:",
        "safety_actions_title": "🛡️ సురక్షిత సూచనలు",
        "safety_actions": [
            "రిజిస్ట్రేషన్ లేదా శిక్షణ రుసుములను చెల్లించవద్దు.",
            "అధికారిక వెబ్‌సైట్‌లో ఉద్యోగ వివరాలను సరిచూసుకోండి.",
            "OTP, UPI PIN, లేదా బ్యాంకు వివరాలను పంచుకోవద్దు."
        ],
        "prev_scan_title": "🧾 క్రితం స్కాన్ ఫలితాలు",
        "no_scans": "ఎటువంటి హిస్టరీ లేదు.",
        "clear_history": "🗑️ హిస్టరీని క్లియర్ చేయండి",
        "verify_tab": "🚀 మెసేజ్‌ని తనిఖీ చేయండి",
        "logo_tab": "🔍 లోగోని సరిచూడండి",
        "presets_title": "⚡ నమూనా పరీక్షలు",
        "preset_fake": "🚨 నకిలీ HR మెసేజ్",
        "preset_telegram": "🟡 టెలిగ్రామ్ ఆఫర్",
        "preset_legit": "✅ నిజమైన ఉద్యోగం",
        "text_area_label": "మెసేజ్‌ని ఇక్కడ పేస్ట్ చేయండి",
        "scan_btn": "🔥 స్కాన్ చేయండి",
        "threat_report": "📊 విశ్లేషణ నివేదిక",
        "risk_score_card": "రిస్క్ స్కోర్",
        "threat_status": "ప్రమాద స్థాయి",
        "high_risk_badge": "🔴 తీవ్రమైన ప్రమాదం గుర్తించబడింది",
        "med_risk_badge": "🟡 మితమైన ప్రమాదం / జాగ్రత్త వహించండి",
        "low_risk_badge": "🟢 సురక్షితమైన సందేశం",
        "verdict": "తీర్పు:",
        "identified_indicators": "🚩 గుర్తించిన రిస్క్ వివరాలు",
        "logo_upload_label": "లోగోని అప్‌లోడ్ చేయండి",
        "company_name_label": "సంస్థ పేరు",
        "verify_logo_btn": "👁️ లోగోని తనిఖీ చేయండి",
        "visual_report": "చిత్ర విశ్లేషణ నివేదిక",
        "auth_index": "విశ్వసనీయత:",
        "authentic_badge": "🟢 నిజమైన లోగో",
        "fake_badge": "🔴 నకిలీ చిత్రమయ్యే అవకాశం ఉంది",
        "flaws_title": "🔍 గుర్తించిన లోపాలు"
    }
}

# Language Selection Screen First Render
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
    </style>
    <div class="language-screen">
        <div class="language-logo">🛡️ ScamCheck AI</div>
        <div style="color: #94a3b8; font-size: 1.05rem; margin-bottom: 28px;">
            Choose your preferred language / உங்கள் மொழியைத் தேர்ந்தெடுக்கவும் / अपनी भाषा चुनें
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_language = st.selectbox(
        "🌐 Select language / மொழியைத் தேர்ந்தெடுக்கவும்",
        list(LANGUAGES.keys()),
        index=0
    )

    if st.button(LANGUAGES[selected_language]["continue"], type="primary"):
        st.session_state["selected_language"] = selected_language
        st.session_state["language_selected"] = True
        st.rerun()

    st.stop()

selected_language = st.session_state.get("selected_language", "English")
UI = LANGUAGES.get(selected_language, LANGUAGES["English"])

# Sidebar language switcher
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

# ---------------------------------------------------------
# LOGIC & HEURISTICS
# ---------------------------------------------------------

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
         25, "🔐 Sensitive ID/Data Request: Asks for identity credentials via unverified channels."),
        (r'\b(bit\.ly|tinyurl|t\.co|goo\.gl)\b',
         10, "🔗 Shortened URL: Link destination is obfuscated."),
        (r'\b(\d+\s*hours?|today|urgent|limited time|act now|immediately)\b',
         15, "⏰ Extreme Urgency: Creates artificial pressure to bypass verification."),
        (r'\b(crypto|bitcoin|usdt|investment required)\b',
         18, "🪙 Financial Scheme Indicator: Links employment with investment."),
        (r'@gmail\.com|@yahoo\.com|@hotmail\.com|@outlook\.com',
         15, "📧 Public Email Domain: Recruitment uses generic webmail instead of company domain.")
    ]

    for pattern, points, message in rules:
        if re.search(pattern, t):
            flags.append(message)
            score += points

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

def show_safety_checklist():
    st.markdown(f"### {UI['safety_actions_title']}")
    for action in UI["safety_actions"]:
        st.markdown(f"- {action}")

# Dashboard Tabs
tab_dashboard, tab_history = st.tabs([UI["sec_dashboard"], UI["scan_history_tab"]])

with tab_dashboard:
    st.markdown(f"""
    <div class="glass-card">
        <h2>{UI["cyber_shield_title"]}</h2>
        <p>{UI["cyber_shield_desc"]}</p>
    </div>
    """, unsafe_allow_html=True)

    h1, h2, h3 = st.columns(3)
    history = st.session_state.get("scan_history", [])

    with h1:
        st.metric(UI["total_scans"], len(history))
    with h2:
        high_count = sum(1 for x in history if x["level"] == "High")
        st.metric(UI["high_risk_scans"], high_count)
    with h3:
        avg_score = (
            round(sum(x["score"] for x in history) / len(history), 1)
            if history else 0
        )
        st.metric(UI["avg_risk"], avg_score)

    st.markdown(f"### {UI['quick_inspector_title']}")
    quick_text = st.text_area(
        UI["quick_inspector_label"],
        height=150,
        key="quick_inspector"
    )

    if st.button(UI["run_quick_check"]):
        if not quick_text.strip():
            st.warning("Enter a message first.")
        else:
            extra_score, extra_flags = advanced_heuristic_check(quick_text)
            urls, emails, phones = extract_links_and_contacts(quick_text)

            st.metric(UI["local_risk_score"], f"{extra_score}/100")

            if extra_score >= 60:
                st.error(UI["high_risk_badge"])
            elif extra_score >= 30:
                st.warning(UI["med_risk_badge"])
            else:
                st.success(UI["no_red_flags"])

            if extra_flags:
                st.markdown(f"#### {UI['red_flags']}")
                for flag in extra_flags:
                    st.write(flag)

            with st.expander(UI["extracted_details"]):
                st.write(f"**{UI['urls']}**", urls if urls else "None")
                st.write(f"**{UI['emails']}**", emails if emails else "None")
                st.write(f"**{UI['phones']}**", phones if phones else "None")

            show_safety_checklist()

with tab_history:
    st.markdown(f"### {UI['prev_scan_title']}")

    if not history:
        st.info(UI["no_scans"])
    else:
        for item in history:
            with st.expander(
                f"{'🔴' if item['level']=='High' else '🟡' if item['level']=='Medium' else '🟢'} "
                f"{item['level']} Risk — Score {item['score']}/100"
            ):
                st.write("**Message:**", item["text"])
                st.write("**Indicators:**", item["indicators"])
                st.write("**Recommendation:**", item["recommendation"])

    if st.button(UI["clear_history"]):
        st.session_state["scan_history"] = []
        st.rerun()

# Primary App Tabs
tab_offer, tab_brand = st.tabs([UI["verify_tab"], UI["logo_tab"]])

with tab_offer:
    col_input, col_presets = st.columns([2, 1])

    with col_presets:
        st.markdown(f'<div class="glass-card"><b>{UI["presets_title"]}</b><br><br>', unsafe_allow_html=True)
        if st.button(UI["preset_fake"]):
            st.session_state["text_input"] = "Congratulations! You are selected for HR Assistant at Amazon. Salary 50,000 INR/month. Work 2 hours daily from home. Pay 1,500 INR registration fee to process laptop kit. Contact HR on WhatsApp: 9876543210."
        if st.button(UI["preset_telegram"]):
            st.session_state["text_input"] = "Urgent Hiring: Data Entry Operator needed. Pay: $200/day. No interview needed. Contact manager directly on Telegram @Jobs_HR_Fast."
        if st.button(UI["preset_legit"]):
            st.session_state["text_input"] = "We are hiring a Software Engineer Intern at TechCorp. Requirements: Python, React. Apply through our official portal: https://techcorp.com/careers/intern-2026."
        st.markdown('</div>', unsafe_allow_html=True)

    with col_input:
        user_text = st.text_area(
            UI["text_area_label"], 
            value=st.session_state.get("text_input", ""), 
            height=180
        )
        analyze_btn = st.button(UI["scan_btn"], type="primary")

    if analyze_btn:
        if not api_key:
            st.error("Please configure your Gemini API Key in the sidebar.")
        elif not user_text.strip():
            st.warning("Please paste offer details first.")
        else:
            with st.spinner("Analyzing..."):
                local_score, local_flags = advanced_heuristic_check(user_text)
                
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    Analyze this opportunity for scam risk and respond in {selected_language}:
                    "{user_text}"

                    Return ONLY a JSON object:
                    {{
                        "risk_score": <number 0 to 100>,
                        "risk_level": "<Low | Medium | High>",
                        "warning_indicators": ["<indicator 1>", "<indicator 2>"],
                        "recommendation": "<advice in {selected_language}>"
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
                        level = "High" if local_score >= 60 else "Medium" if local_score >= 30 else "Low"
                        data = {
                            "risk_score": local_score,
                            "risk_level": level,
                            "warning_indicators": local_flags,
                            "recommendation": "Analysis completed using local heuristic rules."
                        }
                    else:
                        st.error(f"Error: {e}")
                        st.stop()

                score = data.get("risk_score", 0)
                level = data.get("risk_level", "Unknown")

                st.markdown("---")
                st.markdown(f"### {UI['threat_report']}")

                m1, m2 = st.columns([1, 2])
                
                with m1:
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <span style="font-size: 0.9rem; color: #94a3b8;">{UI["risk_score_card"]}</span>
                        <h1 style="font-size: 3.5rem; margin: 0; color: #c084fc;">{score}</h1>
                        <span style="font-size: 0.8rem; color: #64748b;">out of 100</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(score / 100)

                with m2:
                    st.markdown(f"<div class='glass-card'><b>{UI['threat_status']}</b><br><br>", unsafe_allow_html=True)
                    if level == "High":
                        st.markdown(f'<span class="badge-danger">{UI["high_risk_badge"]}</span>', unsafe_allow_html=True)
                    elif level == "Medium":
                        st.markdown(f'<span class="badge-warning">{UI["med_risk_badge"]}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="badge-success">{UI["low_risk_badge"]}</span>', unsafe_allow_html=True)
                    
                    st.markdown(f"<br><br><b>{UI['verdict']}</b> {data.get('recommendation', '')}", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown(f"<div class='glass-card'><b>{UI['identified_indicators']}</b><br><br>", unsafe_allow_html=True)
                all_indicators = list(set(local_flags + data.get("warning_indicators", [])))
                for ind in all_indicators:
                    st.markdown(f"- {ind}")
                st.markdown("</div>", unsafe_allow_html=True)

                save_scan(user_text, score, level, all_indicators, data.get('recommendation', ''))

with tab_brand:
    col_upload, col_preview = st.columns([1, 1])

    with col_upload:
        uploaded_file = st.file_uploader(UI["logo_upload_label"], type=["png", "jpg", "jpeg"])
        company_name = st.text_input(UI["company_name_label"])
        verify_logo_btn = st.button(UI["verify_logo_btn"], type="primary")

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
                        st.image(img, caption="Preview", width=220)

                    client = genai.Client(api_key=api_key)
                    logo_prompt = f"""
                    Inspect this image claiming to be the logo of "{company_name}".
                    Look for pixelation, edited text, or missing brand features.

                    Return ONLY a JSON object:
                    {{
                        "authenticity_score": <number 0 to 100>,
                        "visual_flaws": ["<flaw 1>", "<flaw 2>"],
                        "summary": "<summary in {selected_language}>"
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
                        <h3>{UI['visual_report']}</h3>
                        <h2 style="color: #38bdf8;">{UI['auth_index']} {auth_score}/100</h2>
                    </div>
                    """, unsafe_allow_html=True)

                    if auth_score >= 70:
                        st.markdown(f'<span class="badge-success">{UI["authentic_badge"]}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="badge-danger">{UI["fake_badge"]}</span>', unsafe_allow_html=True)

                    st.markdown(f"<br><div class='glass-card'><b>{UI['flaws_title']}</b><br>", unsafe_allow_html=True)
                    for flaw in data.get("visual_flaws", []):
                        st.markdown(f"- {flaw}")
                    st.write(data.get("summary", ""))
                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {e}")
