import streamlit as st
from gtts import gTTS
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
import os
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="ChandaPitch", page_icon="🕉", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {background-color:#0f172a; color:white;}
.main-title {
font-size:40px; text-align:center; font-weight:bold; color:#f59e0b;
}
.pattern-box {
display:inline-block; padding:8px 14px; margin:3px;
border-radius:6px; font-weight:bold;
}
.guru {background:#f97316; color:white;}
.laghu {background:#0ea5e9; color:white;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">ChandaPitch 🔱</div>', unsafe_allow_html=True)

# ---------------- SANSKRIT LOGIC ----------------
VOWELS = "अआइईउऊऋएऐओऔ"
LONG_VOWELS = "आईऊएऐओऔ"

def clean_text(text):
    return re.sub(r"[^\u0900-\u097F ]", "", text)

def split_syllables(text):
    syllables = []
    current = ""

    for ch in text:
        current += ch
        if ch in VOWELS:
            syllables.append(current.strip())
            current = ""

    if current:
        syllables.append(current)

    return syllables

def analyze_chandas(verse):
    verse = clean_text(verse)
    syllables = split_syllables(verse)

    pattern = []
    for syl in syllables:
        if any(v in syl for v in LONG_VOWELS):
            pattern.append("Guru")
        else:
            pattern.append("Laghu")

    count = len(pattern)

    if count == 8:
        meter = "Anushtubh"
    elif count == 24:
        meter = "Gayatri"
    elif count == 11:
        meter = "Trishtubh"
    else:
        meter = f"Custom ({count})"

    return syllables, pattern, meter

def detect_rasa(text):
    text = text.lower()

    if any(w in text for w in ["राम","कृष्ण","नारायण","गोविन्द"]):
        return "Bhakti"
    elif any(w in text for w in ["युद्ध","वीर","बल"]):
        return "Veera"
    elif any(w in text for w in ["शान्त","शांति"]):
        return "Shanta"
    elif any(w in text for w in ["प्रेम","मधुर"]):
        return "Shringara"
    else:
        return "Neutral"

# ---------------- AUDIO ----------------
def generate_normal_audio(text):
    file = "normal.mp3"
    tts = gTTS(text, lang='hi')
    tts.save(file)
    return file

def generate_chanted_audio(syllables, pattern):

    base_pitch_pattern = [0,2,3,2,1,0,-1,0]
    final_audio = AudioSegment.empty()

    for i, word in enumerate(syllables):

        tts = gTTS(word, lang='hi')
        f1 = f"temp_{i}.mp3"
        tts.save(f1)

        y, sr = librosa.load(f1)

        if np.max(np.abs(y)) != 0:
            y = y / np.max(np.abs(y))

        pitch = base_pitch_pattern[i % len(base_pitch_pattern)]
        y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch)

        if pattern[i] == "Guru":
            y = librosa.effects.time_stretch(y, rate=0.9)
            pause = 120
        else:
            y = librosa.effects.time_stretch(y, rate=1.1)
            pause = 60

        f2 = f"mod_{i}.wav"
        sf.write(f2, y, sr)

        seg = AudioSegment.from_wav(f2)
        final_audio += seg + AudioSegment.silent(duration=pause)

        os.remove(f1)
        os.remove(f2)

    output = "final.wav"
    final_audio.export(output, format="wav")
    return output

# ---------------- UI ----------------
st.write("Enter Sanskrit verse")

examples = {
    "Gita": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
    "Ramayana": "रामो विग्रहवान् धर्मः",
    "Peace": "सर्वे भवन्तु सुखिनः"
}

choice = st.selectbox("Example", list(examples.keys()))

if st.button("Load Example"):
    st.session_state.verse = examples[choice]

if "verse" not in st.session_state:
    st.session_state.verse = ""

verse = st.text_area("Verse", value=st.session_state.verse)
st.session_state.verse = verse

if st.button("Generate"):

    if verse.strip() == "":
        st.warning("Enter verse")
    else:
        syllables, pattern, meter = analyze_chandas(verse)
        rasa = detect_rasa(verse)

        st.subheader("Analysis")
        st.write("Meter:", meter)
        st.write("Rasa:", rasa)

        # Pattern
        st.subheader("Pattern")
        html = ""
        for p in pattern:
            if p == "Guru":
                html += '<span class="pattern-box guru">G</span>'
            else:
                html += '<span class="pattern-box laghu">L</span>'
        st.markdown(html, unsafe_allow_html=True)

        # Graph
        st.subheader("Pitch")
        pitch = [2 if p=="Guru" else 1 for p in pattern]
        st.line_chart(pitch)

        # AUDIO 1
        st.subheader("Original Pronunciation")
        normal = generate_normal_audio(verse)
        st.audio(open(normal,"rb").read())

        # AUDIO 2
        st.subheader("Chanted Output")
        chant = generate_chanted_audio(syllables, pattern)
        st.audio(open(chant,"rb").read())