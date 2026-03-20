from flask import Flask, render_template, request, jsonify
import requests, uuid, os, re

app = Flask(__name__)

# ================= ELEVENLABS FREE CONFIG ================
ELEVEN_API_KEY =("50ebb9d9ec802692ce2650d3e5d75d726456d27422f1f1a7fba885be28995edc")

# FREE voice: Rachel
VOICE_MAP = {
    "en": "ErXwobaYiN019PkySvjV",
    "hi": "EXAVITQu4vr4xnSDxMaL",
    "te": "MF3mGyEYCl7XYWbV9V6O"
}


def remove_emojis(text):
    return re.sub(r'[^\w\s.,!?]', '', text)


def speak(text, lang):
    voice_id = VOICE_MAP.get(lang, VOICE_MAP["en"])
    clean_text = remove_emojis(text)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": clean_text,
        "model_id": "eleven_turbo_v2"  # FREE + Fast model
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        print("\n❌ ELEVENLABS ERROR:")
        print(response.status_code)
        print(response.text)
        return None

    filename = f"audio_{uuid.uuid4()}.mp3"
    filepath = os.path.join("static", filename)

    with open(filepath, "wb") as f:
        f.write(response.content)

    return f"/static/{filename}"


# =================== 20+ MOODS DETECTION ===================

