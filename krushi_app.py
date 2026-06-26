"""
Krushi Rent AI : Intelligent Agricultural Rental Service
A complete AI-powered agricultural equipment rental platform
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import uuid
import re
import random
import sys
import io

# Force UTF-8 encoding for stdout/stderr
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'krushi_rent_ai_secret_2024'
app.config['JSON_AS_ASCII'] = False  # Enable UTF-8 for JSON responses

# CRITICAL: UTF-8 Configuration
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# Ensure all responses use UTF-8
@app.after_request
def after_request(response):
    response.headers['Content-Type'] = response.headers.get('Content-Type', 'text/html') + '; charset=utf-8'
    return response

# Conversation state storage
conversation_state = {}

# AI Recommendation translations
AI_RECO_TRANS = {
    'hi': {
        'Tractor': 'ट्रैक्टर', 'Harvester': 'हार्वेस्टर', 'Seeder': 'बीज बोने की मशीन',
        'Cultivator': 'कल्टीवेटर', 'Sprayer': 'स्प्रेयर', 'Bulldozer': 'बुलडोजर',
        'High': 'उच्च', 'Medium': 'मध्यम', 'Low': 'कम', 'Good': 'अच्छा',
        'Book Now': 'अभी बुक करें', 'AI Recommended': 'AI अनुशंसित',
        'AI Match': 'AI मिलान', 'per day': 'प्रति दिन'
    }
}

def translate_ai(text, lang='hi'):
    if lang != 'hi' or not text: return text
    return AI_RECO_TRANS.get(lang, {}).get(text, text)

# Dashboard translations
DASHBOARD_TRANSLATIONS = {
    "en": {"ai_reco": "AI Equipment Recommendations", "farming_stage": "Farming Stage", "crop_category": "Crop Category", "farm_size": "Farm Size", "season": "Season", "budget": "Budget Range (per day)", "urgency": "Urgency", "get_reco": "Get AI Equipment Recommendations", "total_bookings": "Total Bookings", "recent_bookings": "Recent Bookings", "dashboard_title": "Farmer Dashboard", "welcome": "Welcome", "rental_service": "Rental Service", "logout": "Logout", "no_bookings": "No bookings yet. Start by getting AI recommendations!", "select_farm_size": "Select Farm Size", "small_farm": "Small Farm (0.5 - 2 acres)", "medium_farm": "Medium Farm (2 - 10 acres)", "large_farm": "Large Farm (10+ acres)", "select_season": "Select Season", "kharif": "Kharif (Monsoon Season)", "rabi": "Rabi (Winter Season)", "summer": "Summer Season", "year_round": "Year Round", "select_budget": "Select Budget Range", "low_budget": "Low Budget (₹500 - ₹1500)", "medium_budget": "Medium Budget (₹1500 - ₹3000)", "high_budget": "High Budget (₹3000+)", "select_urgency": "Select Urgency", "immediate": "Immediate (Today/Tomorrow)", "this_week": "This Week", "flexible": "Flexible Timing", "page_title": "Farmer Dashboard - Krushi Rent AI", "krushi_farmer": "Krushi Rent AI - Farmer"},
    "te": {"ai_reco": "AI పరికర సూచనలు", "farming_stage": "వ్యవసాయ దశ", "crop_category": "పంట వర్గం", "farm_size": "పొలం పరిమాణం", "season": "కాలం", "budget": "బడ్జెట్ పరిధి (రోజుకు)", "urgency": "తక్షణ అవసరం", "get_reco": "AI సూచనలు పొందండి", "total_bookings": "మొత్తం బుకింగ్స్", "recent_bookings": "ఇటీవల బుకింగ్స్", "dashboard_title": "రైతు డాష్బోర్డ్", "welcome": "స్వాగతం", "rental_service": "అద్దె సేవ", "logout": "లాగ్అవుట్", "no_bookings": "ఇంకా బుకింగ్స్ లేవు. AI సూచనలు పొందడం ద్వారా ప్రారంభించండి!", "select_farm_size": "పొలం పరిమాణం ఎంచుకోండి", "small_farm": "చిన్న పొలం (0.5 - 2 ఎకరాలు)", "medium_farm": "మధ్యస్థ పొలం (2 - 10 ఎకరాలు)", "large_farm": "పెద్ద పొలం (10+ ఎకరాలు)", "select_season": "కాలం ఎంచుకోండి", "kharif": "ఖరీఫ్ (వర్షాకాలం)", "rabi": "రబీ (శీతాకాలం)", "summer": "వేసవి కాలం", "year_round": "ఏడాది పొడవునా", "select_budget": "బడ్జెట్ పరిధి ఎంచుకోండి", "low_budget": "తక్కువ బడ్జెట్ (₹500 - ₹1500)", "medium_budget": "మధ్యస్థ బడ్జెట్ (₹1500 - ₹3000)", "high_budget": "అధిక బడ్జెట్ (₹3000+)", "select_urgency": "తక్షణ అవసరం ఎంచుకోండి", "immediate": "తక్షణం (ఈరోజు/రేపు)", "this_week": "ఈ వారం", "flexible": "సౌకర్యవంతమైన సమయం", "page_title": "రైతు డాష్బోర్డ్ - కృషి రెంట్ AI", "krushi_farmer": "కృషి రెంట్ AI - రైతు"},
    "hi": {"ai_reco": "AI उपकरण सुझाव", "farming_stage": "कृषि चरण", "crop_category": "फसल श्रेणी", "farm_size": "खेत का आकार", "season": "मौसम", "budget": "बजट सीमा (प्रति दिन)", "urgency": "तत्कालता", "get_reco": "AI सुझाव प्राप्त करें", "total_bookings": "कुल बुकिंग", "recent_bookings": "हाल की बुकिंग", "dashboard_title": "किसान डैशबोर्ड", "welcome": "स्वागत", "rental_service": "किराया सेवा", "logout": "लॉगआउट", "no_bookings": "अभी तक कोई बुकिंग नहीं। AI सुझाव प्राप्त करके शुरू करें!", "select_farm_size": "खेत का आकार चुनें", "small_farm": "छोटा खेत (0.5 - 2 एकड़)", "medium_farm": "मध्यम खेत (2 - 10 एकड़)", "large_farm": "बड़ा खेत (10+ एकड़)", "select_season": "मौसम चुनें", "kharif": "खरीफ (मानसून मौसम)", "rabi": "रबी (सर्दी मौसम)", "summer": "गर्मी मौसम", "year_round": "साल भर", "select_budget": "बजट सीमा चुनें", "low_budget": "कम बजट (₹500 - ₹1500)", "medium_budget": "मध्यम बजट (₹1500 - ₹3000)", "high_budget": "उच्च बजट (₹3000+)", "select_urgency": "तत्कालता चुनें", "immediate": "तत्काल (आज/कल)", "this_week": "इस सप्ताह", "flexible": "लचीला समय", "page_title": "किसान डैशबोर्ड - कृषि रेंट AI", "krushi_farmer": "कृषि रेंट AI - किसान"},
    "kn": {"ai_reco": "AI ಉಪಕರಣ ಶಿಫಾರಸುಗಳು", "farming_stage": "ಕೃಷಿ ಹಂತ", "crop_category": "ಬೆಳೆ ವರ್ಗ", "farm_size": "ಫಾರ್ಮ್ ಗಾತ್ರ", "season": "ಋತು", "budget": "ಬಜೆಟ್ ವ್ಯಾಪ್ತಿ (ದಿನಕ್ಕೆ)", "urgency": "ತುರ್ತು", "get_reco": "AI ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ", "total_bookings": "ಒಟ್ಟು ಬುಕಿಂಗ್ಗಳು", "recent_bookings": "ಇತ್ತೀಚಿನ ಬುಕಿಂಗ್ಗಳು", "dashboard_title": "ರೈತ ಡ್ಯಾಶ್ಬೋರ್ಡ್", "welcome": "ಸ್ವಾಗತ", "rental_service": "ಬಾಡಿಗೆ ಸೇವೆ", "logout": "ಲಾಗ್ಔಟ್", "no_bookings": "ಇನ್ನೂ ಬುಕಿಂಗ್ಗಳಿಲ್ಲ. AI ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯುವ ಮೂಲಕ ಪ್ರಾರಂಭಿಸಿ!", "select_farm_size": "ಫಾರ್ಮ್ ಗಾತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ", "small_farm": "ಸಣ್ಣ ಫಾರ್ಮ್ (0.5 - 2 ಎಕರೆಗಳು)", "medium_farm": "ಮಧ್ಯಮ ಫಾರ್ಮ್ (2 - 10 ಎಕರೆಗಳು)", "large_farm": "ದೊಡ್ಡ ಫಾರ್ಮ್ (10+ ಎಕರೆಗಳು)", "select_season": "ಋತುವನ್ನು ಆಯ್ಕೆಮಾಡಿ", "kharif": "ಖರೀಫ್ (ಮಾನ್ಸೂನ್ ಋತು)", "rabi": "ರಬಿ (ಚಳಿಗಾಲ ಋತು)", "summer": "ಬೇಸಿಗೆ ಋತು", "year_round": "ವರ್ಷಪೂರ್ತಿ", "select_budget": "ಬಜೆಟ್ ವ್ಯಾಪ್ತಿಯನ್ನು ಆಯ್ಕೆಮಾಡಿ", "low_budget": "ಕಡಿಮೆ ಬಜೆಟ್ (₹500 - ₹1500)", "medium_budget": "ಮಧ್ಯಮ ಬಜೆಟ್ (₹1500 - ₹3000)", "high_budget": "ಹೆಚ್ಚಿನ ಬಜೆಟ್ (₹3000+)", "select_urgency": "ತುರ್ತು ಆಯ್ಕೆಮಾಡಿ", "immediate": "ತಕ್ಷಣ (ಇಂದು/ನಾಳೆ)", "this_week": "ಈ ವಾರ", "flexible": "ಹೊಂದಿಕೊಳ್ಳುವ ಸಮಯ", "page_title": "ರೈತ ಡ್ಯಾಶ್ಬೋರ್ಡ್ - ಕೃಷಿ ರೆಂಟ್ AI", "krushi_farmer": "ಕೃಷಿ ರೆಂಟ್ AI - ರೈತ"},
    "ta": {"ai_reco": "AI உபகரண பரிந்துரைகள்", "farming_stage": "விவசாய நிலை", "crop_category": "பயிர் வகை", "farm_size": "பண்ணை அளவு", "season": "பருவம்", "budget": "பட்ஜெட் வரம்பு (நாளுக்கு)", "urgency": "அவசரம்", "get_reco": "AI பரிந்துரைகளைப் பெறுங்கள்", "total_bookings": "மொத்த முன்பதிவுகள்", "recent_bookings": "சமீபத்திய முன்பதிவுகள்", "dashboard_title": "விவசாயி டாஷ்போர்டு", "welcome": "வரவேற்பு", "rental_service": "வாடகை சேவை", "logout": "வெளியேறு", "no_bookings": "இன்னும் முன்பதிவுகள் இல்லை. AI பரிந்துரைகளைப் பெறுவதன் மூலம் தொடங்குங்கள்!", "select_farm_size": "பண்ணை அளவைத் தேர்ந்தெடுக்கவும்", "small_farm": "சிறிய பண்ணை (0.5 - 2 ஏக்கர்)", "medium_farm": "நடுத்தர பண்ணை (2 - 10 ஏக்கர்)", "large_farm": "பெரிய பண்ணை (10+ ஏக்கர்)", "select_season": "பருவத்தைத் தேர்ந்தெடுக்கவும்", "kharif": "கரீஃப் (பருவமழை பருவம்)", "rabi": "ரபி (குளிர்கால பருவம்)", "summer": "கோடை பருவம்", "year_round": "ஆண்டு முழுவதும்", "select_budget": "பட்ஜெட் வரம்பைத் தேர்ந்தெடுக்கவும்", "low_budget": "குறைந்த பட்ஜெட் (₹500 - ₹1500)", "medium_budget": "நடுத்தர பட்ஜெட் (₹1500 - ₹3000)", "high_budget": "அதிக பட்ஜெட் (₹3000+)", "select_urgency": "அவசரத்தைத் தேர்ந்தெடுக்கவும்", "immediate": "உடனடி (இன்று/நாளை)", "this_week": "இந்த வாரம்", "flexible": "நெகிழ்வான நேரம்", "page_title": "விவசாயி டாஷ்போர்டு - கிருஷி ரென்ட் AI", "krushi_farmer": "கிருஷி ரென்ட் AI - விவசாயி"}
}

# Index page translations
INDEX_TRANSLATIONS = {
    "en": {"title": "Krushi Rent AI", "subtitle": "ML Based Rental & Recommendation System for Agriculture Equipment", "hero_subtitle": "AI-Powered Equipment Recommendations for Smart Farming", "farmer_title": "Farmer Login", "farmer_desc": "Get AI-powered equipment recommendations based on your crop, land size, and farming needs. Book equipment easily and manage your rentals.", "owner_title": "Equipment Owner", "owner_desc": "List your agricultural equipment for rent, manage bookings, track earnings, and help farmers access the tools they need.", "admin_title": "Admin Login", "admin_desc": "Monitor system performance, manage users and equipment, view analytics, and ensure smooth operation of the platform.", "login": "Login", "register": "Register", "chat_welcome": "Hello! I'm Krushi AI. Ask me about farming equipment, crops, or agricultural advice!", "chat_placeholder": "Ask about farming...", "username": "Username", "password": "Password", "username_placeholder": "Enter your username", "password_placeholder": "Enter your password", "no_account": "Don't have an account?", "register_here": "Register here", "back_home": "Back to Home"},
    "te": {"title": "కృషి రెంట్ AI", "subtitle": "తెలివైన వ్యవసాయ అద్దె సేవ", "hero_subtitle": "స్మార్ట్ వ్యవసాయం కోసం AI-శక్తితో కూడిన పరికర సూచనలు", "farmer_title": "రైతు లాగిన్", "farmer_desc": "మీ పంట, భూమి పరిమాణం మరియు వ్యవసాయ అవసరాల ఆధారంగా AI-శక్తితో కూడిన పరికర సూచనలు పొందండి. పరికరాలను సులభంగా బుక్ చేసుకోండి.", "owner_title": "పరికర యజమాని", "owner_desc": "మీ వ్యవసాయ పరికరాలను అద్దెకు జాబితా చేయండి, బుకింగ్లను నిర్వహించండి, ఆదాయాలను ట్రాక్ చేయండి.", "admin_title": "అడ్మిన్ లాగిన్", "admin_desc": "సిస్టమ్ పనితీరును పర్యవేక్షించండి, వినియోగదారులు మరియు పరికరాలను నిర్వహించండి, విశ్లేషణలను చూడండి.", "login": "లాగిన్", "register": "నమోదు", "chat_welcome": "నమస్కారం! నేను కృషి AI. వ్యవసాయ పరికరాలు, పంటలు లేదా వ్యవసాయ సలహా గురించి అడగండి!", "chat_placeholder": "వ్యవసాయం గురించి అడగండి...", "username": "వినియోగదారు పేరు", "password": "పాస్వర్డ్", "username_placeholder": "మీ వినియోగదారు పేరు నమోదు చేయండి", "password_placeholder": "మీ పాస్వర్డ్ నమోదు చేయండి", "no_account": "ఖాతా లేదా?", "register_here": "ఇక్కడ నమోదు చేయండి", "back_home": "హోమ్‌కు తిరిగి వెళ్ళండి"},
    "hi": {"title": "कृषि रेंट AI", "subtitle": "बुद्धिमान कृषि किराया सेवा", "hero_subtitle": "स्मार्ट खेती के लिए AI-संचालित उपकरण सुझाव", "farmer_title": "किसान लॉगिन", "farmer_desc": "अपनी फसल, भूमि के आकार और खेती की जरूरतों के आधार पर AI-संचालित उपकरण सुझाव प्राप्त करें। उपकरण आसानी से बुक करें।", "owner_title": "उपकरण मालिक", "owner_desc": "अपने कृषि उपकरणों को किराए पर सूचीबद्ध करें, बुकिंग प्रबंधित करें, कमाई ट्रैक करें।", "admin_title": "एडमिन लॉगिन", "admin_desc": "सिस्टम प्रदर्शन की निगरानी करें, उपयोगकर्ताओं और उपकरणों का प्रबंधन करें, विश्लेषण देखें।", "login": "लॉगिन", "register": "रजिस्टर", "chat_welcome": "नमस्ते! मैं कृषि AI हूं। खेती के उपकरण, फसलों या कृषि सलाह के बारे में पूछें!", "chat_placeholder": "खेती के बारे में पूछें...", "username": "उपयोगकर्ता नाम", "password": "पासवर्ड", "username_placeholder": "अपना उपयोगकर्ता नाम दर्ज करें", "password_placeholder": "अपना पासवर्ड दर्ज करें", "no_account": "खाता नहीं है?", "register_here": "यहां रजिस्टर करें", "back_home": "होम पर वापस जाएं"},
    "kn": {"title": "ಕೃಷಿ ರೆಂಟ್ AI", "subtitle": "ಬುದ್ಧಿವಂತ ಕೃಷಿ ಬಾಡಿಗೆ ಸೇವೆ", "hero_subtitle": "ಸ್ಮಾರ್ಟ್ ಕೃಷಿಗಾಗಿ AI-ಚಾಲಿತ ಉಪಕರಣ ಶಿಫಾರಸುಗಳು", "farmer_title": "ರೈತ ಲಾಗಿನ್", "farmer_desc": "ನಿಮ್ಮ ಬೆಳೆ, ಭೂಮಿ ಗಾತ್ರ ಮತ್ತು ಕೃಷಿ ಅಗತ್ಯಗಳ ಆಧಾರದ ಮೇಲೆ AI-ಚಾಲಿತ ಉಪಕರಣ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ.", "owner_title": "ಉಪಕರಣ ಮಾಲೀಕ", "owner_desc": "ನಿಮ್ಮ ಕೃಷಿ ಉಪಕರಣಗಳನ್ನು ಬಾಡಿಗೆಗೆ ಪಟ್ಟಿ ಮಾಡಿ, ಬುಕಿಂಗ್ಗಳನ್ನು ನಿರ್ವಹಿಸಿ.", "admin_title": "ಅಡ್ಮಿನ್ ಲಾಗಿನ್", "admin_desc": "ಸಿಸ್ಟಮ್ ಕಾರ್ಯಕ್ಷಮತೆಯನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ, ಬಳಕೆದಾರರು ಮತ್ತು ಉಪಕರಣಗಳನ್ನು ನಿರ್ವಹಿಸಿ.", "login": "ಲಾಗಿನ್", "register": "ನೋಂದಣಿ", "chat_welcome": "ನಮಸ್ಕಾರ! ನಾನು ಕೃಷಿ AI. ಕೃಷಿ ಉಪಕರಣಗಳು, ಬೆಳೆಗಳು ಅಥವಾ ಕೃಷಿ ಸಲಹೆಯ ಬಗ್ಗೆ ಕೇಳಿ!", "chat_placeholder": "ಕೃಷಿಯ ಬಗ್ಗೆ ಕೇಳಿ...", "username": "ಬಳಕೆದಾರ ಹೆಸರು", "password": "ಪಾಸ್ವರ್ಡ್", "username_placeholder": "ನಿಮ್ಮ ಬಳಕೆದಾರ ಹೆಸರನ್ನು ನಮೂದಿಸಿ", "password_placeholder": "ನಿಮ್ಮ ಪಾಸ್ವರ್ಡ್ ಅನ್ನು ನಮೂದಿಸಿ", "no_account": "ಖಾತೆ ಇಲ್ಲವೇ?", "register_here": "ಇಲ್ಲಿ ನೋಂದಣಿ ಮಾಡಿ", "back_home": "ಮುಖಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಿ"},
    "ta": {"title": "கிருஷி ரென்ட் AI", "subtitle": "புத்திசாலித்தனமான விவசாய வாடகை சேவை", "hero_subtitle": "ஸ்மார்ட் விவசாயத்திற்கான AI-இயங்கும் உபகரண பரிந்துரைகள்", "farmer_title": "விவசாயி உள்நுழைவு", "farmer_desc": "உங்கள் பயிர், நில அளவு மற்றும் விவசாய தேவைகளின் அடிப்படையில் AI-இயங்கும் உபகரண பரிந்துரைகளைப் பெறுங்கள்.", "owner_title": "உபகரண உரிமையாளர்", "owner_desc": "உங்கள் விவசாய உபகரணங்களை வாடகைக்கு பட்டியலிடுங்கள், முன்பதிவுகளை நிர்வகிக்கவும்.", "admin_title": "நிர்வாகி உள்நுழைவு", "admin_desc": "கணினி செயல்திறனை கண்காணிக்கவும், பயனர்கள் மற்றும் உபகரணங்களை நிர்வகிக்கவும்.", "login": "உள்நுழைவு", "register": "பதிவு", "chat_welcome": "வணக்கம்! நான் கிருஷி AI. விவசாய உபகரணங்கள், பயிர்கள் அல்லது விவசாய ஆலோசனை பற்றி கேளுங்கள்!", "chat_placeholder": "விவசாயம் பற்றி கேளுங்கள்...", "username": "பயனர் பெயர்", "password": "கடவுச்சொல்", "username_placeholder": "உங்கள் பயனர் பெயரை உள்ளிடவும்", "password_placeholder": "உங்கள் கடவுச்சொல்லை உள்ளிடவும்", "no_account": "கணக்கு இல்லையா?", "register_here": "இங்கே பதிவு செய்யுங்கள்", "back_home": "முகப்புக்கு திரும்பு"}
}


def classify_intent(message):
    """Classify user intent with high accuracy"""
    message = message.lower().strip()
    
    # Greeting patterns
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'namaste']
    if any(greeting in message for greeting in greetings):
        return 'greeting'
    
    # Question patterns
    question_words = ['what', 'how', 'when', 'where', 'why', 'which', 'can you', 'do you']
    if any(word in message for word in question_words):
        return 'question'
    
    # Equipment request patterns
    equipment_keywords = ['need', 'want', 'rent', 'hire', 'tractor', 'harvester', 'equipment']
    if any(word in message for word in equipment_keywords):
        return 'equipment_request'
    
    # Problem/issue patterns
    problem_keywords = ['problem', 'issue', 'help', 'disease', 'pest', 'yellow', 'dying']
    if any(word in message for word in problem_keywords):
        return 'problem'
    
    return 'general'

def extract_entities(message):
    """Extract key entities from user message"""
    entities = {}
    message = message.lower()
    
    # Extract crops
    crops = ['rice', 'wheat', 'cotton', 'tomato', 'potato', 'onion', 'maize', 'corn']
    for crop in crops:
        if crop in message:
            entities['crop'] = crop
            break
    
    # Extract farm size
    if any(word in message for word in ['small', '1 acre', '2 acre']):
        entities['farm_size'] = 'small'
    elif any(word in message for word in ['large', 'big', '10 acre', '20 acre']):
        entities['farm_size'] = 'large'
    
    # Extract equipment types
    equipment_types = ['tractor', 'harvester', 'plough', 'cultivator', 'seeder']
    for equipment in equipment_types:
        if equipment in message:
            entities['equipment'] = equipment
            break
    
    return entities

def get_equipment_in_language(equipment_name, user_lang='en'):
    """Get equipment name in user's preferred language"""
    if user_lang == 'en':
        return equipment_name
    
    conn = get_db_connection()
    try:
        # Get translation from database
        translation = conn.execute('''
            SELECT et.translated_name 
            FROM equipment e
            JOIN equipment_translations et ON e.id = et.equipment_id
            WHERE e.name = ? AND et.language_code = ?
        ''', (equipment_name, user_lang)).fetchone()
        
        if translation:
            return translation['translated_name']
    except:
        pass
    finally:
        conn.close()
    
    return equipment_name

