"""
Scoring and ranking module for resume analysis.
Calculates match scores, labels candidates, and ranks resumes by score.
"""

from config import STRONG_THRESHOLD, MODERATE_THRESHOLD, LABEL_COLORS


def score_resume(resume_keywords, jd_keywords, filename):
    """
    Calculate match score and metrics for a single resume.
    
    Args:
        resume_keywords (set): Keywords extracted from resume
        jd_keywords (set): Keywords from job description
        filename (str): Name of the resume file
        
    Returns:
        dict: Result object with keys:
              - filename: str
              - matched_keywords: set (intersection)
              - missing_keywords: set (in JD but not resume)
              - strength_keywords: set (in resume but not JD)
              - score: float (rounded to 2 decimals)
              - label: str ("Strong", "Moderate", "Weak")
              - rank: int (assigned during ranking)
    """
    
    # Calculate set intersections
    matched = resume_keywords.intersection(jd_keywords)
    missing = jd_keywords - resume_keywords
    strengths = resume_keywords - jd_keywords
    
    # Calculate score as percentage of matched keywords
    # score = len(matched) / len(jd_keywords) * 100
    if len(jd_keywords) > 0:
        score = round((len(matched) / len(jd_keywords)) * 100, 2)
    else:
        score = 0.0
    
    # Determine label based on score thresholds
    if score >= STRONG_THRESHOLD:
        label = "Strong"
    elif score >= MODERATE_THRESHOLD:
        label = "Moderate"
    else:
        label = "Weak"
    
    return {
        "filename": filename,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "strength_keywords": strengths,
        "score": score,
        "label": label,
        "rank": None  # Will be assigned during ranking
    }


def rank_results(result_dicts):
    """
    Rank resumes by score (descending) and assign rank numbers.
    
    Args:
        result_dicts (list): List of result dictionaries from score_resume()
        
    Returns:
        list: Sorted list of result dicts with 'rank' field populated
              Sorted by score descending (highest score = rank 1)
    """
    
    if not result_dicts:
        return []
    
    # Sort by score descending
    sorted_results = sorted(result_dicts, key=lambda x: x['score'], reverse=True)
    
    # Assign rank numbers
    for rank, result in enumerate(sorted_results, start=1):
        result['rank'] = rank
    
    return sorted_results


def get_top_moderate_candidates(ranked_results, top_n=5):
    """
    Extract top N moderate candidates for AI suggestions.
    
    Args:
        ranked_results (list): Ranked result dictionaries (from rank_results())
        top_n (int): Number of top moderate candidates to select (default: 5)
        
    Returns:
        list: List of moderate candidates, sorted by score (descending)
              Only includes candidates with label == "Moderate"
              Returns up to top_n candidates (may be fewer if less than top_n exist)
    """
    
    # Filter for moderate candidates
    moderate_candidates = [r for r in ranked_results if r['label'] == "Moderate"]
    
    # Already sorted by score from rank_results(), take top N
    return moderate_candidates[:top_n]


def format_label_with_color(label):
    """
    Format label with emoji color indicator.
    
    Args:
        label (str): Label ("Strong", "Moderate", "Weak")
        
    Returns:
        str: Formatted label with emoji (e.g., "🟢 Strong")
    """
    
    color = LABEL_COLORS.get(label, "")
    return f"{color} {label}"
