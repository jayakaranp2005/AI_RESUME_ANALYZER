"""
Keywords extraction module for matching resume text against JD keywords.
Implements phrase scanning using JD keywords as phrase list and unigram extraction.
"""

import re
from config import STOPWORDS, FILLER_WORDS


def extract_resume_keywords(resume_text, jd_keywords, jd_aliases=None):
    """
    Extract keywords from resume text using phrase scanning and unigram extraction.
    
    Process:
    1. Lowercase the resume text
    2. Phrase scanning - exact phrase match in full text
    3. Component word matching - all words of phrase present as unigrams
    4. Unigram extraction with stopword/filler filtering
    5. Plural/singular normalization
    6. Substring check for merged PDF words
    7. Alias matching - for unmatched keywords, try matching via aliases
    8. Combine all matches
    
    Args:
        resume_text (str): Raw resume text
        jd_keywords (set): Set of keywords from job description
                          (used as phrase list for multi-word matches)
        jd_aliases (dict, optional): Mapping of keywords to alias lists
                                    Example: {"llm": ["large language model"], ...}
                                    If None, alias matching is skipped
                          
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
    
    # ════════════════════════════════════════════════════════════════
    # Step 6 — ALIAS MATCHING (for unmatched keywords only)
    # ════════════════════════════════════════════════════════════════
    if jd_aliases:
        for jd_kw in jd_keywords:
            # Skip if already matched
            if jd_kw in matched_keywords:
                continue
            
            jd_kw_lower = jd_kw.lower().strip()
            
            # Look up aliases for this keyword
            alias_list = jd_aliases.get(jd_kw_lower, [])
            
            # Try to match each alias
            for alias in alias_list:
                alias_lower = alias.lower().strip()
                alias_words = alias_lower.split()
                
                # Alias Check 1 — exact alias phrase in lowercased resume text
                if alias_lower in lowercased:
                    matched_keywords.add(jd_kw)
                    break
                
                # Alias Check 2 — all alias words present as unigrams
                if len(alias_words) > 1 and all(w in unigrams for w in alias_words):
                    matched_keywords.add(jd_kw)
                    break
                
                # Alias Check 3 — single alias word in unigrams
                if len(alias_words) == 1 and alias_lower in unigrams:
                    matched_keywords.add(jd_kw)
                    break
                
                # Alias Check 4 — alias substring in merged PDF tokens (len > 3)
                for token in unigrams:
                    if alias_lower in token and len(alias_lower) > 3:
                        matched_keywords.add(jd_kw)
                        break
                
                # If this alias matched, break out of alias loop
                if jd_kw in matched_keywords:
                    break

    return matched_keywords