def get_realistic_farming_advice(crop, problem_type, user_lang='en'):
    """Generate realistic, practical farming advice"""
    advice_db = {
        'rice': {
            'yellow_leaves': {
                'en': "Yellow leaves in rice indicate nitrogen deficiency. Apply 25kg urea per acre immediately. Check for proper drainage - waterlogged fields cause yellowing. If problem persists, test soil pH (should be 5.5-6.5).",
                'hi': "चावल में पीले पत्ते नाइट्रोजन की कमी दर्शाते हैं। तुरंत 25 किलो यूरिया प्रति एकड़ डालें। जल निकासी जांचें।",
                'kn': "ಅಕ್ಕಿಯಲ್ಲಿ ಹಳದಿ ಎಲೆಗಳು ಸಾರಜನಕ ಕೊರತೆಯನ್ನು ಸೂಚಿಸುತ್ತವೆ. ತಕ್ಷಣ 25 ಕೆಜಿ ಯೂರಿಯಾ ಪ್ರತಿ ಎಕರೆಗೆ ಹಾಕಿ.",
                'te': "వరిలో పసుపు ఆకులు నత్రజని లోపాన్ని సూచిస్తాయి. వెంటనే ఎకరానికి 25 కిలోల యూరియా వేయండి."
            },
            'pest_attack': {
                'en': "For rice pest control: Use Neem oil 5ml/liter for stem borer. Install pheromone traps. For brown plant hopper, spray Imidacloprid 0.5ml/liter in evening.",
                'hi': "चावल में कीट नियंत्रण: तना छेदक के लिए नीम तेल 5ml/लीटर। भूरे फुदके के लिए इमिडाक्लोप्रिड छिड़कें।",
                'kn': "ಅಕ್ಕಿ ಕೀಟ ನಿಯಂತ್ರಣ: ಕಾಂಡ ಕೊರೆಯುವ ಕೀಟಕ್ಕೆ ಬೇವಿನ ಎಣ್ಣೆ 5ml/ಲೀಟರ್.",
                'te': "వరి కీటక నియంత్రణ: కాండం తొలుచు కీటకానికి వేప నూనె 5ml/లీటర్."
            }
        },
        'wheat': {
            'yellow_leaves': {
                'en': "Wheat yellowing suggests rust disease or nutrient deficiency. Spray Propiconazole 1ml/liter for rust. Apply DAP 50kg/acre for nutrients.",
                'hi': "गेहूं में पीलापन रस्ट रोग या पोषक तत्वों की कमी है। रस्ट के लिए प्रोपिकोनाजोल छिड़कें।",
                'kn': "ಗೋಧಿಯಲ್ಲಿ ಹಳದಿ ಬಣ್ಣ ರಸ್ಟ್ ರೋಗ ಅಥವಾ ಪೋಷಕಾಂಶ ಕೊರತೆ.",
                'te': "గోధుమలో పసుపు రంగు రస్ట్ వ్యాధి లేదా పోషకాల లోపం."
            }
        },
        'tomato': {
            'yellow_leaves': {
                'en': "Tomato leaf yellowing indicates overwatering or early blight. Reduce watering frequency. Spray Mancozeb 2g/liter. Ensure good air circulation.",
                'hi': "टमाटर में पीले पत्ते अधिक पानी या अर्ली ब्लाइट दर्शाते हैं। पानी कम करें।",
                'kn': "ಟೊಮೇಟೊದಲ್ಲಿ ಹಳದಿ ಎಲೆಗಳು ಅಧಿಕ ನೀರು ಅಥವಾ ಆರಂಭಿಕ ಬ್ಲೈಟ್.",
                'te': "టమాటోలో పసుపు ఆకులు అధిక నీరు లేదా ఎర్లీ బ్లైట్."
            }
        }
    }
    
    return advice_db.get(crop, {}).get(problem_type, {}).get(user_lang, 
        f"For {crop} {problem_type}, consult your local agricultural extension officer for specific treatment.")

