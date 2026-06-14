"""
Export module for converting analysis results to CSV format.
"""

import pandas as pd
from config import CSV_COLUMNS


def export_results_to_csv(ranked_results):
    """
    Export ranked resume analysis results to CSV bytes.
    
    Args:
        ranked_results (list): List of ranked result dictionaries
                              Each dict should have: filename, score, label,
                              matched_keywords, missing_keywords, strength_keywords, rank
                              
    Returns:
        bytes: CSV content as UTF-8 encoded bytes, ready for Streamlit download
               Columns: Rank, Filename, Score, Label, Matched Skills, Missing Skills, Strengths
               
    Raises:
        ValueError: If results list is empty or malformed
    """
    
    if not ranked_results:
        raise ValueError("No results to export")
    
    # ════════════════════════════════════════════════════════════════
    # Convert result dicts to DataFrame format
    # ════════════════════════════════════════════════════════════════
    
    data_for_df = []
    
    for result in ranked_results:
        # Convert sets to comma-separated strings
        matched_skills = ', '.join(sorted(result['matched_keywords'])) if result['matched_keywords'] else ""
        missing_skills = ', '.join(sorted(result['missing_keywords'])) if result['missing_keywords'] else ""
        strengths = ', '.join(sorted(result['strength_keywords'])) if result['strength_keywords'] else ""
        
        row = {
            "Rank": result['rank'],
            "Filename": result['filename'],
            "Score": result['score'],
            "Label": result['label'],
            "Matched Skills": matched_skills,
            "Missing Skills": missing_skills,
            "Strengths": strengths
        }
        
        data_for_df.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data_for_df)
    
    # Ensure columns are in the correct order
    df = df[CSV_COLUMNS]
    
    # ════════════════════════════════════════════════════════════════
    # Convert to CSV bytes
    # ════════════════════════════════════════════════════════════════
    
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    
    return csv_bytes
