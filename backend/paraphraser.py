import re
import random
from typing import Dict, Any

# Academic synonym replacement dictionary for Indonesian
INDONESIAN_SYNONYMS = {
    "secara signifikan": ["secara substansial", "secara bermakna", "secara nyata"],
    "memiliki peran penting": ["memegang peranan krusial", "memberikan kontribusi utama", "berperan vital"],
    "penting untuk dicatat": ["perlu diperhatikan", "patut digarisbawahi", "penting untuk dipahami"],
    "mengubah": ["mentransformasi", "memperbarui", "merevolusi"],
    "lanskap": ["tatanan", "kondisi", "struktur"],
    "pendidikan": ["dunia akademik", "sistem pembelajaran", "sektor pendidikan"],
    "penggunaan": ["pemanfaatan", "penerapan", "implementasi"],
    "memungkinkan": ["memberikan kemampuan bagi", "memfasilitasi", "memungkinkan terjadinya"],
    "menyesuaikan": ["mengadaptasikan", "menyelaraskan", "mengakomodasi"],
    "kecepatan": ["laju", "ritme", "tempo"],
    "individu": ["perorangan", "setiap orang", "masing-masing peserta"],
    "otomatisasi": ["otomasisasi", "sistem otomatis", "penilaian terotomatisasi"],
    "membantu": ["mempermudah", "mendukung", "membantu kerja"],
    "mengidentifikasi": ["mendeteksi", "menemukan", "menganalisis"],
    "kelemahan": ["kendala", "kekurangan", "titik lemah"],
    "presisi": ["akurat", "tepat sasaran", "cermat"],
    "tantangan": ["hambatan", "kendala", "isu strategis"],
    "mencakup": ["meliputi", "terdiri atas", "melibatkan"],
    "penerapan": ["implementasi", "aplikasi", "eksekusi"],
    "efektif": ["berdaya guna", "optimal", "mujarab"],
    "efisien": ["berhasil guna", "hemat sumber daya", "praktis"]
}

def paraphrase_sentence(sentence: str) -> str:
    """Paraphrases a single sentence by substituting synonyms and adjusting structure."""
    words = sentence.split()
    if len(words) < 3:
        return sentence

    paraphrased = sentence

    # Replace key phrases with academic synonyms
    for phrase, synonyms in INDONESIAN_SYNONYMS.items():
        if phrase in paraphrased.lower():
            chosen_synonym = random.choice(synonyms)
            # Match case of original phrase
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            paraphrased = pattern.sub(chosen_synonym, paraphrased, count=1)

    # Convert simple active structure to passive or vice versa if applicable
    paraphrased = re.sub(r'\bmemperluas\b', 'diperluas oleh', paraphrased, flags=re.IGNORECASE)
    paraphrased = re.sub(r'\bmeningkatkan\b', 'dioptimalkan untuk meningkatkan', paraphrased, flags=re.IGNORECASE)

    return paraphrased

def paraphrase_text(text: str) -> Dict[str, Any]:
    """
    Paraphrases multi-sentence text to lower plagiarism similarity scores.
    """
    if not text or not text.strip():
        return {
            "original_text": "",
            "paraphrased_text": "",
            "original_words": 0,
            "paraphrased_words": 0
        }

    raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    paraphrased_sentences = []

    for sent in raw_sentences:
        p_sent = paraphrase_sentence(sent)
        paraphrased_sentences.append(p_sent)

    result_text = " ".join(paraphrased_sentences)

    return {
        "original_text": text,
        "paraphrased_text": result_text,
        "original_words": len(text.split()),
        "paraphrased_words": len(result_text.split())
    }