def generate_intelligent_response(user_id, message, intent, entities):
    """Generate contextual, intelligent responses with multilingual support"""
    
    # Get user language
    user_lang = get_user_language()
    
    # Get or create conversation state
    if user_id not in conversation_state:
        conversation_state[user_id] = {'context': {}, 'last_intent': None}
    
    state = conversation_state[user_id]
    
    if intent == 'greeting':
        greetings = {
            'en': ["Hello! I'm KrushiRent AI, your farming assistant. How can I help you today?",
                   "Hi there! I'm here to help with your farming needs. What's on your mind?"],
            'hi': ["नमस्ते! मैं कृषि रेंट AI हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
                   "हैलो! मैं आपकी खेती की जरूरतों में मदद के लिए यहां हूं।"],
            'kn': ["ನಮಸ್ಕಾರ! ನಾನು ಕೃಷಿ ರೆಂಟ್ AI. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
                   "ಹಲೋ! ನಿಮ್ಮ ಕೃಷಿ ಅಗತ್ಯಗಳಿಗೆ ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ."],
            'te': ["నమస్కారం! నేను కృషి రెంట్ AI. ఈరోజు నేను మీకు ఎలా సహాయం చేయగలను?",
                   "హలో! మీ వ్యవసాయ అవసరాలకు సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను."]
        }
        state['context'] = {'greeted': True}
        return random.choice(greetings.get(user_lang, greetings['en']))
    
    elif intent == 'equipment_request':
        if 'crop' in entities and 'equipment' in entities:
            crop = entities['crop']
            equipment = entities['equipment']
            equipment_local = get_equipment_in_language(equipment.title(), user_lang)
            
            # Get actual equipment from database with pricing
            conn = get_db_connection()
            try:
                eq_data = conn.execute('''
                    SELECT name, price_per_day, location FROM equipment 
                    WHERE name LIKE ? AND available = 1 
                    ORDER BY price_per_day ASC LIMIT 1
                ''', (f'%{equipment}%',)).fetchone()
                
                if eq_data:
                    if user_lang == 'hi':
                        return f"{crop} की खेती के लिए {equipment_local} उपलब्ध है। दर: ₹{eq_data['price_per_day']}/दिन, स्थान: {eq_data['location']}। बुकिंग के लिए ऊपर AI सुझाव देखें।"
                    elif user_lang == 'kn':
                        return f"{crop} ಕೃಷಿಗೆ {equipment_local} ಲಭ್ಯವಿದೆ. ದರ: ₹{eq_data['price_per_day']}/ದಿನ, ಸ್ಥಳ: {eq_data['location']}. ಬುಕಿಂಗ್‌ಗಾಗಿ ಮೇಲಿನ AI ಸಲಹೆಗಳನ್ನು ನೋಡಿ."
                    elif user_lang == 'te':
                        return f"{crop} వ್యవసాయానికి {equipment_local} అందుబాటులో ఉంది. రేటు: ₹{eq_data['price_per_day']}/రోజు, స్థలం: {eq_data['location']}. బుకింగ్ కోసం పైన AI సూచనలు చూడండి."
                    else:
                        return f"Perfect! {equipment_local} available for {crop} farming at ₹{eq_data['price_per_day']}/day in {eq_data['location']}. Check AI Recommendations above for booking."
            finally:
                conn.close()
        
        elif 'crop' in entities:
            crop = entities['crop']
            if user_lang == 'hi':
                return f"{crop} की खेती के लिए आपको कौन सा उपकरण चाहिए - ट्रैक्टर, हार्वेस्टर, या कुछ और?"
            elif user_lang == 'kn':
                return f"{crop} ಕೃಷಿಗೆ ನಿಮಗೆ ಯಾವ ಉಪಕರಣ ಬೇಕು - ಟ್ರಾಕ್ಟರ್, ಹಾರ್ವೆಸ್ಟರ್, ಅಥವಾ ಬೇರೆ ಏನಾದರೂ?"
            elif user_lang == 'te':
                return f"{crop} వ్యవసాయానికి మీకు ఏ పరికరం కావాలి - ట్రాక్టర్, హార్వెస్టర్, లేదా మరేదైనా?"
            else:
                return f"For {crop} farming, what equipment do you need - tractor, harvester, or something else?"
        
        else:
            if user_lang == 'hi':
                return "मैं उपकरण खोजने में मदद कर सकता हूं। कृपया बताएं: 1) आप कौन सी फसल उगा रहे हैं? 2) कौन सा उपकरण चाहिए?"
            elif user_lang == 'kn':
                return "ನಾನು ಉಪಕರಣ ಹುಡುಕಲು ಸಹಾಯ ಮಾಡಬಹುದು. ದಯವಿಟ್ಟು ಹೇಳಿ: 1) ನೀವು ಯಾವ ಬೆಳೆ ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ? 2) ಯಾವ ಉಪಕರಣ ಬೇಕು?"
            elif user_lang == 'te':
                return "నేను పరికరాలు కనుగొనడంలో సహాయం చేయగలను. దయచేసి చెప్పండి: 1) మీరు ఏ పంట పండిస్తున్నారు? 2) ఏ పరికరం కావాలి?"
            else:
                return "I can help find equipment! Please tell me: 1) What crop are you growing? 2) What equipment do you need?"
    
    elif intent == 'problem':
        if 'crop' in entities:
            crop = entities['crop']
            problem_type = 'yellow_leaves' if 'yellow' in message else 'pest_attack' if 'pest' in message else 'general'
            
            # Get realistic farming advice
            advice = get_realistic_farming_advice(crop, problem_type, user_lang)
            return advice
        else:
            if user_lang == 'hi':
                return "मैं फसल की समस्याओं में मदद कर सकता हूं। कौन सी फसल में समस्या है और क्या लक्षण दिख रहे हैं?"
            elif user_lang == 'kn':
                return "ನಾನು ಬೆಳೆ ಸಮಸ್ಯೆಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಹುದು. ಯಾವ ಬೆಳೆಯಲ್ಲಿ ಸಮಸ್ಯೆ ಮತ್ತು ಯಾವ ಲಕ್ಷಣಗಳು ಕಾಣುತ್ತಿವೆ?"
            elif user_lang == 'te':
                return "నేను పంట సమస్యలలో సహాయం చేయగలను. ఏ పంటలో సమస్య మరియు ఏ లక్షణాలు కనిపిస్తున్నాయి?"
            else:
                return "I can help with crop problems. Which crop is having issues and what symptoms are you seeing?"
    
    elif intent == 'question':
        if 'price' in message or 'cost' in message:
            if user_lang == 'hi':
                return "उपकरण किराया दरें: छोटा ट्रैक्टर ₹800-1200/दिन, बड़ा ट्रैक्टर ₹1500-2500/दिन, हार्वेस्टर ₹3000-5000/दिन। कौन सा उपकरण चाहिए?"
            elif user_lang == 'kn':
                return "ಉಪಕರಣ ಬಾಡಿಗೆ ದರಗಳು: ಸಣ್ಣ ಟ್ರಾಕ್ಟರ್ ₹800-1200/ದಿನ, ದೊಡ್ಡ ಟ್ರಾಕ್ಟರ್ ₹1500-2500/ದಿನ, ಹಾರ್ವೆಸ್ಟರ್ ₹3000-5000/ದಿನ."
            elif user_lang == 'te':
                return "పరికరాల అద్దె రేట్లు: చిన్న ట్రాక్టర్ ₹800-1200/రోజు, పెద్ద ట్రాక్టర్ ₹1500-2500/రోజు, హార్వెస్టర్ ₹3000-5000/రోజు."
            else:
                return "Equipment rental rates: Small tractor ₹800-1200/day, Large tractor ₹1500-2500/day, Harvester ₹3000-5000/day. Which equipment interests you?"
        
        else:
            if user_lang == 'hi':
                return "मैं खेती के सवालों का जवाब दे सकता हूं। कृपया अपना सवाल स्पष्ट रूप से पूछें।"
            elif user_lang == 'kn':
                return "ನಾನು ಕೃಷಿ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಬಹುದು. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಿ."
            elif user_lang == 'te':
                return "నేను వ్యవసాయ ప్రశ్నలకు సమాధానం ఇవ్వగలను. దయచేసి మీ ప్రశ్నను స్పష్టంగా అడగండి."
            else:
                return "I can answer farming questions. Please ask your question more specifically."
    
    else:  # general
        if user_lang == 'hi':
            return "मैं उपकरण किराया, फसल सलाह, कीट नियंत्रण और खेती की जानकारी में मदद कर सकता हूं। आपको क्या चाहिए?"
        elif user_lang == 'kn':
            return "ನಾನು ಉಪಕರಣ ಬಾಡಿಗೆ, ಬೆಳೆ ಸಲಹೆ, ಕೀಟ ನಿಯಂತ್ರಣ ಮತ್ತು ಕೃಷಿ ಮಾರ್ಗದರ್ಶನದಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಹುದು. ನಿಮಗೆ ಏನು ಬೇಕು?"
        elif user_lang == 'te':
            return "నేను పరికరాల అద్దె, పంట సలహా, కీటక నియంత్రణ మరియు వ్యవసాయ మార్గదర్శకత్వంలో సహాయం చేయగలను. మీకు ఏమి కావాలి?"
        else:
            return "I can help with equipment rental, crop advice, pest control, and farming guidance. What do you need?"

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').strip()
    
    if not user_msg:
        return jsonify({'reply': 'Please type a message to get help.'})
    
    # Get or create user ID for conversation tracking
    user_id = session.get('user_id', 'anonymous')
    
    # Track conversation count for dynamic responses
    if user_id not in conversation_state:
        conversation_state[user_id] = {'count': 0, 'topics': []}
    
    conversation_state[user_id]['count'] += 1
    count = conversation_state[user_id]['count']
    
    message_lower = user_msg.lower().strip()
    
    # Equipment requests - different responses each time
    if any(word in message_lower for word in ['tractor', 'harvester', 'equipment', 'rent', 'hire']):
        response = get_equipment_response_dynamic(message_lower, count)
        return jsonify({'reply': response})
    
    # Crop problems - varied solutions
    if any(word in message_lower for word in ['yellow', 'disease', 'pest', 'problem', 'dying']):
        response = get_crop_problem_response_dynamic(message_lower, count)
        return jsonify({'reply': response})
    
    # Planting advice - different each time
    if any(word in message_lower for word in ['plant', 'sow', 'seed', 'when to plant']):
        response = get_planting_response_dynamic(message_lower, count)
        return jsonify({'reply': response})
    
    # Harvesting - varied timing advice
    if any(word in message_lower for word in ['harvest', 'when to harvest', 'ready']):
        response = get_harvesting_response_dynamic(message_lower, count)
        return jsonify({'reply': response})
    
    # Fertilizer - different recommendations
    if any(word in message_lower for word in ['fertilizer', 'nutrition', 'urea', 'dap']):
        response = get_fertilizer_response_dynamic(message_lower, count)
        return jsonify({'reply': response})
    
    # Irrigation - varied methods
    if any(word in message_lower for word in ['water', 'irrigation', 'drip', 'sprinkler']):
        response = get_irrigation_response_dynamic(message_lower, count)
        return jsonify({'reply': response})
    
    # Weather/season - different seasonal advice
    if any(word in message_lower for word in ['weather', 'season', 'monsoon', 'winter']):
        response = get_weather_response_dynamic(message_lower, count)
        return jsonify({'reply': response})
    
    # Soil - varied soil advice
    if any(word in message_lower for word in ['soil', 'ph', 'testing', 'preparation']):
        response = get_soil_response_dynamic(message_lower, count)
        return jsonify({'reply': response})
    
    # Pricing - different cost perspectives
    if any(word in message_lower for word in ['price', 'cost', 'expensive', 'cheap']):
        response = get_pricing_response_dynamic(message_lower, count)
        return jsonify({'reply': response})
    
    # Greetings - varied welcomes
    if any(word in message_lower for word in ['hi', 'hello', 'hey', 'namaste']):
        response = get_greeting_response_dynamic(count)
        return jsonify({'reply': response})
    
    # Default varied responses
    response = get_default_response_dynamic(count)
    return jsonify({'reply': response})

def get_equipment_response_dynamic(message, count):
    """Equipment responses that change each time"""
    
    if 'rice' in message:
        responses = [
            "For rice farming, you'll need a rice transplanter (₹800/day) and mini tractor (₹600/day). Which stage are you at?",
            "Rice equipment: Transplanting machine saves labor, combine harvester for efficient harvest. What's your field size?",
            "Rice farming tools: Puddling tractor, transplanter, harvester. Manual vs machine depends on your budget.",
            "Rice cultivation needs: Land preparation tractor, seedling transplanter, threshing machine. Which operation first?"
        ]
    elif 'wheat' in message:
        responses = [
            "Wheat farming: Seed drill (₹500/day) for sowing, combine harvester (₹1000/day) for harvest. What do you need?",
            "For wheat: Tractor for field prep, precision seed drill, harvester. When are you planning to sow?",
            "Wheat equipment: Cultivator for land prep, seed drill for uniform sowing, harvester for clean grain.",
            "Wheat machinery: Deep plowing tractor, seed cum fertilizer drill, combine harvester. Which stage?"
        ]
    elif 'cotton' in message:
        responses = [
            "Cotton farming: Heavy tractor for deep plowing (₹700/day), cotton picker for harvest (₹1500/day).",
            "Cotton equipment: Land preparation tractor, seed drill, cotton harvesting machine. What's your priority?",
            "For cotton: Deep cultivation tractor, precision planter, mechanical cotton picker. Which operation?"
        ]
    elif 'tractor' in message:
        responses = [
            "We have tractors available for rent. Small tractors cost ₹1000/day, large tractors cost ₹2000/day. What size do you need?",
            "Tractor options: Mini tractor (₹800/day) for small farms, heavy tractor (₹1500/day) for large fields. Which suits you?",
            "Tractors available: 35HP (₹1000/day), 50HP (₹1500/day), 75HP (₹2000/day). What's your requirement?",
            "Tractor rental: Compact models for orchards, standard for field work, heavy-duty for deep plowing. Which type?"
        ]
    elif 'harvester' in message:
        responses = [
            "Combine harvesters are available at ₹4000/day. Perfect for wheat, rice, and other grain crops. When do you need it?",
            "Harvester options: Mini harvester (₹3000/day), combine harvester (₹4500/day). Which crop are you harvesting?",
            "Harvesting machines: Self-propelled combine (₹4000/day), tractor-mounted (₹2500/day). What's your preference?",
            "Harvest equipment: Combine harvester for grains, specialized harvesters for different crops. Which do you need?"
        ]
    else:
        responses = [
            "Which crop are you growing? I'll recommend the right equipment with current rental rates.",
            "Tell me your crop and field size - I'll suggest the most suitable equipment options.",
            "Equipment depends on crop type and farming stage. What are you planning to cultivate?",
            "I can help with tractors, harvesters, seeders for any crop. What's your farming plan?"
        ]
    
    return responses[count % len(responses)]

def get_crop_problem_response_dynamic(message, count):
    """Crop problem responses with different solutions"""
    
    if 'yellow' in message:
        if 'rice' in message:
            responses = [
                "Rice yellowing = nitrogen deficiency. Apply 25kg urea/acre immediately. Check drainage too.",
                "Yellow rice leaves indicate nutrient shortage. Use urea and ensure proper water management.",
                "Rice turning yellow? Usually nitrogen deficiency or waterlogging. Apply fertilizer and improve drainage.",
                "Rice yellowing suggests nitrogen lack or poor drainage. Apply urea 25kg/acre, check field water level."
            ]
        elif 'wheat' in message:
            responses = [
                "Wheat yellowing = rust disease or nutrients. Spray Propiconazole, apply DAP 50kg/acre.",
                "Yellow wheat suggests rust or deficiency. Use fungicide spray and phosphorus fertilizer.",
                "Wheat turning yellow? Could be rust disease or nutrient deficiency. Spray fungicide, add fertilizer."
            ]
        else:
            responses = [
                "Yellowing usually means nitrogen deficiency. Which crop? I'll give specific treatment.",
                "Yellow leaves indicate nutrient issues or disease. Tell me the crop for exact solution.",
                "Yellowing can be nutrients, disease, or water stress. What crop are we dealing with?"
            ]
    elif 'pest' in message:
        responses = [
            "Pest control: Start with neem oil 5ml/liter. Which crop and what pests are you seeing?",
            "For pests: Use integrated approach - neem oil, pheromone traps. What's the crop?",
            "Pest management: Identify pest first, then targeted treatment. Which crop is affected?",
            "Pest issues: Neem spray, beneficial insects, pheromone traps work well. What pests do you see?"
        ]
    else:
        responses = [
            "Describe the problem: yellowing, spots, wilting? I'll diagnose and suggest treatment.",
            "What symptoms are you seeing? I can identify the issue and recommend solutions.",
            "Tell me the crop and symptoms - I'll help identify and treat the problem."
        ]
    
    return responses[count % len(responses)]

def get_planting_response_dynamic(message, count):
    """Planting advice with seasonal variations"""
    
    if 'rice' in message:
        responses = [
            "Rice planting: June-July with monsoon. 20-25kg seeds/acre, maintain 2-3 inches water.",
            "Rice sowing: Nursery in May-June, transplant after 25 days. Keep standing water.",
            "Rice timing: Plant with first monsoon rains. Use 20kg seeds/acre for transplanting.",
            "Rice cultivation: Start nursery before monsoon, transplant in flooded fields after 3-4 weeks."
        ]
    elif 'wheat' in message:
        responses = [
            "Wheat sowing: November-December. 40-50kg seeds/acre, 2-3cm depth, 20cm rows.",
            "Wheat planting: After rice harvest, November ideal. Ensure soil moisture before sowing.",
            "Wheat timing: Late November to early December. Use seed drill for uniform spacing.",
            "Wheat cultivation: Sow after Diwali, 45kg seeds/acre, maintain proper row spacing."
        ]
    else:
        responses = [
            "Which crop are you planting? I'll give specific timing, seed rate, and techniques.",
            "Planting advice depends on crop and season. What are you planning to grow?",
            "Tell me the crop - I'll provide sowing time, seed rate, and best practices."
        ]
    
    return responses[count % len(responses)]

