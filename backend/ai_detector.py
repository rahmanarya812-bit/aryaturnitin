import re
import math
from typing import List, Dict, Any, Tuple

# Enterprise 100+ AI Phrasing Markers & Structural Syntactic Connectors (ID & EN)
AI_TRANSITION_MARKERS = [
    r"\b(secara umum|dapat disimpulkan bahwa|penting untuk dicatat|dalam era digital|tidak dapat dipungkiri|pada dasarnya|sebagai kesimpulan|dalam konteks ini|di sisi lain|perlu diingat bahwa|memiliki peran penting|dalam upaya untuk|hal meunjukkan bahwa|berdasarkan hal tersebut|secara keseluruhan|merupakan salah satu|sangat penting untuk|dalam kehidupan sehari-hari|seiring berjalannya waktu|perlu digarisbawahi|dapat dikatakan bahwa|oleh sebab itu|berdasarkan uraian di atas|memegang peranan kunci|memberikan kontribusi signifikan)\b",
    r"\b(it is important to note|in conclusion|furthermore|moreover|delve into|tapestry|testament|crucial role|play a pivotal role|it is worth noting|in summary|as a result|consequently|it goes without saying|in the realm of|shed light on|a myriad of|spearhead|foster a culture|game changer|beacon of hope|pave the way|paramount importance|ever-evolving landscape)\b",
    r"\b(berdasarkan analisis|dalam hal ini|oleh karena itu|dengan demikian|diharapkan dapat|sebagaimana kita ketahui|tentu saja|dengan kata lain|dalam menghadapi tantangan|solusi yang efektif|langkah strategis|dampak positif|memberikan pemahaman|meningkatkan efisiensi|mengoptimalkan proses)\b"
]

def calculate_perplexity_proxy(tokens: List[str]) -> float:
    """
    Calculates pseudo-perplexity entropy of unigrams & bigrams.
    AI generated text has LOW perplexity (highly predictable word transitions).
    """
    if not tokens:
        return 10.0
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    
    entropy = 0.0
    total = len(tokens)
    for t, count in freq.items():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def calculate_burstiness(sentence_lengths: List[int]) -> float:
    """
    Calculates sentence length variance (Burstiness).
    AI text has low burstiness (uniform, balanced sentence lengths).
    Human writing has high burstiness (mix of short punchy & long complex sentences).
    """
    if len(sentence_lengths) < 2:
        return 0.5
    mean = sum(sentence_lengths) / len(sentence_lengths)
    variance = sum((x - mean) ** 2 for x in sentence_lengths) / len(sentence_lengths)
    std_dev = math.sqrt(variance)
    if mean == 0:
        return 0.0
    return std_dev / mean

def detect_ai_generated_text(text: str) -> Dict[str, Any]:
    """
    Enterprise Grade AI Writing Detection Engine.
    Evaluates:
      1. Perplexity Entropy & Token Uniformity
      2. Burstiness Index (Sentence Length Variance)
      3. Type-Token Ratio (Lexical Richness)
      4. Syntactic LLM Marker Lexicon
    """
    if not text or not text.strip():
        return {
            "ai_score": 0.0,
            "perplexity_index": 0.0,
            "burstiness_index": 0.0,
            "total_sentences": 0,
            "ai_sentences_count": 0,
            "annotated_ai_sentences": []
        }

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if not sentences:
        return {
            "ai_score": 0.0,
            "perplexity_index": 0.0,
            "burstiness_index": 0.0,
            "total_sentences": 0,
            "ai_sentences_count": 0,
            "annotated_ai_sentences": []
        }

    all_tokens = re.findall(r'\b\w+\b', text.lower())
    sentence_lengths = [len(s.split()) for s in sentences]
    
    perplexity = calculate_perplexity_proxy(all_tokens)
    burstiness = calculate_burstiness(sentence_lengths)

    annotated_sentences = []
    ai_sentence_count = 0

    for sent in sentences:
        words = sent.split()
        word_count = len(words)
        if word_count < 3:
            annotated_sentences.append({
                "text": sent,
                "ai_probability": 0.0,
                "is_ai": False
            })
            continue

        base_score = 0.30

        # 1. Check Syntactic AI Transition Markers
        marker_hits = 0
        for pattern in AI_TRANSITION_MARKERS:
            matches = re.findall(pattern, sent, re.IGNORECASE)
            marker_hits += len(matches)

        if marker_hits > 0:
            base_score += min(0.35 * marker_hits, 0.55)

        # 2. Balanced Sentence Length Check (AI sweet-spot: 12-25 words)
        if 12 <= word_count <= 26:
            base_score += 0.15

        # 3. Lexical Type-Token Ratio (TTR)
        unique_ratio = len(set(w.lower() for w in words)) / word_count
        if 0.65 <= unique_ratio <= 0.88:
            base_score += 0.15

        # 4. Global Low Burstiness Penalty
        if burstiness < 0.45:
            base_score += 0.12

        # 5. Low Perplexity Entropy Penalty
        if perplexity < 4.8 and word_count > 8:
            base_score += 0.15

        ai_prob = min(max(base_score, 0.0), 0.99)
        is_ai = ai_prob >= 0.52

        if is_ai:
            ai_sentence_count += 1

        annotated_sentences.append({
            "text": sent,
            "ai_probability": round(ai_prob * 100, 1),
            "is_ai": is_ai
        })

    overall_ai_score = round((ai_sentence_count / len(sentences)) * 100, 1)

    return {
        "ai_score": overall_ai_score,
        "perplexity_index": round(perplexity, 2),
        "burstiness_index": round(burstiness, 2),
        "total_sentences": len(sentences),
        "ai_sentences_count": ai_sentence_count,
        "annotated_ai_sentences": annotated_sentences
    }
