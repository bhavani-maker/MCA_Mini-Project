# Receipt translations for multi-language support
translations = {
    "en": {
        "receipt": "Payment Receipt",
        "download": "Download Receipt",
        "thankyou": "Thank you for using KrushiRent AI",
        "booking_id": "Booking ID",
        "transaction_id": "Transaction ID",
        "amount": "Amount",
        "date_time": "Date & Time",
        "customer_name": "Customer Name",
        "address": "Address",
        "equipment_name": "Equipment Name",
        "payment_status": "Payment Status",
        "success": "SUCCESS",
        "phone": "Phone",
        "duration": "Duration",
        "hours": "hours"
    },
    "te": {
        "receipt": "చెల్లింపు రసీదు",
        "download": "రసీదు డౌన్లోడ్",
        "thankyou": "కృషి రెంట్ AI ఉపయోగించినందుకు ధన్యవాదాలు",
        "booking_id": "బుకింగ్ ID",
        "transaction_id": "లావాదేవీ ID",
        "amount": "మొత్తం",
        "date_time": "తేదీ & సమయం",
        "customer_name": "కస్టమర్ పేరు",
        "address": "చిరునామా",
        "equipment_name": "పరికరం పేరు",
        "payment_status": "చెల్లింపు స్థితి",
        "success": "విజయవంతం",
        "phone": "ఫోన్",
        "duration": "వ్యవధి",
        "hours": "గంటలు"
    },
    "kn": {
        "receipt": "ಪಾವತಿ ರಸೀದಿ",
        "download": "ರಸೀದಿ ಡೌನ್ಲೋಡ್",
        "thankyou": "KrushiRent AI ಬಳಸಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು",
        "booking_id": "ಬುಕಿಂಗ್ ID",
        "transaction_id": "ವಹಿವಾಟು ID",
        "amount": "ಮೊತ್ತ",
        "date_time": "ದಿನಾಂಕ ಮತ್ತು ಸಮಯ",
        "customer_name": "ಗ್ರಾಹಕರ ಹೆಸರು",
        "equipment_name": "ಉಪಕರಣದ ಹೆಸರು",
        "payment_status": "ಪಾವತಿ ಸ್ಥಿತಿ",
        "success": "ಯಶಸ್ವಿ",
        "phone": "ಫೋನ್",
        "duration": "ಅವಧಿ",
        "hours": "ಗಂಟೆಗಳು"
    },
    "hi": {
        "receipt": "भुगतान रसीद",
        "download": "रसीद डाउनलोड करें",
        "thankyou": "KrushiRent AI का उपयोग करने के लिए धन्यवाद",
        "booking_id": "बुकिंग ID",
        "transaction_id": "लेनदेन ID",
        "amount": "राशि",
        "date_time": "तारीख और समय",
        "customer_name": "ग्राहक का नाम",
        "equipment_name": "उपकरण का नाम",
        "payment_status": "भुगतान स्थिति",
        "success": "सफल",
        "phone": "फोन",
        "duration": "अवधि",
        "hours": "घंटे"
    },
    "ta": {
        "receipt": "பணம் செலுத்திய ரசீது",
        "download": "ரசீதை பதிவிறக்கவும்",
        "thankyou": "KrushiRent AI பயன்படுத்தியதற்கு நன்றி",
        "booking_id": "பதிவு ID",
        "transaction_id": "பரிவர்த்தனை ID",
        "amount": "தொகை",
        "date_time": "தேதி மற்றும் நேரம்",
        "customer_name": "வாடிக்கையாளர் பெயர்",
        "equipment_name": "உபகரணத்தின் பெயர்",
        "payment_status": "பணம் செலுத்தும் நிலை",
        "success": "வெற்றி",
        "phone": "தொலைபேசி",
        "duration": "காலம்",
        "hours": "மணிநேரம்"
    }
}

def t(key, lang='en'):
    """Get translation for a key in specified language"""
    return translations.get(lang, translations['en']).get(key, key)