def get_harvesting_response_dynamic(message, count):
    """Harvesting guidance with different timing tips"""
    
    if 'rice' in message:
        responses = [
            "Rice harvest: 120-150 days when grains turn golden. Cut at 20-25% moisture.",
            "Rice ready when panicles bend down, grains firm. Use combine harvester for efficiency.",
            "Rice harvesting: Check grain hardness, golden color. Early morning cutting reduces loss.",
            "Rice maturity: Grains turn golden, panicles heavy. Harvest at proper moisture for quality."
        ]
    elif 'wheat' in message:
        responses = [
            "Wheat harvest: 120-130 days when grains hard. Best at 12-14% moisture.",
            "Wheat ready when ears golden, grains firm. Harvest in cool morning hours.",
            "Wheat maturity: Golden color, hard grains. Cut early morning to avoid shattering."
        ]
    else:
        responses = [
            "Which crop are you harvesting? I'll tell you exact timing and best methods.",
            "Harvest timing varies by crop. Tell me what you're growing for specific advice.",
            "Different crops have different harvest signs. What crop needs harvesting guidance?"
        ]
    
    return responses[count % len(responses)]

def get_fertilizer_response_dynamic(message, count):
    """Fertilizer advice with different nutrient focus"""
    
    responses = [
        "Fertilizer needs: NPK 120:60:40 kg/acre for most crops. Which crop needs advice?",
        "Balanced nutrition: Urea for nitrogen, DAP for phosphorus. Apply in splits. What crop?",
        "Fertilizer timing: Basal dose at planting, top dressing during growth. Which crop?",
        "Nutrient management: Soil test first, then balanced NPK application. What's your crop?"
    ]
    return responses[count % len(responses)]

def get_irrigation_response_dynamic(message, count):
    """Irrigation advice with method comparisons"""
    
    if 'drip' in message:
        responses = [
            "Drip irrigation: Saves 40% water, costs ₹50,000/acre. Best for vegetables, fruits.",
            "Drip system: High initial cost but water-efficient. Suitable for high-value crops.",
            "Drip irrigation: Precise water application, reduces weeds. Good for water-scarce areas."
        ]
    else:
        responses = [
            "Irrigation methods: Drip (water-saving), sprinkler (field crops), flood (rice). Which interests you?",
            "Water management: Early morning/evening irrigation. Check soil moisture at 6-inch depth.",
            "Irrigation timing: Water when soil feels dry at finger depth. Avoid midday watering.",
            "Water application: Deep, less frequent watering better than shallow, frequent watering."
        ]
    return responses[count % len(responses)]

def get_weather_response_dynamic(message, count):
    """Weather and seasonal advice variations"""
    
    responses = [
        "Seasonal crops: Kharif (June-Oct) rice/cotton, Rabi (Nov-Apr) wheat/mustard. What season?",
        "Weather planning: Monsoon crops need drainage, winter crops need irrigation. Which season?",
        "Crop calendar: Summer prep, monsoon planting, winter sowing, spring harvest. What's your plan?",
        "Season planning: Kharif with rains, Rabi with irrigation, Zaid with intensive care. Which season?"
    ]
    return responses[count % len(responses)]

def get_soil_response_dynamic(message, count):
    """Soil management with different focus areas"""
    
    responses = [
        "Soil health: Test pH every 2 years (ideal 6.0-7.5). Add organic matter 2-3 tons/acre.",
        "Soil preparation: Deep plowing before monsoon, add compost, check nutrient levels.",
        "Soil management: pH testing, organic matter, proper drainage. What's your soil type?",
        "Soil improvement: Regular testing, organic inputs, crop rotation. What's your main concern?"
    ]
    return responses[count % len(responses)]

def get_pricing_response_dynamic(message, count):
    """Pricing with different cost perspectives"""
    
    responses = [
        "Equipment rates: Mini tractor ₹500-700/day, Harvester ₹1000-1500/day. Varies by location.",
        "Rental costs: Tractor ₹600/day, Seed drill ₹400/day, Sprayer ₹300/day. What equipment?",
        "Pricing factors: Equipment type, duration, location, season. Which equipment interests you?",
        "Cost comparison: Buying vs renting depends on usage frequency. What's your requirement?"
    ]
    return responses[count % len(responses)]

def get_greeting_response_dynamic(count):
    """Varied greeting responses"""
    
    responses = [
        "Hello! What farming challenge can I help you solve today?",
        "Hi there! Ready to assist with your agricultural needs.",
        "Namaste! I'm your farming expert - what's on your mind?",
        "Good to see you! What crop or equipment question do you have?",
        "Welcome! How can I help with your farming today?",
        "Hello farmer! What agricultural advice do you need?"
    ]
    return responses[count % len(responses)]

def get_default_response_dynamic(count):
    """Default responses with variety"""
    
    responses = [
        "I can help with any farming question! What specific challenge are you facing?",
        "Tell me about your farming situation - crop type, land size, or current issue?",
        "What would you like to know? I cover equipment, crops, diseases, planting, and more.",
        "I'm here for all your agricultural needs. What's your main concern right now?",
        "Ask me anything about farming - I'm here to help with practical solutions!",
        "What farming topic interests you? Equipment, crops, problems, or techniques?"
    ]
    return responses[count % len(responses)]

def create_translations_table():
    """Create equipment_translations table if it doesn't exist"""
    conn = get_db_connection()
    
    # Check if table exists
    table_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='equipment_translations'"
    ).fetchone()
    
    if not table_exists:
        print("Creating equipment_translations table...")
        
        # Create equipment_translations table
        conn.execute('''
            CREATE TABLE equipment_translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER NOT NULL,
                language_code VARCHAR(5) NOT NULL,
                translated_name VARCHAR(200) NOT NULL,
                translated_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (equipment_id) REFERENCES equipment (id) ON DELETE CASCADE,
                UNIQUE(equipment_id, language_code)
            )
        ''')
        
        # Insert sample translations
        sample_translations = [
            # Kannada translations
            ('Tractor', 'kn', 'ಟ್ರಾಕ್ಟರ್', 'ಕೃಷಿ ಕಾರ್ಯಗಳಿಗೆ ಬಳಸುವ ವಾಹನ'),
            ('Bulldozer', 'kn', 'ಬುಲ್ಡೋಜರ್', 'ಮಣ್ಣು ಸಾಗಿಸುವ ಭಾರೀ ಯಂತ್ರ'),
            ('Solar Inverter', 'kn', 'ಸೌರ ಇನ್ವೆರ್ಟರ್', 'ಸೌರ ಶಕ್ತಿ ಪರಿವರ್ತಕ ಸಾಧನ'),
            ('Harvester', 'kn', 'ಕೊಯ್ಲುಗಾರ ಯಂತ್ರ', 'ಬೆಳೆ ಕೊಯ್ಲು ಮಾಡುವ ಯಂತ್ರ'),
            ('Bio Gas Plant', 'kn', 'ಬಯೋ ಗ್ಯಾಸ್ ಘಟಕ', 'ನವೀಕರಿಸಬಹುದಾದ ಇಂಧನ ಉತ್ಪಾದನಾ ವ್ಯವಸ್ಥೆ'),
            
            # Telugu translations
            ('Tractor', 'te', 'ట్రాక్టర్', 'వ్యవసాయ కార్యకలాపాలకు వాహనం'),
            ('Bulldozer', 'te', 'బుల్డోజర్', 'మట్టి తవ్వే భారీ యంత్రం'),
            ('Solar Inverter', 'te', 'సౌర ఇన్వర్టర్', 'సౌర శక్తి మార్చే పరికరం'),
            ('Harvester', 'te', 'హార్వెస్టర్', 'పంట కోత యంత్రం'),
            ('Bio Gas Plant', 'te', 'బయో గ్యాస్ ప్లాంట్', 'పునరుత్పాదక ఇంధన వ్యవస్థ'),
            
            # Hindi translations
            ('Tractor', 'hi', 'ट्रैक्टर', 'कृषि कार्यों के लिए वाहन'),
            ('Bulldozer', 'hi', 'बुलडोजर', 'मिट्टी खोदने की भारी मशीन'),
            ('Solar Inverter', 'hi', 'सोलर इन्वर्टर', 'सौर ऊर्जा परिवर्तक उपकरण'),
            ('Harvester', 'hi', 'हार्वेस्टर', 'फसल काटने की मशीन'),
            ('Bio Gas Plant', 'hi', 'बायो गैस प्लांट', 'नवीकरणीय ऊर्जा उत्पादन प्रणाली')
        ]
        
        # Insert translations for existing equipment
        for eq_name, lang, trans_name, trans_desc in sample_translations:
            # Find equipment by name
            equipment = conn.execute('SELECT id FROM equipment WHERE name = ?', (eq_name,)).fetchone()
            if equipment:
                conn.execute('''
                    INSERT OR REPLACE INTO equipment_translations 
                    (equipment_id, language_code, translated_name, translated_description)
                    VALUES (?, ?, ?, ?)
                ''', (equipment['id'], lang, trans_name, trans_desc))
        
        conn.commit()
        print("Equipment translations table created and populated!")
    
    conn.close()

def ensure_payment_tables():
    """Auto-create payment tables and columns if missing"""
    conn = sqlite3.connect('krushi_rent_ai.db')
    cursor = conn.cursor()
    
    try:
        # Create payments table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                payment_status TEXT DEFAULT 'PENDING',
                transaction_id TEXT,
                upi_id TEXT,
                card_number TEXT,
                card_name TEXT,
                card_expiry TEXT,
                card_cvv TEXT,
                cod_address TEXT,
                cod_mobile TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add payment columns to bookings table if missing
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'payment_status' not in columns:
            cursor.execute('ALTER TABLE bookings ADD COLUMN payment_status TEXT DEFAULT "PENDING"')
            print("Added payment_status column to bookings")
            
        if 'payment_id' not in columns:
            cursor.execute('ALTER TABLE bookings ADD COLUMN payment_id INTEGER')
            print("Added payment_id column to bookings")
        
        conn.commit()
        print("Payment tables verified/created successfully")
        
    except Exception as e:
        print(f"Error setting up payment tables: {e}")
    finally:
        conn.close()

def migrate_database():
    """Handle database migrations for missing columns"""
    conn = None
    try:
        conn = sqlite3.connect('krushi_rent_ai.db', timeout=30.0)
        cursor = conn.cursor()
        
        # Check if payment_status column exists in payments table
        cursor.execute("PRAGMA table_info(payments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'payment_status' not in columns:
            print("Adding missing payment_status column...")
            cursor.execute('ALTER TABLE payments ADD COLUMN payment_status TEXT DEFAULT "PENDING"')
            conn.commit()
            print("payment_status column added successfully")
        else:
            print("payment_status column already exists")
            
    except sqlite3.OperationalError as e:
        print(f"Migration error: {e}")
        # If payments table doesn't exist, it will be created by init_database
        pass
    finally:
        if conn:
            conn.close()

def init_database():
    conn = None
    try:
        conn = sqlite3.connect('krushi_rent_ai.db', timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                user_type TEXT NOT NULL,
                phone TEXT,
                location TEXT,
                farm_size TEXT,
                crops TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                price_per_hour REAL NOT NULL,
                price_per_day REAL NOT NULL,
                location TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                available BOOLEAN DEFAULT 1,
                description TEXT,
                image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id TEXT UNIQUE NOT NULL,
                equipment_id INTEGER NOT NULL,
                farmer_id INTEGER NOT NULL,
                booking_date TEXT NOT NULL,
                duration_hours INTEGER NOT NULL,
                delivery_address TEXT,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'CONFIRMED',
                payment_status TEXT DEFAULT 'PENDING',
                payment_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (equipment_id) REFERENCES equipment (id),
                FOREIGN KEY (farmer_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                payment_status TEXT DEFAULT 'PENDING',
                upi_id TEXT,
                card_number TEXT,
                card_name TEXT,
                card_expiry TEXT,
                card_cvv TEXT,
                cod_address TEXT,
                cod_mobile TEXT,
                transaction_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (booking_id) REFERENCES bookings (booking_id)
            )
        ''')
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, name, user_type)
            VALUES ('admin', 'admin123', 'System Administrator', 'admin')
        ''')
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, name, user_type, phone, location)
            VALUES ('owner1', 'owner123', 'Equipment Owner', 'owner', '9876543210', 'Hyderabad')
        ''')
        
        cursor.execute('''
            INSERT OR IGNORE INTO equipment (name, type, price_per_hour, price_per_day, location, owner_id, description)
            VALUES 
            ('Heavy Duty Tractor', 'Tractor', 150, 1200, 'Hyderabad', 2, 'Powerful tractor for heavy farming work'),
            ('Combine Harvester', 'Harvester', 200, 1600, 'Hyderabad', 2, 'Efficient harvesting machine'),
            ('Seed Drill Machine', 'Seeder', 80, 640, 'Hyderabad', 2, 'Precision seeding equipment')
        ''')
        
        conn.commit()
    finally:
        if conn:
            conn.close()

def get_db_connection():
    conn = sqlite3.connect('krushi_rent_ai.db', timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def get_user(username, user_type=None):
    conn = get_db_connection()
    if user_type:
        user = conn.execute('SELECT * FROM users WHERE username = ? AND user_type = ?', (username, user_type)).fetchone()
    else:
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def create_user(username, password, name, user_type, phone='', location='', farm_size='', crops=''):
    conn = get_db_connection()
    try:
        conn.execute('''INSERT INTO users (username, password, name, user_type, phone, location, farm_size, crops) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (username, password, name, user_type, phone, location, farm_size, crops))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

@app.route('/')
def index():
    user_lang = get_user_language()
    text = INDEX_TRANSLATIONS.get(user_lang, INDEX_TRANSLATIONS['en'])
    return render_template('index.html', text=text, current_lang=user_lang)

@app.route('/login/<user_type>')
def login(user_type):
    if user_type not in ['farmer', 'owner', 'admin']:
        return redirect(url_for('index'))
    
    # Sync language from localStorage if available
    user_lang = get_user_language()
    print(f"[LOGIN] Current language: {user_lang}")
    
    text = INDEX_TRANSLATIONS.get(user_lang, INDEX_TRANSLATIONS['en'])
    return render_template('login.html', user_type=user_type, current_lang=user_lang, text=text)

@app.route('/register/<user_type>')
def register(user_type):
    if user_type not in ['farmer', 'owner']:
        return redirect(url_for('index'))
    user_lang = get_user_language()
    text = INDEX_TRANSLATIONS.get(user_lang, INDEX_TRANSLATIONS['en'])
    return render_template('register.html', user_type=user_type, current_lang=user_lang, text=text)

