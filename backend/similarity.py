import re
import math
from typing import List, Dict, Any, Tuple

def normalize_text(text: str) -> str:
    """Normalize text: lowercase, remove punctuation noise, normalize spaces."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase words/alphanumeric tokens."""
    return re.findall(r'\b\w+\b', text.lower())

def get_ngrams(tokens: List[str], n: int = 5) -> List[Tuple[str, ...]]:
    """Generate n-grams from a list of tokens."""
    if len(tokens) < n:
        return [tuple(tokens)] if tokens else []
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences preserving sentence boundaries."""
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences

def levenshtein_similarity(s1: str, s2: str) -> float:
    """Calculates character-level Levenshtein similarity ratio between two strings."""
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    len1, len2 = len(s1), len(s2)
    # Fast DP table approach for string comparison
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution
            )
    distance = dp[len1][len2]
    max_len = max(len1, len2)
    return 1.0 - (distance / max_len)

def compute_jaccard_similarity(tokens1: List[str], tokens2: List[str]) -> float:
    """Calculates Jaccard similarity between two token sets."""
    set1, set2 = set(tokens1), set(tokens2)
    if not set1 or not set2:
        return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def compute_cosine_similarity(text1: str, text2: str) -> float:
    """Compute TF-IDF Cosine Similarity between two texts."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        if not text1.strip() or not text2.strip():
            return 0.0
            
        vectorizer = TfidfVectorizer(stop_words=None, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(sim)
    except Exception:
        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)
        return compute_jaccard_similarity(tokens1, tokens2)

def filter_bibliography(text: str) -> str:
    """Strips bibliography/references section at the end of academic document."""
    patterns = [
        r'(?i)\n\s*(daftar pustaka|references|bibliography|referensi)\s*\n.*$',
        r'(?i)\n\s*bab\s+[v|vi|vii|5|6|7]*\s*\n\s*(daftar pustaka|referensi)\s*\n.*$'
    ]
    filtered = text
    for p in patterns:
        filtered = re.sub(p, '', filtered, flags=re.DOTALL)
    return filtered.strip()

def filter_quotes(text: str) -> str:
    """Strips direct quote text enclosed in quotes ("...", «...», etc.)."""
    # Remove text inside double quotes or guillemets
    filtered = re.sub(r'"[^"]*"', '', text)
    filtered = re.sub(r'«[^»]*»', '', filtered)
    filtered = re.sub(r'“[^”]*”', '', filtered)
    return filtered