MOODS = {
    "happy": {
        "k": ["happy", "joy", "excited", "glad", "cheerful", "delighted"],
        "en": ("😊 Happiness", "You feel joyful and bright today.", "Keep spreading positivity!"),
        "hi": ("😊 खुशी", "आप अच्छा और सकारात्मक महसूस कर रहे हैं।", "अपनी खुशी दूसरों से बाँटें!"),
        "te": ("😊 ఆనందం", "మీరు ఈ రోజు ఆనందంగా ఉన్నారు.", "ఈ ఆనందాన్ని పంచుకోండి!")
    },
    "sad": {
        "k": ["sad", "down", "depressed", "unhappy"],
        "en": ("😔 Sadness", "You seem emotionally low.", "Talk to someone you trust."),
        "hi": ("😔 उदासी", "आप दुखी लग रहे हैं।", "किसी भरोसेमंद से बात करें।"),
        "te": ("😔 బాధ", "మీరు దిగులుగా ఉన్నారు.", "ఎవరితోనైనా మాట్లాడండి.")
    },
    "anger": {
        "k": ["angry", "mad", "furious", "rage"],
        "en": ("😡 Anger", "Something triggered your frustration.", "Take deep breaths and relax."),
        "hi": ("😡 गुस्सा", "कुछ आपके लिए परेशान करने वाला है।", "थोड़ा शांति से सोचें।"),
        "te": ("😡 కోపం", "ఏదో మీను కోపానికి గురి చేసింది.", "श్వాస తీసుకోండి మరియు शांतంగా ఉండండి.")
    },
    "stress": {
        "k": ["stress", "tense", "pressure", "overwhelmed"],
        "en": ("😣 Stress", "Your mind feels overloaded.", "Slow down and breathe slowly."),
        "hi": ("😣 तनाव", "आपके मन पर बोझ है।", "आराम करें और गहरी साँस लें।"),
        "te": ("😣 ఒత్తిడి", "మీ మనసు ఒత్తిడిలో ఉంది.", "నెమ్మదిగా శ్వాస తీసుకోండి.")
    },
    "fear": {
        "k": ["fear", "scared", "afraid", "terrified"],
        "en": ("😨 Fear", "Something is making you uncomfortable.", "Stay close to someone you trust."),
        "hi": ("😨 डर", "कुछ आपको डरा रहा है।", "किसी भरोसेमंद को पास रखें।"),
        "te": ("😨 భయం", "ఏదో మీకు భయాన్ని కలిగిస్తోంది.", "నమ్మకమైన వ్యక్తితో ఉండండి.")
    },
    "lonely": {
        "k": ["lonely", "alone", "isolated"],
        "en": ("🧍 Loneliness", "You may be craving connection.", "Reach out to a friend."),
        "hi": ("🧍 अकेलापन", "आप भावनात्मक जुड़ाव चाह रहे हैं।", "किसी दोस्त से बात करें।"),
        "te": ("🧍 ఒంటరితనం", "మీకు ఎవరో కావాలి.", "ఒకరి తో మాట్లాడండి.")
    },
    "anxiety": {
        "k": ["anxiety", "worried", "nervous", "panic"],
        "en": ("😰 Anxiety", "Your thoughts seem restless.", "Take slow deep breaths."),
        "hi": ("😰 चिंता", "आपकी सोच तेज चल रही है।", "गहरी साँस लें।"),
        "te": ("😰 ఆందోళన", "మీ ఆలోచనలు వేగంగా ఉన్నాయి.", "నెమ్మదిగా శ్వాస తీసుకోండి.")
    },
    "bored": {
        "k": ["bored", "nothing to do", "lazy"],
        "en": ("😐 Boredom", "You feel unmotivated.", "Try doing something creative."),
        "hi": ("😐 बोरियत", "आप ऊब महसूस कर रहे हैं।", "कुछ रचनात्मक करने की कोशिश करें।"),
        "te": ("😐 బోర్ గా ఉంది", "మీకు ఆసక్తి లేదు.", "ఏదైనా కొత్త పని చేయండి.")
    },
    "love": {
        "k": ["love", "romantic", "affection"],
        "en": ("💖 Love", "You feel emotionally warm.", "Express your feelings openly."),
        "hi": ("💖 प्यार", "आप प्रेम महसूस कर रहे हैं।", "अपनी भावनाएँ व्यक्त करें।"),
        "te": ("💖 ప్రేమ", "మీరు ప్రేమలో ఉన్నారు.", "మీ భావాలను చెప్పండి.")
    },
    "confused": {
        "k": ["confused", "uncertain", "unsure"],
        "en": ("❓ Confusion", "You're unsure about something.", "Take time to think clearly."),
        "hi": ("❓ उलझन", "आप किसी चीज़ को लेकर अनिश्चित हैं।", "धीरे-धीरे सोचें।"),
        "te": ("❓ అయోమయం", "మీకు స్పష్టత లేదు.", "శాంతిగా ఆలోచించండి.")
    },
    "tired": {
        "k": ["tired", "exhausted", "fatigue"],
        "en": ("😴 Tiredness", "Your body or mind is exhausted.", "Get some rest."),
        "hi": ("😴 थकान", "आप थके हुए हैं।", "आराम करें।"),
        "te": ("😴 అలసట", "మీరు అలసిపోయారు.", "కొంచెం విశ్రాంతి తీసుకోండి.")
    },
    "motivated": {
        "k": ["motivated", "inspired", "determined"],
        "en": ("🔥 Motivation", "You feel driven and focused.", "Keep going, you're doing great!"),
        "hi": ("🔥 प्रेरणा", "आप प्रेरित महसूस कर रहे हैं।", "ऐसे ही आगे बढ़ते रहें!"),
        "te": ("🔥 ప్రేరణ", "మీకు జోష్ ఉంది.", "ఇలాగే ముందుకు సాగండి!")
    },
    "grateful": {
        "k": ["grateful", "thankful", "blessed"],
        "en": ("🙏 Gratitude", "You appreciate the good things in life.", "Keep this positive mindset."),
        "hi": ("🙏 कृतज्ञता", "आप आभारी महसूस कर रहे हैं।", "यह सकारात्मक सोच बनाए रखें।"),
        "te": ("🙏 కృతజ్ఞత", "మీరు కృతజ్ఞతతో ఉన్నారు.", "ఈ భావాన్ని కొనసాగించండి.")
    },
    "guilty": {
        "k": ["guilty", "regret", "remorse"],
        "en": ("😞 Guilt", "You feel responsible for something.", "Learn from mistakes and move on."),
        "hi": ("😞 अपराधबोध", "आपको किसी बात का पछतावा है।", "गलतियों से सीखें।"),
        "te": ("😞 నేరభావం", "మీకు పశ్చాత్తాపం ఉంది.", "ఇది నుంచి నేర్చుకోండి.")
    },
    "jealous": {
        "k": ["jealous", "envy"],
        "en": ("🟩 Jealousy", "You are comparing yourself with others.", "Focus on your journey."),
        "hi": ("🟩 जलन", "आप दूसरों से तुलना कर रहे हैं।", "अपने लक्ष्य पर ध्यान दें।"),
        "te": ("🟩 అసూయ", "మీరు ఎవరికో పోల్చుకుంటున్నారు.", "మీ మార్గం పై దృష్టి పెట్టండి.")
    },
    "proud": {
        "k": ["proud", "accomplished"],
        "en": ("🏆 Pride", "You achieved something meaningful.", "Celebrate your success!"),
        "hi": ("🏆 गर्व", "आपने कुछ हासिल किया है।", "अपनी सफलता का आनंद लें!"),
        "te": ("🏆 గర్వం", "మీరు ఏదో సాధించారు.", "ఆనందించండి!")
    },
    "hopeful": {
        "k": ["hopeful", "optimistic"],
        "en": ("🌈 Hope", "You believe good things will happen.", "Keep that hope alive."),
        "hi": ("🌈 आशा", "आप सकारात्मक सोच रहे हैं।", "यह सोच बनाए रखें।"),
        "te": ("🌈 ఆశ", "మీకు మంచి జరుగుతుందని నమ్మకముంది.", "దాన్ని కొనసాగించండి.")
    },
    "shy": {
        "k": ["shy", "awkward"],
        "en": ("😳 Shyness", "You feel hesitant.", "Take your time."),
        "hi": ("😳 शर्म", "आप झिझक महसूस कर रहे हैं।", "आराम से कदम बढ़ाएँ।"),
        "te": ("😳 సిగ్గు", "మీకు సంకోచం ఉంది.", "నెమ్మదిగా ముందుకు సాగండి.")
    },
    "surprised": {
        "k": ["surprised", "shocked", "wow"],
        "en": ("😮 Surprise", "Something unexpected happened!", "Take it positively."),
        "hi": ("😮 आश्चर्य", "कुछ अप्रत्याशित हुआ!", "इसे सकारात्मक रूप से लें।"),
        "te": ("😮 ఆశ్చర్యం", "ఏదో ఆశ్చర్యకరమైనది జరిగింది!", "దాన్ని సానుకూలంగా చూడండి.")
    }
}


# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/greet", methods=["POST"])
def greet():
    lang = request.json.get("lang", "en")

    greeting = {
        "en": "🙏 Namaste! I am your AI Human Behaviour Assistant.",
        "hi": "🙏 नमस्ते! मैं आपका AI व्यवहार सहायक हूँ।",
        "te": "🙏 నమస్కారం! నేను మీ AI ప్రవర్తనా సహాయకుడిని."
    }[lang]

    audio = speak(greeting, lang)
    return jsonify(text=greeting, audio=audio)


@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.json["text"].lower()
    lang = request.json["lang"]

    for mood, mood_data in MOODS.items():
        if any(keyword in text for keyword in mood_data["k"]):
            title, cause, advice = mood_data[lang]
            reply = f"{title}\nCause: {cause}\nAdvice: {advice}"

            audio = speak(reply, lang)
            return jsonify(text=reply, audio=audio)

    fallback = {
        "en": "🙂 Tell me more about how you're feeling.",
        "hi": "🙂 थोड़ा और बताएं कि आप कैसा महसूस कर रहे हैं।",
        "te": "🙂 మీ భావాలను ఇంకాస్త వివరించండి."
    }[lang]

    audio = speak(fallback, lang)
    return jsonify(text=fallback, audio=audio)


if __name__ == "__main__":
    app.run(debug=True)