@app.route('/auth', methods=['POST'])
def authenticate():
    user_type = request.form['user_type']
    action = request.form['action']
    username = request.form['username']
    password = request.form['password']
    
    if action == 'login':
        user = get_user(username, user_type)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = username
            session['user_type'] = user_type
            session['user_name'] = user['name']
            return redirect(url_for(f'{user_type}_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
            return redirect(url_for('login', user_type=user_type))
    
    elif action == 'register':
        name = request.form['name']
        phone = request.form.get('phone', '')
        location = request.form.get('location', '')
        address = request.form.get('address', '')
        farm_size = request.form.get('farm_size', '')
        crops = request.form.get('crops', '')
        
        if create_user(username, password, name, user_type, phone, location, farm_size, crops):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login', user_type=user_type))
        else:
            flash('Username already exists!', 'error')
            return redirect(url_for('register', user_type=user_type))

@app.route('/farmer_dashboard')
def farmer_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return redirect(url_for('index'))
    
    user_lang = get_user_language()
    text = DASHBOARD_TRANSLATIONS.get(user_lang, DASHBOARD_TRANSLATIONS['en'])
    
    conn = get_db_connection()
    
    try:
        # Check if equipment_translations table exists
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='equipment_translations'"
        ).fetchone()
        
        if table_exists:
            bookings = conn.execute('''
                SELECT b.*, e.name as equipment_name, e.type as equipment_type,
                       et.translated_name as equipment_name_local
                FROM bookings b 
                JOIN equipment e ON b.equipment_id = e.id 
                LEFT JOIN equipment_translations et ON e.id = et.equipment_id AND et.language_code = ?
                WHERE b.farmer_id = ? 
                ORDER BY b.created_at DESC LIMIT 5
            ''', (user_lang, session['user_id'])).fetchall()
        else:
            print(f"[DB_WARNING] equipment_translations table missing, using fallback query")
            bookings = conn.execute('''
                SELECT b.*, e.name as equipment_name, e.type as equipment_type,
                       NULL as equipment_name_local
                FROM bookings b 
                JOIN equipment e ON b.equipment_id = e.id 
                WHERE b.farmer_id = ? 
                ORDER BY b.created_at DESC LIMIT 5
            ''', (session['user_id'],)).fetchall()
    
    except Exception as e:
        print(f"[DB_ERROR] Database error in farmer_dashboard: {e}")
        # Emergency fallback
        bookings = conn.execute('''
            SELECT b.*, e.name as equipment_name, e.type as equipment_type,
                   NULL as equipment_name_local
            FROM bookings b 
            JOIN equipment e ON b.equipment_id = e.id 
            WHERE b.farmer_id = ? 
            ORDER BY b.created_at DESC LIMIT 5
        ''', (session['user_id'],)).fetchall()
    
    # Process bookings to add display names with safe Unicode handling
    processed_bookings = []
    for booking in bookings:
        try:
            booking_dict = dict(booking)
            name_en = str(booking_dict['equipment_name'] or '')
            name_local = booking_dict.get('equipment_name_local')
            
            # Safe Unicode handling
            if name_local:
                try:
                    # Decode if it's escaped Unicode
                    name_local = decode_unicode_string(str(name_local))
                    if name_local and name_local != name_en:
                        booking_dict['equipment_display_name'] = f"{name_en} ({name_local})"
                    else:
                        booking_dict['equipment_display_name'] = name_en
                except Exception as unicode_error:
                    print(f"Unicode error for {name_local}: {unicode_error}")
                    booking_dict['equipment_display_name'] = name_en
            else:
                booking_dict['equipment_display_name'] = name_en
                
            processed_bookings.append(booking_dict)
            print(f"Booking equipment: {name_en} -> {booking_dict['equipment_display_name']}")
            
        except Exception as booking_error:
            print(f"Error processing booking: {booking_error}")
            # Add booking with minimal data to prevent crashes
            processed_bookings.append({
                'equipment_display_name': 'Equipment',
                'booking_date': dict(booking).get('booking_date', ''),
                'total_amount': dict(booking).get('total_amount', 0)
            })
    
    conn.close()
    
    return render_template('farmer_dashboard.html', bookings=processed_bookings, current_lang=user_lang, text=text)

@app.route('/owner_dashboard')
def owner_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('index'))
    
    user_lang = get_user_language()
    
    conn = get_db_connection()
    equipment = conn.execute('SELECT * FROM equipment WHERE owner_id = ? ORDER BY created_at DESC',
                           (session['user_id'],)).fetchall()
    
    bookings = conn.execute('''
        SELECT b.*, e.name as equipment_name, u.name as farmer_name 
        FROM bookings b 
        JOIN equipment e ON b.equipment_id = e.id 
        JOIN users u ON b.farmer_id = u.id 
        WHERE e.owner_id = ? ORDER BY b.created_at DESC LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    total_earnings = conn.execute('''
        SELECT COALESCE(SUM(b.total_amount), 0) as total 
        FROM bookings b 
        JOIN equipment e ON b.equipment_id = e.id 
        WHERE e.owner_id = ? AND b.status = 'CONFIRMED'
    ''', (session['user_id'],)).fetchone()['total']
    
    conn.close()
    
    import json, os
    try:
        with open(os.path.join('static', 'translations', f'{user_lang}.json'), 'r', encoding='utf-8') as f:
            text = json.load(f)
    except:
        text = {}
    
    return render_template('owner_dashboard.html', 
                         equipment=equipment, 
                         bookings=bookings, 
                         total_earnings=total_earnings,
                         current_lang=user_lang,
                         text=text)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    user_lang = get_user_language()
    
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    equipment = conn.execute('SELECT * FROM equipment ORDER BY created_at DESC').fetchall()
    bookings = conn.execute('SELECT * FROM bookings ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', users=users, equipment=equipment, bookings=bookings, current_lang=user_lang)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/set_language', methods=['POST'])
def set_language():
    """Set user's preferred language"""
    data = request.get_json()
    lang = data.get('language', 'en')
    session['user_language'] = lang
    print(f"Language set to: {lang}")
    return jsonify({'success': True, 'language': lang})

@app.route('/set_language/<lang>')
def set_language_get(lang):
    """Set language via GET request and redirect back"""
    if lang in ['en', 'te', 'hi', 'kn', 'ta']:
        session['user_language'] = lang
    return redirect(request.referrer or url_for('farmer_dashboard'))

def get_user_language():
    """Get user's preferred language from session"""
    return session.get('user_language', 'en')

@app.route('/get_ai_recommendations', methods=['POST'])
def get_ai_recommendations():
    """Get AI-powered equipment recommendations based on form data"""
    print("\n=== GET_AI_RECOMMENDATIONS ROUTE HIT ===")
    
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        print("[AI_RECS] Unauthorized access attempt")
        return jsonify({'error': 'Unauthorized', 'success': False}), 401
    
    try:
        data = request.get_json()
        print(f"[AI_RECS] Received data: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data received',
                'data': []
            }), 400
        
        farming_stage = data.get('farming_stage')
        crop_category = data.get('crop_category')
        farm_size = data.get('farm_size')
        season = data.get('season')
        budget_range = data.get('budget_range')
        urgency = data.get('urgency')
        
        print(f"[AI_RECS] Parameters: stage={farming_stage}, crop={crop_category}, size={farm_size}")
        
        # Validate required parameters
        if not all([farming_stage, crop_category, farm_size]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: farming_stage, crop_category, farm_size',
                'data': []
            }), 400
        
        # Generate AI recommendations based on parameters
        recommendations = generate_equipment_recommendations(
            farming_stage, crop_category, farm_size, season, budget_range, urgency
        )
        
        print(f"[AI_RECS] Generated {len(recommendations)} recommendations")
        
        if recommendations:
            return jsonify({
                'success': True,
                'data': recommendations,
                'message': f'Found {len(recommendations)} AI-recommended equipment for {crop_category} {farming_stage}',
                'count': len(recommendations)
            })
        else:
            return jsonify({
                'success': True,
                'data': [],
                'message': 'No equipment available for your specific requirements. Try adjusting your criteria.',
                'count': 0
            })
            
    except Exception as e:
        print(f"[AI_RECS] Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'AI recommendation system error: {str(e)}',
            'data': []
        }), 500

def generate_equipment_recommendations(farming_stage, crop_category, farm_size, season, budget_range, urgency):
    """Generate intelligent equipment recommendations"""
    print(f"[AI_ENGINE] Generating recommendations for {crop_category} {farming_stage}")
    
    try:
        conn = get_db_connection()
        
        # Equipment mapping based on farming stage and crop
        stage_equipment_map = {
            'land_preparation': ['Tractor', 'Cultivator', 'Bulldozer'],
            'sowing': ['Seeder', 'Seed Drill Machine', 'Tractor'],
            'irrigation': ['Sprayer', 'Irrigation'],
            'maintenance': ['Sprayer', 'Cultivator', 'Weeder'],
            'harvesting': ['Harvester', 'Combine Harvester', 'Thresher'],
            'post_harvest': ['Thresher', 'Dryer']
        }
        
        # Get relevant equipment types
        equipment_types = stage_equipment_map.get(farming_stage, ['Tractor'])
        print(f"[AI_ENGINE] Looking for equipment types: {equipment_types}")
        
        # Check if equipment_translations table exists
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='equipment_translations'"
        ).fetchone()
        
        if table_exists:
            # Build query with equipment type filter and translations
            type_conditions = ' OR '.join(['e.type LIKE ?' for _ in equipment_types])
            name_conditions = ' OR '.join(['e.name LIKE ?' for _ in equipment_types])
            
            query = f'''
                SELECT e.*, u.name as owner_name, et.translated_name
                FROM equipment e 
                JOIN users u ON e.owner_id = u.id 
                LEFT JOIN equipment_translations et ON e.id = et.equipment_id AND et.language_code = 'en'
                WHERE e.available = 1 AND u.user_type = 'owner'
                AND (({type_conditions}) OR ({name_conditions}))
                ORDER BY e.price_per_day ASC
                LIMIT 10
            '''
        else:
            print(f"[AI_ENGINE] equipment_translations table missing, using fallback query")
            # Fallback query without translations
            type_conditions = ' OR '.join(['e.type LIKE ?' for _ in equipment_types])
            name_conditions = ' OR '.join(['e.name LIKE ?' for _ in equipment_types])
            
            query = f'''
                SELECT e.*, u.name as owner_name, NULL as translated_name
                FROM equipment e 
                JOIN users u ON e.owner_id = u.id 
                WHERE e.available = 1 AND u.user_type = 'owner'
                AND (({type_conditions}) OR ({name_conditions}))
                ORDER BY e.price_per_day ASC
                LIMIT 10
            '''
        
        # Prepare parameters for query
        params = []
        for eq_type in equipment_types:
            params.append(f'%{eq_type}%')
        for eq_type in equipment_types:
            params.append(f'%{eq_type}%')
        
        print(f"[AI_ENGINE] Query: {query}")
        print(f"[AI_ENGINE] Params: {params}")
        
        equipment_list = conn.execute(query, params).fetchall()
        print(f"[AI_ENGINE] Found {len(equipment_list)} equipment items")
        
        recommendations = []
        for i, eq in enumerate(equipment_list):
            try:
                # Convert Row to dict for safe access
                eq_dict = dict(eq)
                
                # Calculate AI match score
                score = calculate_match_score(eq, farming_stage, crop_category, farm_size, budget_range)
                
                # Generate match reason
                match_reason = generate_match_reason(eq, farming_stage, crop_category, farm_size)
                
                recommendation = {
                    'id': eq_dict['id'],
                    'name': eq_dict['name'],
                    'name_en': eq_dict['name'],
                    'name_local': eq_dict.get('translated_name', ''),
                    'type': eq_dict['type'],
                    'price_per_hour': eq_dict['price_per_hour'],
                    'price_per_day': eq_dict['price_per_day'],
                    'location': eq_dict['location'],
                    'owner_name': eq_dict['owner_name'],
                    'image_url': f"/static/uploads/{eq_dict['image']}" if eq_dict.get('image') else '/static/images/default.png',
                    'match_score': score,
                    'match_reason': match_reason,
                    'ai_confidence': 'High' if i == 0 else 'Medium' if i == 1 else 'Good',
                    'user_lang': get_user_language()
                }
                recommendations.append(recommendation)
                
            except Exception as e:
                print(f"[AI_ENGINE] Error processing equipment {i}: {e}")
                continue
        
        conn.close()
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        print(f"[AI_ENGINE] Returning {len(recommendations)} recommendations")
        return recommendations
        
    except Exception as e:
        print(f"[AI_ENGINE] Critical error in generate_equipment_recommendations: {e}")
        return []

def calculate_match_score(equipment, farming_stage, crop_category, farm_size, budget_range):
    """Calculate AI match score for equipment"""
    score = 70  # Base score
    
    # Convert Row to dict for safe access
    eq_dict = dict(equipment)
    
    # Stage-specific scoring
    if farming_stage == 'land_preparation' and 'Tractor' in eq_dict['name']:
        score += 20
    elif farming_stage == 'harvesting' and 'Harvester' in eq_dict['name']:
        score += 25
    elif farming_stage == 'sowing' and 'Seed' in eq_dict['name']:
        score += 20
    
    # Farm size scoring
    if farm_size == 'small' and eq_dict['price_per_day'] < 1500:
        score += 15
    elif farm_size == 'large' and eq_dict['price_per_day'] > 2000:
        score += 15
    elif farm_size == 'medium':
        score += 10
    
    # Budget scoring
    if budget_range == 'low' and eq_dict['price_per_day'] < 1500:
        score += 10
    elif budget_range == 'high' and eq_dict['price_per_day'] > 3000:
        score += 10
    elif budget_range == 'medium':
        score += 5
    
    return min(score, 100)

def generate_match_reason(equipment, farming_stage, crop_category, farm_size):
    """Generate human-readable match reason"""
    reasons = []
    
    # Convert Row to dict for safe access
    eq_dict = dict(equipment)
    
    if farming_stage == 'land_preparation':
        reasons.append("Perfect for soil preparation")
    elif farming_stage == 'harvesting':
        reasons.append("Ideal for efficient harvesting")
    elif farming_stage == 'sowing':
        reasons.append("Excellent for precise seeding")
    
    if farm_size == 'small':
        reasons.append("suitable for small farms")
    elif farm_size == 'large':
        reasons.append("designed for large-scale operations")
    else:
        reasons.append("perfect for medium farms")
    
    if eq_dict['price_per_day'] < 1500:
        reasons.append("budget-friendly option")
    elif eq_dict['price_per_day'] > 3000:
        reasons.append("premium equipment")
    
    return ", ".join(reasons).capitalize()

@app.route('/book_equipment', methods=['POST'])
def book_equipment():
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    equipment_id = data.get('equipment_id')
    booking_date = data.get('booking_date')
    duration_hours = int(data.get('duration_hours', 8))
    delivery_address = data.get('delivery_address', '')
    
    conn = get_db_connection()
    
    # Get equipment details
    equipment = conn.execute(
        'SELECT * FROM equipment WHERE id = ?', (equipment_id,)
    ).fetchone()
    
    if not equipment:
        conn.close()
        return jsonify({'error': 'Equipment not found'}), 404
    
    # Calculate total amount
    total_amount = equipment['price_per_hour'] * duration_hours
    booking_id = str(uuid.uuid4())[:8].upper()
    
    # Create booking with delivery address
    conn.execute('''
        INSERT INTO bookings (booking_id, equipment_id, farmer_id, booking_date, duration_hours, delivery_address, total_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (booking_id, equipment_id, session['user_id'], booking_date, duration_hours, delivery_address, total_amount))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'booking_id': booking_id,
        'redirect_url': url_for('payment_page', booking_id=booking_id)
    })

