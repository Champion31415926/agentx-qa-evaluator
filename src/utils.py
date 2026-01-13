import string
def normalize_text(text: str) -> str:
    if not text: return ""
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())