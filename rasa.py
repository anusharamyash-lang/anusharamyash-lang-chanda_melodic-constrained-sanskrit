def detect_rasa(text):

    rasa_keywords = {

        "Shringara": ["प्रेम", "प्रिय", "सुन्दरी"],
        "Hasya": ["हास", "हसति"],
        "Karuna": ["दुःख", "विलाप"],
        "Raudra": ["क्रोध", "रक्त"],
        "Veera": ["वीर", "युद्ध"],
        "Bhayanaka": ["भय"],
        "Bibhatsa": ["घृणा"],
        "Adbhuta": ["अद्भुत"],
        "Shanta": ["योग", "ध्यान"]
    }

    scores = {rasa: 0 for rasa in rasa_keywords}

    # ✅ FIXED PART
    words = text.split()

    for rasa, keywords in rasa_keywords.items():
        for keyword in keywords:
            if keyword in words:
                scores[rasa] += 1

    return max(scores, key=scores.get)
def apply_rasa_style(text, rasa):

    if rasa == "Shanta":
        return text + " ..."   # calm, slow

    if rasa == "Veera":
        return text.upper()   # strong emphasis

    if rasa == "Karuna":
        return text + " .. .."  # soft pauses

    return text