@app.route('/payment/<booking_id>')
def payment_page(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get booking details with equipment info
    booking = conn.execute('''
        SELECT b.*, e.name as equipment_name, e.location
        FROM bookings b
        JOIN equipment e ON b.equipment_id = e.id
        WHERE b.booking_id = ? AND b.farmer_id = ?
    ''', (booking_id, session['user_id'])).fetchone()
    
    conn.close()
    
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('farmer_dashboard'))
    
    user_lang = get_user_language()
    print(f"[PAYMENT] User language: {user_lang}")
    
    # Load payment translations - FLAT structure
    import json
    import os
    translation_path = os.path.join('static', 'translations', f'{user_lang}.json')
    text = {}
    try:
        with open(translation_path, 'r', encoding='utf-8') as f:
            text = json.load(f)  # Load entire flat JSON
            print(f"[PAYMENT] Loaded {len(text)} translation keys")
    except Exception as e:
        print(f"[PAYMENT] Error: {e}")
        text = {
            'payment_title': 'Payment Details',
            'booking_summary': 'Booking Summary',
            'equipment': 'Equipment',
            'booking_id': 'Booking ID',
            'date': 'Date',
            'location': 'Location',
            'duration': 'Duration',
            'total': 'Total',
            'select_payment': 'Select Payment Method',
            'upi': 'UPI Payment',
            'upi_desc': 'Pay using UPI ID',
            'card': 'Debit/Credit Card',
            'card_desc': 'Pay using card',
            'cod': 'Cash on Delivery',
            'cod_desc': 'Pay when equipment arrives',
            'pay_now': 'Pay Now'
        }
    
    return render_template('payment.html', booking=dict(booking), current_lang=user_lang, text=text)

@app.route('/payment/<booking_id>', methods=['POST'])
def process_payment(booking_id):
    """Process payment with error handling for missing tables/columns"""
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return redirect(url_for('index'))
    
    try:
        payment_method = request.form.get('payment_method')
        conn = get_db_connection()
        
        # Get booking details
        booking = conn.execute(
            'SELECT * FROM bookings WHERE booking_id = ? AND farmer_id = ?',
            (booking_id, session['user_id'])
        ).fetchone()
        
        if not booking:
            conn.close()
            return redirect(url_for('farmer_dashboard'))
        
        amount = booking['total_amount']
        payment_status = 'FAILED'
        transaction_id = str(uuid.uuid4())[:12].upper()
        
        # Payment validation logic
        if payment_method == 'UPI':
            upi_id = request.form.get('upi_id', '').strip()
            if upi_id:
                payment_status = 'SUCCESS'
            else:
                payment_status = 'FAILED'
        elif payment_method == 'CARD':
            card_number = request.form.get('card_number', '').strip()
            card_name = request.form.get('card_name', '').strip()
            card_cvv = request.form.get('card_cvv', '').strip()
            card_expiry = request.form.get('card_expiry', '').strip()
            if card_number and card_name and card_cvv and card_expiry:
                payment_status = 'SUCCESS'
            else:
                payment_status = 'FAILED'
        elif payment_method == 'COD':
            cod_address = request.form.get('cod_address', '').strip()
            cod_mobile = request.form.get('cod_mobile', '').strip()
            if cod_address and cod_mobile:
                payment_status = 'PENDING'
            elif cod_address or cod_mobile:
                payment_status = 'PENDING'
            else:
                payment_status = 'PENDING'
        
        # Insert payment record with error handling
        try:
            cursor = conn.execute('''
                INSERT INTO payments (booking_id, payment_method, amount, payment_status, transaction_id, upi_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (booking_id, payment_method, amount, payment_status, transaction_id, request.form.get('upi_id')))
            payment_id = cursor.lastrowid
        except sqlite3.OperationalError:
            # Fallback: create table and retry
            ensure_payment_tables()
            cursor = conn.execute('''
                INSERT INTO payments (booking_id, payment_method, amount, payment_status, transaction_id, upi_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (booking_id, payment_method, amount, payment_status, transaction_id, request.form.get('upi_id')))
            payment_id = cursor.lastrowid
        
        # Update booking with payment info
        try:
            conn.execute('UPDATE bookings SET payment_status = ?, payment_id = ? WHERE booking_id = ?',
                        (payment_status, payment_id, booking_id))
        except sqlite3.OperationalError:
            # Columns missing, add them and retry
            ensure_payment_tables()
            conn.execute('UPDATE bookings SET payment_status = ?, payment_id = ? WHERE booking_id = ?',
                        (payment_status, payment_id, booking_id))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('payment_status', 
                              booking_id=booking_id, 
                              status=payment_status.lower(),
                              transaction_id=transaction_id,
                              amount=amount))
                              
    except Exception as e:
        print(f"Payment error: {e}")
        # Generate real values even on error
        real_transaction_id = str(uuid.uuid4())[:12].upper()
        real_amount = 1000  # Default amount
        
        return redirect(url_for('payment_status', 
                              booking_id=booking_id, 
                              status='failed',
                              transaction_id=real_transaction_id,
                              amount=real_amount))

@app.route('/payment/status/<booking_id>')
def payment_status(booking_id):
    status = request.args.get('status', 'failed')
    transaction_id = request.args.get('transaction_id')
    amount = request.args.get('amount')
    message = request.args.get('message')
    
    return render_template('payment_status.html',
                         booking_id=booking_id,
                         status=status,
                         transaction_id=transaction_id,
                         amount=amount,
                         message=message)

@app.route('/receipt/<booking_id>')
def receipt(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get booking, payment, and equipment details
    booking_data = conn.execute('''
        SELECT b.*, e.name as equipment_name, e.type as equipment_type,
               u.name as farmer_name, u.phone as farmer_phone,
               p.payment_method, p.transaction_id, p.payment_status, p.created_at as payment_date
        FROM bookings b
        JOIN equipment e ON b.equipment_id = e.id
        JOIN users u ON b.farmer_id = u.id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        WHERE b.booking_id = ?
    ''', (booking_id,)).fetchone()
    
    conn.close()
    
    if not booking_data:
        flash('Receipt not found', 'error')
        return redirect(url_for('farmer_dashboard'))
    
    user_lang = get_user_language()
    import json, os
    try:
        with open(os.path.join('static', 'translations', f'{user_lang}.json'), 'r', encoding='utf-8') as f:
            text = json.load(f)
    except:
        text = {}
    
    return render_template('receipt.html', booking=dict(booking_data), text=text, current_lang=user_lang)

@app.route('/download-receipt/<booking_id>')
def download_receipt(booking_id):
    """Generate and download PDF receipt with multi-language support"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get booking, payment, and equipment details
    booking_data = conn.execute('''
        SELECT b.*, e.name as equipment_name, e.type as equipment_type,
               u.name as farmer_name, u.phone as farmer_phone,
               p.payment_method, p.transaction_id, p.payment_status, p.created_at as payment_date
        FROM bookings b
        JOIN equipment e ON b.equipment_id = e.id
        JOIN users u ON b.farmer_id = u.id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        WHERE b.booking_id = ?
    ''', (booking_id,)).fetchone()
    
    conn.close()
    
    if not booking_data:
        flash('Receipt not found', 'error')
        return redirect(url_for('farmer_dashboard'))
    
    # Get user language
    user_lang = session.get('lang', session.get('user_language', 'en'))
    
    # Generate PDF
    from pdf_generator import generate_receipt_pdf
    try:
        pdf_path = generate_receipt_pdf(dict(booking_data), user_lang)
        from flask import send_file
        return send_file(pdf_path, as_attachment=True, download_name=f'receipt_{booking_id}.pdf')
    except Exception as e:
        print(f"PDF generation error: {e}")
        flash('Error generating receipt PDF', 'error')
        return redirect(url_for('receipt', booking_id=booking_id))

@app.route('/api/equipment/<language>')
def get_equipment_by_language(language='en'):
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    equipment = conn.execute('''
        SELECT e.*, u.name as owner_name,
               COALESCE(et.translated_name, e.name) as display_name,
               COALESCE(et.translated_description, e.description) as display_description
        FROM equipment e 
        JOIN users u ON e.owner_id = u.id 
        LEFT JOIN equipment_translations et ON LOWER(e.name) = et.equipment_name_key AND et.language_code = ?
        WHERE e.available = 1 AND u.user_type = 'owner'
        ORDER BY e.created_at DESC
    ''', (language,)).fetchall()
    
    equipment_list = []
    for eq in equipment:
        equipment_list.append({
            'id': eq['id'],
            'name': eq['display_name'],
            'type': eq['type'],
            'description': eq['display_description'],
            'price_per_hour': eq['price_per_hour'],
            'price_per_day': eq['price_per_day'],
            'location': eq['location'],
            'owner_name': eq['owner_name'],
            'image': eq['image']
        })
    
    conn.close()
    return jsonify({'equipment': equipment_list})
@app.route('/add_sample_equipment')
def add_sample_equipment():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Admin access required'}), 401
    
    conn = get_db_connection()
    
    # Add sample equipment
    sample_equipment = [
        ('Tractor', 'Tractor', 500, 2000, 'Bangalore', 'High-quality farming tractor'),
        ('Harvester', 'Harvester', 800, 3000, 'Mysore', 'Efficient crop harvesting machine'),
        ('Bulldozer', 'Bulldozer', 1000, 4000, 'Hubli', 'Heavy earth moving equipment'),
        ('Solar Inverter', 'Solar Equipment', 200, 800, 'Mangalore', 'Solar energy conversion device'),
        ('Bio Gas Plant', 'Bio Equipment', 300, 1200, 'Belgaum', 'Renewable energy generation system')
    ]
    
    # Get first owner user for sample data
    owner = conn.execute("SELECT id FROM users WHERE user_type = 'owner' LIMIT 1").fetchone()
    if not owner:
        # Create a sample owner
        from werkzeug.security import generate_password_hash
        owner_password = generate_password_hash('owner123')
        conn.execute('''
            INSERT INTO users (username, password, name, user_type, phone, location) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('sample_owner', owner_password, 'Sample Owner', 'owner', '9876543210', 'Karnataka'))
        owner_id = conn.lastrowid
    else:
        owner_id = owner['id']
    
    for eq in sample_equipment:
        conn.execute('''
            INSERT OR REPLACE INTO equipment (name, type, price_per_hour, price_per_day, location, owner_id, description, available) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (*eq, owner_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Sample equipment added successfully!'})

@app.route('/setup_multilingual')
def setup_multilingual():
    conn = get_db_connection()
    
    # Step 1: Create sample owner if not exists
    owner = conn.execute("SELECT id FROM users WHERE user_type = 'owner' LIMIT 1").fetchone()
    if not owner:
        from werkzeug.security import generate_password_hash
        owner_password = generate_password_hash('owner123')
        conn.execute('''
            INSERT INTO users (username, password, name, user_type, phone, location) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('sample_owner', owner_password, 'Sample Owner', 'owner', '9876543210', 'Karnataka'))
        owner_id = conn.lastrowid
    else:
        owner_id = owner['id']
    
    # Step 2: Add sample equipment
    sample_equipment = [
        ('Tractor', 'Tractor', 500, 2000, 'Bangalore', 'High-quality farming tractor'),
        ('Harvester', 'Harvester', 800, 3000, 'Mysore', 'Efficient crop harvesting machine'),
        ('Bulldozer', 'Bulldozer', 1000, 4000, 'Hubli', 'Heavy earth moving equipment'),
        ('Solar Inverter', 'Solar Equipment', 200, 800, 'Mangalore', 'Solar energy conversion device'),
        ('Bio Gas Plant', 'Bio Equipment', 300, 1200, 'Belgaum', 'Renewable energy generation system')
    ]
    
    equipment_ids = []
    for eq in sample_equipment:
        cursor = conn.execute('''
            INSERT OR REPLACE INTO equipment (name, type, price_per_hour, price_per_day, location, owner_id, description, available) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (*eq, owner_id))
        equipment_ids.append(cursor.lastrowid)
    
    # Step 3: Add translations
    translations = {
        'Tractor': {'kn': 'ಟ್ರಾಕ್ಟರ್', 'te': 'ట్రాక్టర్', 'hi': 'ट्रैक्टर'},
        'Bulldozer': {'kn': 'ಬುಲ್ಡೋಜರ್', 'te': 'బుల్డోజర్', 'hi': 'बुलडोजर'},
        'Solar Inverter': {'kn': 'ಸೌರ ಇನ್ವೆರ್ಟರ್', 'te': 'సౌర ఇన్వర్టర్', 'hi': 'सोलर इन्वर्टर'},
        'Harvester': {'kn': 'ಕೊಯ್ಲುಗಾರ ಯಂತ್ರ', 'te': 'హార్వెస్టర్', 'hi': 'हार्वेस्टर'},
        'Bio Gas Plant': {'kn': 'ಬಯೋ ಗ್ಯಾಸ್ ಘಟಕ', 'te': 'బయో గ್యాస్ ప్లాంట్', 'hi': 'बायो गैस प्लांट'}
    }
    
    added_count = 0
    equipment_list = conn.execute('SELECT id, name FROM equipment').fetchall()
    for eq in equipment_list:
        eq_name = eq['name']
        eq_id = eq['id']
        
        if eq_name in translations:
            for lang_code, trans_name in translations[eq_name].items():
                conn.execute('''
                    INSERT OR REPLACE INTO equipment_translations 
                    (equipment_id, language_code, translated_name, translated_description)
                    VALUES (?, ?, ?, ?)
                ''', (eq_id, lang_code, trans_name, f'Translated {eq_name}'))
                added_count += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Multilingual setup complete!',
        'equipment_added': len(sample_equipment),
        'translations_added': added_count,
        'next_step': 'Login as farmer and visit /rental_service?lang=kn'
    })

@app.route('/populate_translations')
def populate_translations():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Admin access required'}), 401
    
    conn = get_db_connection()
    
    # Get all equipment
    equipment_list = conn.execute('SELECT id, name FROM equipment').fetchall()
    
    # Translation mappings
    translations = {
        'Tractor': {
            'kn': 'ಟ್ರಾಕ್ಟರ್',
            'te': 'ట్రాక్టర్', 
            'hi': 'ट्रैक्टर'
        },
        'Bulldozer': {
            'kn': 'ಬುಲ್ಡೋಜರ್',
            'te': 'బుల్డోజర್',
            'hi': 'बुलडोजर'
        },
        'Solar Inverter': {
            'kn': 'ಸೌರ ಇನ್ವೆರ್ಟರ್',
            'te': 'సౌర ఇన్వర్టర్',
            'hi': 'सोलर इन्वर्टर'
        },
        'Harvester': {
            'kn': 'ಕೊಯ್ಲುಗಾರ ಯಂತ್ರ',
            'te': 'హార్వెస్టర్',
            'hi': 'हार्वेस्टर'
        },
        'Bio Gas Plant': {
            'kn': 'ಬಯೋ ಗ್ಯಾಸ್ ಘಟಕ',
            'te': 'బయో గ್యాస్ ప్లాంట్',
            'hi': 'बायो गैस प्लांट'
        }
    }
    
    added_count = 0
    for eq in equipment_list:
        eq_name = eq['name']
        eq_id = eq['id']
        
        if eq_name in translations:
            for lang_code, trans_name in translations[eq_name].items():
                conn.execute('''
                    INSERT OR REPLACE INTO equipment_translations 
                    (equipment_id, language_code, translated_name, translated_description)
                    VALUES (?, ?, ?, ?)
                ''', (eq_id, lang_code, trans_name, f'Translated {eq_name}'))
                added_count += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'message': f'Added {added_count} translations',
        'equipment_processed': len(equipment_list)
    })

@app.route('/debug/translations')
def debug_translations():
    conn = get_db_connection()
    
    # Get all equipment with their translations
    equipment = conn.execute('''
        SELECT e.id, e.name, 
               et_kn.translated_name as kannada_name,
               et_te.translated_name as telugu_name,
               et_hi.translated_name as hindi_name
        FROM equipment e
        LEFT JOIN equipment_translations et_kn ON e.id = et_kn.equipment_id AND et_kn.language_code = 'kn'
        LEFT JOIN equipment_translations et_te ON e.id = et_te.equipment_id AND et_te.language_code = 'te' 
        LEFT JOIN equipment_translations et_hi ON e.id = et_hi.equipment_id AND et_hi.language_code = 'hi'
    ''').fetchall()
    
    conn.close()
    
    result = []
    for eq in equipment:
        result.append({
            'id': eq['id'],
            'english': eq['name'],
            'kannada': eq['kannada_name'],
            'telugu': eq['telugu_name'],
            'hindi': eq['hindi_name']
        })
    
    return jsonify(result)

@app.route('/fix_missing_translations')
def fix_missing_translations():
    """Add translations for equipment that don't have them"""
    conn = get_db_connection()
    
    # Get equipment without translations
    missing_equipment = conn.execute('''
        SELECT e.id, e.name
        FROM equipment e
        WHERE e.available = 1 
        AND e.id NOT IN (SELECT DISTINCT equipment_id FROM equipment_translations)
    ''').fetchall()
    
    # Basic translation mappings
    translation_map = {
        'tractor': {'kn': 'ಟ್ರಾಕ್ಟರ್', 'te': 'ట్రాక్టర్', 'hi': 'ट्रैक्टर'},
        'harvester': {'kn': 'ಹಾರ್ವೆಸ್ಟರ್', 'te': 'హార్వెస్టర్', 'hi': 'हार्वेस्टर'},
        'drill': {'kn': 'ಬೀಜ ಬಿತ್ತುವ ಯಂತ್ರ', 'te': 'విత్తన యంత్రం', 'hi': 'बीज बोने की मशीन'},
        'seeder': {'kn': 'ಬೀಜ ಬಿತ್ತುವ ಯಂತ್ರ', 'te': 'విత్తన యంత్రం', 'hi': 'बीज बोने की मशीन'},
        'irrigation': {'kn': 'ನೀರಾವರಿ ವ್ಯವಸ್ಥೆ', 'te': 'నీటిపారుదల వ్యవస్థ', 'hi': 'सिंचाई प्रणाली'},
        'tiller': {'kn': 'ಟಿಲ್ಲರ್', 'te': 'టిల్లర్', 'hi': 'टिलर'},
        'sprayer': {'kn': 'ಸ್ಪ್ರೇಯರ್', 'te': 'స్ప్రేయర్', 'hi': 'स्प्रेयर'},
        'weeder': {'kn': 'ಕಳೆ ತೆಗೆಯುವ ಯಂತ್ರ', 'te': 'కలుపు తొలగింపు యంత్రం', 'hi': 'खरपतवार हटाने की मशीन'},
        'fertilizer': {'kn': 'ರಸಗೊಬ್ಬರ', 'te': 'ఎరువులు', 'hi': 'उर्वरक'},
        'machine': {'kn': 'ಯಂತ್ರ', 'te': 'యంత్రం', 'hi': 'मशीन'}
    }
    
    added_count = 0
    for eq in missing_equipment:
        eq_name = eq['name'].lower()
        eq_id = eq['id']
        
        # Find matching translation
        translation = None
        for key, trans_dict in translation_map.items():
            if key in eq_name:
                translation = trans_dict
                break
        
        # Use generic machine translation if no specific match
        if not translation:
            translation = translation_map['machine']
        
        # Add translations for all languages
        for lang_code, trans_name in translation.items():
            conn.execute('''
                INSERT OR REPLACE INTO equipment_translations 
                (equipment_id, language_code, translated_name, translated_description)
                VALUES (?, ?, ?, ?)
            ''', (eq_id, lang_code, trans_name, f'{trans_name} - Description'))
            added_count += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Added translations for {len(missing_equipment)} equipment items',
        'missing_equipment_count': len(missing_equipment),
        'translations_added': added_count
    })

