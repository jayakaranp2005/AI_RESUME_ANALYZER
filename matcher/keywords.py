"""
Keywords extraction module for matching resume text against JD keywords.
Implements phrase scanning using JD keywords as phrase list and unigram extraction.
"""

import re
from config import STOPWORDS, FILLER_WORDS


def extract_resume_keywords(resume_text, jd_keywords):
    """
    Extract keywords from resume text using phrase scanning and unigram extraction.
    
    Process:
    1. Lowercase the resume text
    2. Phrase scanning - exact phrase match in full text
    3. Component word matching - all words of phrase present as unigrams
    4. Unigram extraction with stopword/filler filtering
    5. Plural/singular normalization
    6. Substring check for merged PDF words
    7. Combine all matches
    
    Args:
        resume_text (str): Raw resume text
        jd_keywords (set): Set of keywords from job description
                          (used as phrase list for multi-word matches)
                          
    Returns:
        set: Set of extracted keywords found in resume
             Example: {"python", "machine learning", "aws"}
    """

    if not resume_text or not resume_text.strip():
        return set()

    if not jd_keywords:
        return set()

    # Step 1 — Lowercase
    lowercased = resume_text.lower()

    # ════════════════════════════════════════════════════════════════
    # Step 2 — UNIGRAM EXTRACTION
    # ════════════════════════════════════════════════════════════════
    pattern = r'\b[a-z][a-z0-9+#.]*(?:-[a-z0-9]+)*\b'
    raw_tokens = re.findall(pattern, lowercased)
    unigrams = {
        t for t in raw_tokens
        if t not in STOPWORDS and t not in FILLER_WORDS and len(t) >= 2
    }

    # ════════════════════════════════════════════════════════════════
    # Step 3 — MATCH JD KEYWORDS AGAINST RESUME (5 checks)
    # ════════════════════════════════════════════════════════════════
    matched_keywords = set()

    for jd_kw in jd_keywords:
        jd_kw_lower = jd_kw.lower().strip()
        words = jd_kw_lower.split()

        # Check 1 — exact phrase in full text
        if jd_kw_lower in lowercased:
            matched_keywords.add(jd_kw)
            continue

        # Check 2 — all component words present as unigrams
        if len(words) > 1 and all(w in unigrams for w in words):
            matched_keywords.add(jd_kw)
            continue

        # Check 3 — single word direct unigram match
        if len(words) == 1 and jd_kw_lower in unigrams:
            matched_keywords.add(jd_kw)
            continue

        # Check 4 — plural/singular normalization
        if len(words) == 1:
            singular = jd_kw_lower.rstrip('s')
            plural   = jd_kw_lower + 's'
            if singular in unigrams or plural in unigrams:
                matched_keywords.add(jd_kw)
                continue

        # Check 5 — substring check for merged PDF words
        for token in unigrams:
            if jd_kw_lower in token and len(jd_kw_lower) > 3:
                matched_keywords.add(jd_kw)
                break

    return matched_keywords