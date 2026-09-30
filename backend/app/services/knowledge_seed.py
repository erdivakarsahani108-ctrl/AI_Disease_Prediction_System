"""Seed structured educational knowledge documents into DB."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import KnowledgeDocument

SEED_DOCS = [
    {
        "title": "Fever – General Guidance (Allopathy)",
        "content": (
            "Fever is a temporary rise in body temperature, often due to infection. "
            "Rest, hydration and monitoring are important. Seek care if fever is very high "
            "(>39.4°C / 103°F), lasts more than 3 days, or is accompanied by severe symptoms "
            "such as stiff neck, rash, difficulty breathing or confusion."
        ),
        "content_hi": (
            "बुखार शरीर के तापमान में अस्थायी वृद्धि है। आराम, तरल पदार्थ और निगरानी जरूरी। "
            "बहुत तेज (>39.4°C), 3 दिन से ज्यादा, या गंभीर लक्षणों में डॉक्टर से मिलें।"
        ),
        "medical_system": "allopathy",
        "category": "disease",
        "tags": ["fever", "bukhar", "infection", "temperature"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Common Cold vs Influenza",
        "content": (
            "Common cold usually has gradual onset with runny nose and mild symptoms. "
            "Influenza often starts suddenly with high fever, body aches and marked fatigue. "
            "Both are usually viral; antibiotics are not indicated unless a secondary bacterial "
            "infection is confirmed by a clinician."
        ),
        "content_hi": (
            "सर्दी-जुकाम धीरे शुरू होता है। फ्लू अचानक तेज बुखार और बदन दर्द के साथ। "
            "दोनों आमतौर पर वायरल; एंटीबायोटिक तभी जब बैक्टीरियल संक्रमण पुष्ट हो।"
        ),
        "medical_system": "allopathy",
        "category": "disease",
        "tags": ["cold", "flu", "influenza", "zukam", "khansi"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Ayurveda – Agni & Digestion (Educational)",
        "content": (
            "In Ayurveda, digestive fire (Agni) is considered central to health. "
            "Diet and lifestyle suited to constitution (Prakriti) and season (Ritucharya) "
            "are traditional concepts. Always consult a qualified Ayurvedic practitioner (BAMS)."
        ),
        "content_hi": (
            "आयुर्वेद में अग्नि स्वास्थ्य की कुंजी मानी जाती है। प्रकृति और ऋतु के अनुसार "
            "आहार-विहार। योग्य वैद्य (BAMS) से सलाह लें।"
        ),
        "medical_system": "ayurveda",
        "category": "lifestyle",
        "tags": ["ayurveda", "agni", "digestion", "prakriti"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Homeopathy – Individualization (Educational)",
        "content": (
            "Classical homeopathy emphasizes matching the totality of symptoms to a remedy. "
            "Evidence levels vary across conditions. Never replace emergency or proven "
            "allopathic care when clinically indicated."
        ),
        "content_hi": (
            "होम्योपैथी व्यक्तिगत लक्षणों के आधार पर दवा चुनती है। "
            "आपातकाल में आधुनिक चिकित्सा न छोड़ें।"
        ),
        "medical_system": "homeopathy",
        "category": "lifestyle",
        "tags": ["homeopathy", "remedy", "individualization"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Yoga & Breathing for Stress (Educational)",
        "content": (
            "Gentle yoga, pranayama and mindfulness are widely used as complementary approaches "
            "for stress. They are not a substitute for medical treatment of clinical anxiety, "
            "depression or other psychiatric conditions."
        ),
        "content_hi": (
            "हल्की योगासन और प्राणायाम तनाव कम करने में सहायक। "
            "क्लिनिकल चिंता/अवसाद का विकल्प नहीं।"
        ),
        "medical_system": "yoga_naturopathy",
        "category": "lifestyle",
        "tags": ["yoga", "pranayama", "stress", "anxiety"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "When to Seek Emergency Care",
        "content": (
            "Call emergency services immediately for: severe chest pain or pressure, "
            "sudden weakness/numbness or speech difficulty (possible stroke), severe breathing "
            "difficulty, uncontrolled bleeding, loss of consciousness, severe allergic reaction, "
            "or thoughts of self-harm/suicide."
        ),
        "content_hi": (
            "तुरंत आपातकालीन सेवा: तेज सीने का दर्द, अचानक कमजोरी/बोलने में तकलीफ, "
            "सांस लेने में कठिनाई, बेकाबू खून, बेहोशी, गंभीर एलर्जी, आत्महत्या के विचार।"
        ),
        "medical_system": "allopathy",
        "category": "emergency",
        "tags": ["emergency", "chest pain", "stroke", "suicide", "breathing"],
        "source": "educational-synthetic",
        "evidence_level": "guideline-style",
    },
    {
        "title": "BMI Categories (Educational)",
        "content": (
            "BMI = weight(kg) / height(m)^2. Underweight <18.5, Normal 18.5–24.9, "
            "Overweight 25–29.9, Obese ≥30. BMI does not measure body fat directly and "
            "has limitations in athletes, elderly and some ethnic groups."
        ),
        "content_hi": (
            "BMI = वजन(kg) / ऊंचाई(m)^2। कम वजन <18.5, सामान्य 18.5–24.9, "
            "अधिक वजन 25–29.9, मोटापा ≥30। सीमाएँ हैं।"
        ),
        "medical_system": "allopathy",
        "category": "nutrition",
        "tags": ["bmi", "obesity", "weight", "nutrition"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Diabetes – Lifestyle Basics (Educational)",
        "content": (
            "Type 2 diabetes management often includes diet, physical activity, weight management "
            "and medications as prescribed. Regular glucose monitoring and foot care matter. "
            "Never change prescribed medicines without consulting your doctor."
        ),
        "content_hi": (
            "टाइप 2 मधुमेह में आहार, व्यायाम, वजन नियंत्रण और दवाएँ। "
            "डॉक्टर की सलाह के बिना दवा न बदलें।"
        ),
        "medical_system": "allopathy",
        "category": "disease",
        "tags": ["diabetes", "sugar", "glucose", "madhumeh"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Hypertension – Salt & Lifestyle",
        "content": (
            "Reducing dietary sodium, increasing fruits/vegetables (DASH-style pattern), "
            "limiting alcohol, maintaining healthy weight and regular activity support "
            "blood pressure control alongside prescribed therapy."
        ),
        "content_hi": (
            "नमक कम करें, फल-सब्जियाँ बढ़ाएँ, शराब सीमित करें, वजन नियंत्रित रखें। "
            "दवाएँ डॉक्टर के अनुसार जारी रखें।"
        ),
        "medical_system": "allopathy",
        "category": "disease",
        "tags": ["hypertension", "bp", "blood pressure", "salt"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "PCOS – Educational Overview",
        "content": (
            "Polycystic ovary syndrome may involve irregular periods, androgen excess signs "
            "and metabolic features. Diagnosis and management require clinical evaluation. "
            "Lifestyle measures (diet, activity, weight if indicated) are often part of care."
        ),
        "content_hi": (
            "PCOS में अनियमित माहवारी और अन्य लक्षण हो सकते हैं। "
            "निदान व इलाज के लिए डॉक्टर से मिलें।"
        ),
        "medical_system": "allopathy",
        "category": "disease",
        "tags": ["pcos", "periods", "hormones", "irregular periods"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Hydration & Dehydration Signs",
        "content": (
            "Adequate fluid intake supports many body functions. Signs of dehydration can include "
            "thirst, dry mouth, dark urine, dizziness and fatigue. Severe dehydration needs "
            "medical care, especially in children and elderly."
        ),
        "content_hi": (
            "पर्याप्त पानी पिएँ। निर्जलीकरण: प्यास, सूखा मुँह, गहरा पेशाब, चक्कर। "
            "गंभीर स्थिति में डॉक्टर।"
        ),
        "medical_system": "allopathy",
        "category": "nutrition",
        "tags": ["hydration", "dehydration", "water", "paani"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Unani – Temperament Concept (Educational)",
        "content": (
            "Unani medicine uses concepts of temperament (Mizaj) and balance of humours. "
            "Educational overview only — seek care from a qualified Unani practitioner (BUMS)."
        ),
        "content_hi": (
            "यूनानी चिकित्सा में मिजाज और अخلاत की अवधारणा। "
            "योग्य हकीम (BUMS) से सलाह लें।"
        ),
        "medical_system": "unani",
        "category": "lifestyle",
        "tags": ["unani", "mizaj", "temperament"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Dengue – Warning Signs (Educational)",
        "content": "Warning signs include severe abdominal pain, persistent vomiting, bleeding gums, lethargy, restlessness, and rapid drop in platelets. Seek urgent care if these appear.",
        "content_hi": "चेतावनी संकेत: तेज पेट दर्द, बार-बार उल्टी, मसूड़ों से खून, सुस्ती। तुरंत डॉक्टर/अस्पताल जाएँ।",
        "medical_system": "allopathy",
        "category": "emergency",
        "tags": ["dengue", "warning", "platelets", "mosquito"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "PCOS – Lifestyle Basics (Educational)",
        "content": "Lifestyle measures such as balanced diet, physical activity and weight management (when indicated) are often part of PCOS care. Diagnosis requires clinical evaluation.",
        "content_hi": "PCOS में संतुलित आहार और व्यायाम सहायक हो सकते हैं। निदान डॉक्टर द्वारा।",
        "medical_system": "allopathy",
        "category": "disease",
        "tags": ["pcos", "hormones", "periods", "lifestyle"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Pediatric Fever – When to Seek Care",
        "content": "In infants under 3 months, any fever needs prompt medical evaluation. In older children, seek care for high fever, lethargy, rash, stiff neck, or breathing difficulty.",
        "content_hi": "3 महीने से छोटे शिशु में कोई भी बुखार तुरंत जाँच। बच्चों में तेज बुखार, सुस्ती, चकत्ते पर डॉक्टर।",
        "medical_system": "allopathy",
        "category": "emergency",
        "tags": ["pediatric", "fever", "child", "infant", "baccha"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Pregnancy – Red Flags (Educational)",
        "content": "Seek urgent care for vaginal bleeding, severe headache, vision changes, severe abdominal pain, reduced fetal movements, or seizures during pregnancy.",
        "content_hi": "गर्भावस्था में खून आना, तेज सिरदर्द, दृष्टि समस्या, पेट दर्द, भ्रूण की हलचल कम होना — तुरंत अस्पताल।",
        "medical_system": "allopathy",
        "category": "emergency",
        "tags": ["pregnancy", "pregnant", "bleeding", "garbh"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
    {
        "title": "Drug Safety – Basic Principles",
        "content": "Never share prescription medicines. Inform clinicians about all drugs and supplements. This system does not recommend dosages or specific medications.",
        "content_hi": "नुस्खे की दवाएँ साझा न करें। सभी दवाओं की जानकारी डॉक्टर को दें। यह सिस्टम खुराक नहीं बताता।",
        "medical_system": "allopathy",
        "category": "safety",
        "tags": ["drug", "medicine", "dosage", "safety", "dawai"],
        "source": "educational-synthetic",
        "evidence_level": "educational",
    },
]


def seed_knowledge(db: Session) -> int:
    existing = db.query(KnowledgeDocument).count()
    if existing > 0:
        return 0
    for item in SEED_DOCS:
        doc = KnowledgeDocument(**item)
        db.add(doc)
    db.commit()
    return len(SEED_DOCS)