@app.route('/debug/routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify(routes)

def decode_unicode_string(text):
    """Safely decode unicode-escaped strings"""
    if not text:
        return text
    
    try:
        # Remove surrounding quotes if present
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        # Try to decode if it contains unicode escapes
        if '\\u' in text:
            return text.encode('utf-8').decode('unicode_escape')
        else:
            return text
            
    except Exception as e:
        print(f"Unicode decode error for '{text}': {e}")
        return text

@app.route('/rental_service')
def rental_service():
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return redirect(url_for('index'))
    
    # Handle language parameter from URL
    lang_param = request.args.get('lang')
    if lang_param:
        session['user_language'] = lang_param
        print(f"Language set from URL parameter: {lang_param}")
    
    user_lang = get_user_language()
    print(f"Rental service language: {user_lang}")
    
    conn = get_db_connection()
    
    try:
        # Check if equipment_translations table exists
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='equipment_translations'"
        ).fetchone()
        
        if table_exists:
            # Get equipment with ALL translations
            equipment = conn.execute('''
                SELECT e.*, u.name as owner_name
                FROM equipment e 
                JOIN users u ON e.owner_id = u.id 
                WHERE e.available = 1 AND u.user_type = 'owner'
                ORDER BY e.created_at DESC
            ''').fetchall()
        else:
            equipment = conn.execute('''
                SELECT e.*, u.name as owner_name
                FROM equipment e 
                JOIN users u ON e.owner_id = u.id 
                WHERE e.available = 1 AND u.user_type = 'owner'
                ORDER BY e.created_at DESC
            ''').fetchall()
        
    except Exception as e:
        print(f"[DB_ERROR] Database error in rental_service: {e}")
        equipment = conn.execute('''
            SELECT e.*, u.name as owner_name
            FROM equipment e 
            JOIN users u ON e.owner_id = u.id 
            WHERE e.available = 1 AND u.user_type = 'owner'
            ORDER BY e.created_at DESC
        ''').fetchall()
    
    processed_equipment = []
    
    for eq in equipment:
        eq_dict = dict(eq)
        name_en = str(eq_dict['name'])
        
        # Get all translations for this equipment
        translations = {}
        if table_exists:
            trans_rows = conn.execute('''
                SELECT language_code, translated_name
                FROM equipment_translations
                WHERE equipment_id = ?
            ''', (eq_dict['id'],)).fetchall()
            
            for trans in trans_rows:
                translations[trans['language_code']] = trans['translated_name']
        
        # Get current language translation
        name_local = translations.get(user_lang, '')
        
        processed_equipment.append({
            'id': eq_dict['id'],
            'name': name_en,
            'name_en': name_en,
            'name_hi': translations.get('hi', ''),
            'name_te': translations.get('te', ''),
            'name_kn': translations.get('kn', ''),
            'name_ta': translations.get('ta', ''),
            'name_local': name_local,
            'display_name': name_en,
            'display_description': eq_dict.get('description', 'Professional agricultural equipment'),
            'type': eq_dict['type'],
            'price_per_hour': eq_dict['price_per_hour'],
            'price_per_day': eq_dict['price_per_day'],
            'location': eq_dict['location'],
            'owner_name': eq_dict['owner_name'],
            'image': eq_dict['image'],
            'available': eq_dict['available']
        })
    
    conn.close()
    
    print(f"Processed {len(processed_equipment)} equipment items for language {user_lang}")
    
    return render_template('rental_service.html', 
                         equipment=processed_equipment,
                         current_lang=user_lang)

@app.route('/test_unicode_page')
def test_unicode_page():
    """Test Unicode display in template"""
    return render_template('test_unicode.html')

@app.route('/test_unicode')
def test_unicode():
    """Test Unicode display"""
    test_data = {
        'kannada': 'ಟ್ರಾಕ್ಟರ್',
        'telugu': 'ట్రాక్టర్',
        'hindi': 'ट्रैक्टर',
        'escaped_kannada': 'escaped_text',
        'decoded_kannada': 'decoded_text'
    }
    
    return jsonify(test_data)

@app.route('/populate_correct_unicode')
def populate_correct_unicode():
    """Add correct Unicode translations"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Admin access required'}), 401
    
    conn = get_db_connection()
    
    # Correct Unicode translations
    translations = {
        'Tractor': {'kn': 'ಟ್ರಾಕ್ಟರ್', 'te': 'ట్రాక్టర్', 'hi': 'ट्रैक्टर'},
        'Heavy Duty Tractor': {'kn': 'ಟ್ರಾಕ್ಟರ್', 'te': 'ట్రాక్టర్', 'hi': 'ट्रैक्टर'},
        'Harvester': {'kn': 'ಹಾರ್ವೆಸ್ಟರ್', 'te': 'హార్వెస్టర్', 'hi': 'हार्वेस्टर'},
        'Combine Harvester': {'kn': 'ಹಾರ್ವೆಸ್ಟರ್', 'te': 'హార్వెస్టర్', 'hi': 'हार्वेस्टर'},
        'Seeder': {'kn': 'ಬೀಜ ಬಿತ್ತುವ ಯಂತ್ರ', 'te': 'విత్తన యంత్రం', 'hi': 'बीज बोने की मशीन'},
        'Seed Drill Machine': {'kn': 'ಬೀಜ ಬಿತ್ತುವ ಯಂತ್ರ', 'te': 'విత్తన యంత్రం', 'hi': 'बीज बोने की मशीन'}
    }
    
    # Get all equipment
    equipment_list = conn.execute('SELECT id, name FROM equipment').fetchall()
    
    added_count = 0
    for eq in equipment_list:
        eq_name = eq['name']
        eq_id = eq['id']
        
        if eq_name in translations:
            for lang_code, trans_name in translations[eq_name].items():
                conn.execute('''
                    INSERT OR REPLACE INTO equipment_translations 
                    (equipment_id, language_code, translated_name, translated_description)
                    VALUES (?, ?, ?, ?)
                ''', (eq_id, lang_code, trans_name, f'{trans_name} - Description'))
                added_count += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Added {added_count} correct Unicode translations',
        'added_count': added_count
    })

@app.route('/debug_unicode')
def debug_unicode():
    """Debug Unicode data in database"""
    conn = get_db_connection()
    
    # Get raw data from database
    translations = conn.execute('''
        SELECT et.*, e.name as equipment_name
        FROM equipment_translations et
        JOIN equipment e ON et.equipment_id = e.id
        WHERE et.language_code = 'kn'
    ''').fetchall()
    
    result = []
    for t in translations:
        raw_name = t['translated_name']
        decoded_name = decode_unicode_string(raw_name)
        
        result.append({
            'equipment': t['equipment_name'],
            'raw_stored': raw_name,
            'decoded': decoded_name,
            'contains_escape': '\\u' in raw_name
        })
    
    conn.close()
    return jsonify(result)

@app.route('/fix_unicode_issues')
def fix_unicode_issues():
    """Fix Unicode encoding issues in database"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Admin access required'}), 401
    
    conn = get_db_connection()
    fixed_count = 0
    errors = []
    
    try:
        # Check if equipment_translations table exists
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='equipment_translations'"
        ).fetchone()
        
        if table_exists:
            # Fix escaped Unicode in translations
            translations = conn.execute('SELECT * FROM equipment_translations').fetchall()
            
            for trans in translations:
                original_name = trans['translated_name']
                
                if original_name and '\\u' in str(original_name):
                    try:
                        fixed_name = decode_unicode_string(str(original_name))
                        
                        # Verify the fixed name is valid UTF-8
                        fixed_name.encode('utf-8')
                        
                        # Update the record
                        conn.execute('''
                            UPDATE equipment_translations 
                            SET translated_name = ? 
                            WHERE id = ?
                        ''', (fixed_name, trans['id']))
                        
                        print(f"Fixed: {original_name} -> {fixed_name}")
                        fixed_count += 1
                        
                    except Exception as e:
                        error_msg = f"Error fixing translation ID {trans['id']}: {str(e)}"
                        print(error_msg)
                        errors.append(error_msg)
        
        conn.commit()
        
    except Exception as e:
        error_msg = f"Database error: {str(e)}"
        print(error_msg)
        errors.append(error_msg)
    
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Fixed {fixed_count} Unicode issues',
        'fixed_count': fixed_count,
        'errors': errors,
        'status': 'completed' if len(errors) == 0 else 'completed_with_errors'
    })

@app.route('/add_equipment', methods=['POST'])
def add_equipment():
    if 'user_id' not in session or session.get('user_type') != 'owner':
        return jsonify({'error': 'Unauthorized'}), 401
    
    name = request.form.get('name')
    equipment_type = request.form.get('type')
    price_per_hour = float(request.form.get('price_per_hour'))
    price_per_day = float(request.form.get('price_per_day'))
    location = request.form.get('location')
    description = request.form.get('description', '')
    
    # Handle image upload
    image_filename = None
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename:
            import os
            filename = f"{uuid.uuid4().hex}_{image_file.filename}"
            upload_path = os.path.join('static', 'uploads')
            os.makedirs(upload_path, exist_ok=True)
            image_path = os.path.join(upload_path, filename)
            image_file.save(image_path)
            image_filename = filename
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO equipment (name, type, price_per_hour, price_per_day, location, owner_id, description, image) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, equipment_type, price_per_hour, price_per_day, location, session['user_id'], description, image_filename))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Equipment added successfully!'})