def analyze_plagiarism(
    target_text: str,
    corpus_docs: List[Dict[str, Any]],
    n_gram_size: int = 5,
    exclude_bibliography: bool = True,
    exclude_quotes: bool = True,
    exclude_sources: bool = False,
    exclude_matches: bool = False
) -> Dict[str, Any]:
    """
    High-Precision Enterprise Similarity Engine with Exclusion Filters.
    Filters:
      - exclude_bibliography: Removes Daftar Pustaka / References section
      - exclude_quotes: Removes quoted sentences ("...")
      - exclude_sources: Excludes small sources < 1% contribution
      - exclude_matches: Excludes small sentence matches < 5 words
    """
    processed_text = target_text
    if exclude_bibliography:
        processed_text = filter_bibliography(processed_text)
    if exclude_quotes:
        processed_text = filter_quotes(processed_text)

    if not processed_text.strip():
        processed_text = target_text # Fallback if filtering cleared all text

    sentences = split_into_sentences(processed_text)
    total_tokens = tokenize(processed_text)
    total_word_count = len(total_tokens)

    COLOR_PALETTE = [
        "#E53E3E", # Red
        "#3182CE", # Blue
        "#38A169", # Green
        "#805AD5", # Purple
        "#DD6B20", # Orange
        "#319795", # Teal
        "#D69E2E", # Yellow
        "#D53F8C", # Pink
    ]

    source_color_map = {}
    for idx, doc in enumerate(corpus_docs):
        source_color_map[doc['id']] = COLOR_PALETTE[idx % len(COLOR_PALETTE)]

    annotated_sentences = []
    source_match_counts = {doc['id']: 0 for doc in corpus_docs}
    source_words_matched = {doc['id']: 0 for doc in corpus_docs}
    source_snippets_map = {doc['id']: [] for doc in corpus_docs}
    
    overall_matched_words = 0

    for sentence in sentences:
        sent_tokens = tokenize(sentence)
        # Check exclude matches filter threshold (< 5 words)
        min_words_threshold = 5 if exclude_matches else 3
        if len(sent_tokens) < min_words_threshold:
            annotated_sentences.append({
                "text": sentence,
                "matched": False,
                "source_id": None,
                "source_title": None,
                "similarity": 0.0,
                "color": None
            })
            continue

        best_match_doc = None
        best_matched_c_sent = None
        best_sim = 0.0

        target_ngrams_3 = set(get_ngrams(sent_tokens, 3))
        target_ngrams_5 = set(get_ngrams(sent_tokens, 5))

        for doc in corpus_docs:
            doc_text = doc.get('text', doc.get('text_content', ''))
            doc_sentences = split_into_sentences(doc_text)
            if not doc_sentences:
                continue

            sent_token_set = set(sent_tokens)
            for c_sent in doc_sentences:
                c_tokens = tokenize(c_sent)
                if len(c_tokens) < 3:
                    continue

                c_token_set = set(c_tokens)
                overlap_words = sent_token_set.intersection(c_token_set)
                if not overlap_words:
                    continue # Fast Short-Circuit: Skip zero overlap sentences instantly!

                c_ngrams_3 = set(get_ngrams(c_tokens, 3))
                c_ngrams_5 = set(get_ngrams(c_tokens, 5))

                ngram_3_sim = len(target_ngrams_3.intersection(c_ngrams_3)) / len(target_ngrams_3) if target_ngrams_3 else 0.0
                ngram_5_sim = len(target_ngrams_5.intersection(c_ngrams_5)) / len(target_ngrams_5) if target_ngrams_5 else 0.0
                ngram_sim = (ngram_3_sim * 0.4) + (ngram_5_sim * 0.6)

                jaccard_sim = len(overlap_words) / len(sent_token_set.union(c_token_set))

                cos_sim = 0.0
                if jaccard_sim > 0.25 or ngram_sim > 0.25:
                    cos_sim = compute_cosine_similarity(sentence, c_sent)

                lev_sim = 0.0
                if jaccard_sim > 0.4 and len(sentence) < 150 and len(c_sent) < 150:
                    lev_sim = levenshtein_similarity(normalize_text(sentence), normalize_text(c_sent))

                combined_score = max(
                    ngram_sim * 0.9,
                    cos_sim,
                    (jaccard_sim * 0.6 + cos_sim * 0.4),
                    lev_sim
                )

                if combined_score > 0.38 and combined_score > best_sim:
                    best_sim = combined_score
                    best_match_doc = doc
                    best_matched_c_sent = c_sent

        if best_match_doc and best_sim >= 0.40:
            doc_id = best_match_doc['id']
            color = source_color_map[doc_id]
            
            source_match_counts[doc_id] += 1
            source_words_matched[doc_id] += len(sent_tokens)
            overall_matched_words += len(sent_tokens)

            if doc_id not in source_snippets_map:
                source_snippets_map[doc_id] = []
            if best_matched_c_sent and best_matched_c_sent not in source_snippets_map[doc_id]:
                source_snippets_map[doc_id].append(best_matched_c_sent)

            annotated_sentences.append({
                "text": sentence,
                "matched": True,
                "source_id": doc_id,
                "source_title": best_match_doc.get('title', f"Dokumen #{doc_id}"),
                "source_author": best_match_doc.get('author', 'Unknown'),
                "matched_reference_text": best_matched_c_sent,
                "similarity": round(best_sim * 100, 1),
                "color": color
            })
        else:
            annotated_sentences.append({
                "text": sentence,
                "matched": False,
                "source_id": None,
                "source_title": None,
                "matched_reference_text": None,
                "similarity": 0.0,
                "color": None
            })

    sources_summary = []
    min_source_pct = 1.0 if exclude_sources else 0.0
    for doc in corpus_docs:
        doc_id = doc['id']
        words_matched = source_words_matched[doc_id]
        percentage = round((words_matched / total_word_count) * 100, 1) if total_word_count > 0 else 0.0

        if percentage > min_source_pct:
            sources_summary.append({
                "id": doc_id,
                "title": doc.get('title', f"Dokumen #{doc_id}"),
                "author": doc.get('author', 'Unknown'),
                "institution": doc.get('institution', 'Internet Source / Local Repository'),
                "percentage": percentage,
                "words_matched": words_matched,
                "matched_snippets": source_snippets_map.get(doc_id, []),
                "color": source_color_map[doc_id]
            })

    sources_summary.sort(key=lambda x: x['percentage'], reverse=True)
    overall_percentage = round((overall_matched_words / total_word_count * 100), 1) if total_word_count > 0 else 0.0

    return {
        "similarity_score": min(overall_percentage, 100.0),
        "total_words": total_word_count,
        "matched_words": overall_matched_words,
        "sources": sources_summary,
        "annotated_sentences": annotated_sentences
    }
