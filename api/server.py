import json
import os
import urllib.request
import urllib.parse
import base64
from gtts import gTTS
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Custom Override Dictionary
EASY_WORDS_MAP = {
    "structural": "basic",
    "paradigms": "ways of working",
    "synergistic": "helpful",
    "efficiencies": "saves time",
    "suboptimal": "bad",
    "outcome": "result",
    "cognitive": "thinking",
    "fatigue": "tiredness",
    "temporary": "short",
    "cessation": "stop",
    "labor": "work",
    "imperative": "very important",
    "utilize": "use",
    "expedite": "speed up",
}

# --- Smart Synonym Finder ---
def get_two_simplest_synonyms(word):
    clean_word = "".join(c for c in word if c.isalpha()).lower()
    if not clean_word:
        return [word]
        
    results = []
    
    url_syn = f"https://api.datamuse.com/words?rel_syn={clean_word}&md=f&max=10"
    try:
        req = urllib.request.Request(url_syn, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            results.extend(json.loads(response.read().decode()))
    except Exception as e:
        print(f"Direct synonym lookup failed: {e}")
        
    if len(results) < 5:
        url_ml = f"https://api.datamuse.com/words?ml={clean_word}&md=f&max=15"
        try:
            req = urllib.request.Request(url_ml, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                ml_data = json.loads(response.read().decode())
                existing = {r['word'].lower() for r in results}
                for item in ml_data:
                    if item['word'].lower() not in existing:
                        results.append(item)
        except Exception as e:
            print(f"Means-like fallback failed: {e}")

    valid_candidates = []
    for item in results:
        syn = item['word'].lower()
        if syn == clean_word:
            continue
        freq = 0.0
        tags = item.get('tags', [])
        for tag in tags:
            if tag.startswith('f:'):
                freq = float(tag.split(':')[1])
        valid_candidates.append((item['word'], freq))
        
    valid_candidates.sort(key=lambda x: x[1], reverse=True)
    
    top_synonyms = []
    for syn, freq in valid_candidates:
        if syn.lower() not in [s.lower() for s in top_synonyms]:
            top_synonyms.append(syn)
        if len(top_synonyms) == 2:
            break
            
    return top_synonyms if top_synonyms else ["no simpler word found"]

def get_single_simplest_synonym(word):
    syns = get_two_simplest_synonyms(word)
    return syns[0] if syns else word

def simplify_paragraph(text):
    words = text.split()
    simplified_words = []
    for word in words:
        clean_word = word.rstrip(".,!?;:\"'")
        punctuation = word[len(clean_word):]
        lowered = clean_word.lower()
        if lowered in EASY_WORDS_MAP:
            replacement = EASY_WORDS_MAP[lowered]
        elif len(lowered) > 6 and clean_word.isalpha(): 
            replacement = get_single_simplest_synonym(lowered)
        else:
            replacement = clean_word
        if clean_word.istitle() and replacement:
            replacement = replacement.capitalize()
        simplified_words.append(replacement + punctuation)
    return " ".join(simplified_words)

# --- API Endpoints ---
@app.route('/synonym', methods=['POST'])
def synonym_route():
    try:
        data = request.get_json()
        word = data.get('text', '').strip()
        if not word: return jsonify({"error": "No word"}), 400
        syns = get_two_simplest_synonyms(word)
        return jsonify({"result": ", ".join(syns)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pronounce', methods=['POST'])
def pronounce_route():
    try:
        data = request.get_json()
        word = data.get('text', '').strip()
        if not word: return jsonify({"error": "No word"}), 400
        tts = gTTS(text=word, lang='en')
        tts.save("/tmp/temp_audio.mp3") # Save to temp folder on Vercel
        with open("/tmp/temp_audio.mp3", "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        return jsonify({"audio": encoded})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/simplify', methods=['POST'])
def simplify_route():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        if not text: return jsonify({"error": "No text"}), 400
        return jsonify({"result": simplify_paragraph(text)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500