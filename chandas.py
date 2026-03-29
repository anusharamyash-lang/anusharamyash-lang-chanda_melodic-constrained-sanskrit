# Sanskrit vowel classification
short_vowels = ["अ","इ","उ","ऋ"]
long_vowels = ["आ","ई","ऊ","ए","ऐ","ओ","औ"]
def split_syllables(text):

    syllables = []
    current = ""

    matras = ["ा","ि","ी","ु","ू","े","ै","ो","ौ"]

    for char in text:

        current += char

        if char in matras:
            syllables.append(current)
            current = ""

    if current:
        syllables.append(current)

    return syllables
def detect_laghu_guru(syllables):

    pattern = []

    long_markers = ["ा","ी","ू","े","ै","ो","ौ"]

    for syllable in syllables:

        if any(marker in syllable for marker in long_markers):
            pattern.append("Guru")
        else:
            pattern.append("Laghu")

    return pattern
def detect_meter(pattern):

    pattern_str = "".join(["G" if p == "Guru" else "L" for p in pattern])

    if pattern_str.startswith("LGGLGLGG"):
        return "Anushtubh"

    if pattern_str.startswith("GGLLGLGGLGG"):
        return "Trishtubh"

    if pattern_str.startswith("GLGLGLGLGLGL"):
        return "Jagati"

    return "Unknown Meter"
def analyze_chandas(text):

    syllables = split_syllables(text)

    pattern = detect_laghu_guru(syllables)

    meter = detect_meter(pattern)

    return syllables, pattern, meter