@app.route('/delete_equipment', methods=['POST'])
def delete_equipment():
    if 'user_id' not in session or session.get('user_type') != 'owner':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    equipment_id = data.get('equipment_id')
    
    conn = get_db_connection()
    conn.execute('DELETE FROM equipment WHERE id = ? AND owner_id = ?', 
                (equipment_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Equipment deleted successfully!'})

@app.route('/get_equipment/<int:equipment_id>')
def get_equipment(equipment_id):
    if 'user_id' not in session or session.get('user_type') != 'owner':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    equipment = conn.execute('SELECT * FROM equipment WHERE id = ? AND owner_id = ?', 
                           (equipment_id, session['user_id'])).fetchone()
    conn.close()
    
    if equipment:
        return jsonify({'success': True, 'equipment': dict(equipment)})
    else:
        return jsonify({'error': 'Equipment not found'}), 404

@app.route('/update_equipment', methods=['POST'])
def update_equipment():
    if 'user_id' not in session or session.get('user_type') != 'owner':
        return jsonify({'error': 'Unauthorized'}), 401
    
    equipment_id = request.form.get('equipment_id')
    name = request.form.get('name')
    equipment_type = request.form.get('type')
    price_per_hour = float(request.form.get('price_per_hour'))
    price_per_day = float(request.form.get('price_per_day'))
    location = request.form.get('location')
    description = request.form.get('description', '')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE equipment SET name = ?, type = ?, price_per_hour = ?, price_per_day = ?, 
        location = ?, description = ? WHERE id = ? AND owner_id = ?
    ''', (name, equipment_type, price_per_hour, price_per_day, location, description, 
          equipment_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Equipment updated successfully!'})

@app.route('/unlock_database')
def unlock_database():
    """Force unlock database by closing all connections"""
    import gc
    import time
    
    try:
        # Force garbage collection to close any lingering connections
        gc.collect()
        time.sleep(1)
        
        # Test database access
        conn = sqlite3.connect('krushi_rent_ai.db', timeout=5.0)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Database unlocked successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Database still locked. Try restarting the Flask app.'
        })

@app.route('/fix_payment_schema')
def fix_payment_schema():
    """Manually fix payment schema issues"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Admin access required'}), 401
    
    conn = sqlite3.connect('krushi_rent_ai.db')
    cursor = conn.cursor()
    
    try:
        # Check current payments table structure
        cursor.execute("PRAGMA table_info(payments)")
        columns = {column[1]: column[2] for column in cursor.fetchall()}
        
        missing_columns = []
        
        # Check for payment_status column
        if 'payment_status' not in columns:
            cursor.execute('ALTER TABLE payments ADD COLUMN payment_status TEXT DEFAULT "PENDING"')
            missing_columns.append('payment_status')
        
        # Update existing records to have proper payment_status
        cursor.execute('UPDATE payments SET payment_status = "PENDING" WHERE payment_status IS NULL')
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment schema fixed successfully',
            'columns_added': missing_columns,
            'existing_columns': list(columns.keys())
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        conn.close()

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    import os
    from flask import send_file
    return send_file(os.path.join('static', 'uploads', filename))

# ============= ML DEMAND PREDICTION =============

@app.route('/api/demand-prediction')
def demand_prediction_api():
    """Get ML-based demand predictions for all equipment types"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        from demand_prediction import get_demand_summary
        summary = get_demand_summary()
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/demand-prediction/<equipment_type>')
def demand_prediction_detail(equipment_type):
    """Get 30-day demand forecast for a specific equipment type"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        from demand_prediction import predict_demand_for_equipment, get_monthly_demand_forecast
        forecast = predict_demand_for_equipment(equipment_type, days_ahead=30)
        monthly = get_monthly_demand_forecast(equipment_type, months_ahead=6)
        return jsonify({'success': True, 'daily': forecast, 'monthly': monthly})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/booking/<booking_id>')
def get_booking_detail(booking_id):
    """Return booking details as JSON for the modal"""
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db_connection()
    b = conn.execute('''
        SELECT b.*, e.name as equipment_name, e.price_per_hour as hourly_rate,
               p.payment_method, p.payment_status as pay_status
        FROM bookings b
        JOIN equipment e ON b.equipment_id = e.id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        WHERE b.booking_id = ? AND b.farmer_id = ?
    ''', (booking_id, session['user_id'])).fetchone()
    conn.close()
    if not b:
        return jsonify({'error': 'Not found'}), 404
    d = dict(b)
    return jsonify({
        'booking_id':     d['booking_id'],
        'equipment_name': d['equipment_name'],
        'farmer':         session.get('user_name', ''),
        'booking_date':   d['booking_date'],
        'booking_time':   '08:00 AM',
        'rental_duration':d.get('duration_hours', 0),
        'hourly_rate':    d.get('hourly_rate', 0),
        'total_amount':   d.get('total_amount', 0),
        'payment_method': d.get('payment_method') or 'COD',
        'payment_status': d.get('pay_status') or d.get('payment_status') or 'PENDING',
        'booking_status': d.get('status', 'CONFIRMED'),
        'created_at':     d.get('created_at', ''),
    })

@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return redirect(url_for('index'))
    conn = get_db_connection()
    bookings_raw = conn.execute('''
        SELECT b.*, e.name as equipment_name, e.price_per_hour as hourly_rate,
               p.payment_method, p.payment_status as pay_status
        FROM bookings b
        JOIN equipment e ON b.equipment_id = e.id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        WHERE b.farmer_id = ?
        ORDER BY b.created_at DESC
    ''', (session['user_id'],)).fetchall()
    # Get booking_ids already reviewed
    reviewed = set(r['booking_id'] for r in conn.execute(
        'SELECT booking_id FROM reviews WHERE farmer_id=?', (session['user_id'],)
    ).fetchall())
    conn.close()
    bookings = []
    for b in bookings_raw:
        d = dict(b)
        d['display_status'] = d.get('status', 'CONFIRMED').title()
        d['booking_time']   = '08:00 AM'
        d['rental_duration']= d.get('duration_hours', 0)
        d['payment_method'] = d.get('payment_method') or 'COD'
        d['payment_status'] = d.get('pay_status') or d.get('payment_status') or 'PENDING'
        d['already_reviewed'] = d['booking_id'] in reviewed
        bookings.append(d)
    user_lang = get_user_language()
    return render_template('my_bookings.html', bookings=bookings, current_lang=user_lang)

# ============= RATINGS & REVIEWS =============

@app.route('/submit_review', methods=['POST'])
def submit_review():
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    booking_id   = data.get('booking_id')
    rating       = int(data.get('rating', 0))
    review_text  = data.get('review_text', '').strip()
    if not booking_id or not (1 <= rating <= 5):
        return jsonify({'error': 'Invalid data'}), 400
    conn = get_db_connection()
    try:
        booking = conn.execute(
            'SELECT * FROM bookings WHERE booking_id=? AND farmer_id=?',
            (booking_id, session['user_id'])
        ).fetchone()
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        conn.execute('''
            INSERT OR REPLACE INTO reviews (booking_id, farmer_id, equipment_id, rating, review_text)
            VALUES (?, ?, ?, ?, ?)
        ''', (booking_id, session['user_id'], booking['equipment_id'], rating, review_text))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/my_reviews')
def my_reviews():
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT r.*, COALESCE(e.name, 'Equipment #'||r.equipment_id) as equipment_name, b.booking_date
        FROM reviews r
        LEFT JOIN equipment e ON r.equipment_id = e.id
        JOIN bookings b ON r.booking_id = b.booking_id
        WHERE r.farmer_id = ?
        ORDER BY r.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/equipment_reviews/<int:equipment_id>')
def equipment_reviews(equipment_id):
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT r.rating, r.review_text, r.created_at, u.name as farmer_name
        FROM reviews r
        JOIN users u ON r.farmer_id = u.id
        WHERE r.equipment_id = ?
        ORDER BY r.created_at DESC
    ''', (equipment_id,)).fetchall()
    avg = conn.execute(
        'SELECT ROUND(AVG(rating),1) as avg, COUNT(*) as cnt FROM reviews WHERE equipment_id=?',
        (equipment_id,)
    ).fetchone()
    conn.close()
    return jsonify({
        'reviews': [dict(r) for r in rows],
        'avg_rating': avg['avg'] or 0,
        'total': avg['cnt']
    })

@app.route('/api/owner_ratings')
def owner_ratings():
    if 'user_id' not in session or session.get('user_type') != 'owner':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT e.name as equipment_name, e.id as equipment_id,
               ROUND(AVG(r.rating),1) as avg_rating, COUNT(r.id) as total_reviews
        FROM equipment e
        LEFT JOIN reviews r ON e.id = r.equipment_id
        WHERE e.owner_id = ?
        GROUP BY e.id
        ORDER BY avg_rating DESC
    ''', (session['user_id'],)).fetchall()
    recent = conn.execute('''
        SELECT r.rating, r.review_text, r.created_at,
               u.name as farmer_name,
               COALESCE(e.name, 'Equipment #'||r.equipment_id) as equipment_name
        FROM reviews r
        JOIN users u ON r.farmer_id = u.id
        LEFT JOIN equipment e ON r.equipment_id = e.id
        WHERE e.owner_id = ? OR r.equipment_id IN (
            SELECT id FROM equipment WHERE owner_id = ?
        )
        ORDER BY r.created_at DESC LIMIT 10
    ''', (session['user_id'], session['user_id'])).fetchall()
    conn.close()
    return jsonify({'equipment_ratings': [dict(r) for r in rows], 'recent_reviews': [dict(r) for r in recent]})

# ============= REPORTS MODULE =============

@app.route('/admin/reports')
def admin_reports():
    """Admin reports dashboard"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    user_lang = get_user_language()
    return render_template('admin/reports.html', current_lang=user_lang)

@app.route('/admin/reports/data')
def admin_reports_data():
    """Get reports data with date filtering"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        
        conn = get_db_connection()
        
        # Equipment Usage Report
        if start_date and end_date:
            equipment_usage = conn.execute('''
                SELECT e.name, e.type, COUNT(b.id) as times_rented, 
                       COALESCE(SUM(b.total_amount), 0) as revenue
                FROM equipment e
                LEFT JOIN bookings b ON e.id = b.equipment_id AND b.booking_date BETWEEN ? AND ?
                GROUP BY e.id ORDER BY revenue DESC
            ''', (start_date, end_date)).fetchall()
        else:
            equipment_usage = conn.execute('''
                SELECT e.name, e.type, COUNT(b.id) as times_rented, 
                       COALESCE(SUM(b.total_amount), 0) as revenue
                FROM equipment e
                LEFT JOIN bookings b ON e.id = b.equipment_id
                GROUP BY e.id ORDER BY revenue DESC
            ''').fetchall()
        
        # Farmer Bookings Report
        if start_date and end_date:
            farmer_bookings = conn.execute('''
                SELECT u.name, COALESCE(u.phone, 'N/A') as phone, COUNT(b.id) as total_bookings, 
                       COALESCE(SUM(b.total_amount), 0) as total_paid
                FROM users u
                LEFT JOIN bookings b ON u.id = b.farmer_id AND b.booking_date BETWEEN ? AND ?
                WHERE u.user_type = 'farmer'
                GROUP BY u.id ORDER BY total_paid DESC
            ''', (start_date, end_date)).fetchall()
        else:
            farmer_bookings = conn.execute('''
                SELECT u.name, COALESCE(u.phone, 'N/A') as phone, COUNT(b.id) as total_bookings, 
                       COALESCE(SUM(b.total_amount), 0) as total_paid
                FROM users u
                LEFT JOIN bookings b ON u.id = b.farmer_id
                WHERE u.user_type = 'farmer'
                GROUP BY u.id ORDER BY total_paid DESC
            ''').fetchall()
        
        # Daily Revenue Report
        if start_date and end_date:
            daily_revenue = conn.execute('''
                SELECT booking_date as date, SUM(total_amount) as revenue
                FROM bookings
                WHERE booking_date BETWEEN ? AND ?
                GROUP BY booking_date ORDER BY booking_date
            ''', (start_date, end_date)).fetchall()
        else:
            daily_revenue = conn.execute('''
                SELECT booking_date as date, SUM(total_amount) as revenue
                FROM bookings
                GROUP BY booking_date ORDER BY booking_date
            ''').fetchall()
        
        # Monthly Revenue Report
        if start_date and end_date:
            monthly_revenue = conn.execute('''
                SELECT strftime('%Y-%m', booking_date) as month, SUM(total_amount) as revenue
                FROM bookings
                WHERE booking_date BETWEEN ? AND ?
                GROUP BY month ORDER BY month
            ''', (start_date, end_date)).fetchall()
        else:
            monthly_revenue = conn.execute('''
                SELECT strftime('%Y-%m', booking_date) as month, SUM(total_amount) as revenue
                FROM bookings
                GROUP BY month ORDER BY month
            ''').fetchall()
        
        # Payment Method Report
        if start_date and end_date:
            payment_methods = conn.execute('''
                SELECT p.payment_method, COUNT(*) as count, SUM(p.amount) as total_amount
                FROM payments p
                JOIN bookings b ON p.booking_id = b.booking_id
                WHERE b.booking_date BETWEEN ? AND ?
                GROUP BY p.payment_method
            ''', (start_date, end_date)).fetchall()
        else:
            payment_methods = conn.execute('''
                SELECT payment_method, COUNT(*) as count, SUM(amount) as total_amount
                FROM payments
                GROUP BY payment_method
            ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'equipment_usage': [dict(row) for row in equipment_usage],
            'farmer_bookings': [dict(row) for row in farmer_bookings],
            'daily_revenue': [dict(row) for row in daily_revenue],
            'monthly_revenue': [dict(row) for row in monthly_revenue],
            'payment_methods': [dict(row) for row in payment_methods]
        }), 200
        
    except Exception as e:
        print(f"Error in admin_reports_data: {str(e)}")
        return jsonify({
            'equipment_usage': [],
            'farmer_bookings': [],
            'daily_revenue': [],
            'monthly_revenue': [],
            'payment_methods': []
        }), 200



def get_user_language():
    """Get user's preferred language from session"""
    return session.get('user_language', 'en')

def set_user_language(lang):
    """Set user's preferred language in session"""
    valid_langs = ['en', 'hi', 'kn', 'te', 'ta']
    if lang in valid_langs:
        session['user_language'] = lang
        return True
    return False

# ============= LANGUAGE SWITCHING ROUTES =============
@app.route('/set-language/<lang>')
def set_language_route(lang):
    """Set user language and return success"""
    valid_langs = ['en', 'hi', 'kn', 'te', 'ta']
    if lang in valid_langs:
        session['user_language'] = lang
        session.permanent = True
        print(f"[LANG] Language set to: {lang}")
        return jsonify({'success': True, 'language': lang})
    return jsonify({'success': False, 'error': 'Invalid language'}), 400

@app.route('/set_language', methods=['POST'])
def set_language_post():
    """Set language via POST (for AJAX calls)"""
    data = request.get_json()
    lang = data.get('language', 'en')
    if set_user_language(lang):
        session.permanent = True
        return jsonify({'success': True, 'language': lang})
    return jsonify({'success': False, 'error': 'Invalid language'}), 400

@app.route('/get-current-language')
def get_current_language():
    """Get current user language"""
    return jsonify({'language': get_user_language()})

@app.route('/api/translations/<lang>')
def get_translations(lang):
    """Serve translation JSON files with proper UTF-8 encoding"""
    import os
    import json
    valid_langs = ['en', 'hi', 'kn', 'te', 'ta']
    if lang not in valid_langs:
        lang = 'en'
    
    translation_path = os.path.join('static', 'translations', f'{lang}.json')
    
    try:
        with open(translation_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            response = app.response_class(
                response=json.dumps(data, ensure_ascii=False, indent=2),
                status=200,
                mimetype='application/json; charset=utf-8'
            )
            return response
    except FileNotFoundError:
        return jsonify({'error': 'Translation not found'}), 404

if __name__ == '__main__':
    ensure_payment_tables()
    migrate_database()
    init_database()
    create_translations_table()
    # Create reviews table
    conn = sqlite3.connect('krushi_rent_ai.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT NOT NULL UNIQUE,
            farmer_id INTEGER NOT NULL,
            equipment_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            review_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
            FOREIGN KEY (farmer_id) REFERENCES users(id),
            FOREIGN KEY (equipment_id) REFERENCES equipment(id)
        )
    ''')
    conn.commit()
    conn.close()
    from demand_prediction import warmup
    warmup()
    print("=== KRUSHI_APP.PY IS RUNNING ===")
    print("Krushi Rent AI : Intelligent Agricultural Rental Service")
    print("Admin Login: username=admin, password=admin123")
    print("Starting the application...")
    print("Access at: http://localhost:5000")
    print("=== CHAT ROUTE AVAILABLE AT /chat ===")
    app.run(debug=True)


