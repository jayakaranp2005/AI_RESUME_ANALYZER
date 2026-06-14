"""
AI suggestions module for generating improvement suggestions using Google Gemini API.
Makes ONE Gemini API call to generate suggestions for top 5 moderate candidates.
"""

import json
import google.generativeai as genai


def generate_ai_suggestions(top_moderate_candidates, jd_keywords, gemini_key_2):
    """
    Generate AI improvement suggestions for top moderate candidates using Gemini API (Account 2).
    
    Only runs if moderate candidates exist.
    Makes ONE API call with all candidates at once.
    
    Args:
        top_moderate_candidates (list): List of top 5 moderate result dicts
                                        Each dict has: filename, matched_keywords, missing_keywords
        jd_keywords (set): Set of keywords from job description
        gemini_key_2 (str): Second Gemini API key (for suggestions)
        
    Returns:
        dict: Mapping of filename -> list of 3 suggestions
              Example: {
                  "resume1.pdf": ["Suggestion 1", "Suggestion 2", "Suggestion 3"],
                  "resume2.pdf": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
              }
              Returns empty dict if no moderate candidates
              
    Raises:
        ValueError: If API key is missing
        Exception: If API call fails
    """
    
    # Early return if no moderate candidates
    if not top_moderate_candidates:
        return {}
    
    if not gemini_key_2:
        raise ValueError("GEMINI_KEY_2 environment variable is not set")
    
    # Configure Gemini API with second key
    genai.configure(api_key=gemini_key_2)
    
    # ════════════════════════════════════════════════════════════════
    # Build the candidates information for the prompt
    # ════════════════════════════════════════════════════════════════
    
    candidates_text = ""
    for idx, candidate in enumerate(top_moderate_candidates, 1):
        filename = candidate['filename']
        matched = ', '.join(sorted(candidate['matched_keywords'])) if candidate['matched_keywords'] else "None"
        missing = ', '.join(sorted(candidate['missing_keywords'])) if candidate['missing_keywords'] else "None"
        
        candidates_text += f"""Candidate {idx} - {filename}
  Has: {matched}
  Missing: {missing}

"""
    
    # Convert JD keywords to comma-separated string
    jd_keywords_str = ', '.join(sorted(jd_keywords))
    
    # ════════════════════════════════════════════════════════════════
    # Build the prompt
    # ════════════════════════════════════════════════════════════════
    
    prompt = f"""You are an expert resume coach. Analyze these candidates against the job requirements and give improvement suggestions.

Job requires: {jd_keywords_str}

Candidates:
{candidates_text}

For each candidate return exactly 3 bullet point suggestions that are specific and actionable.
Return ONLY a valid JSON object:
{{
  "filename1": ["suggestion1", "suggestion2", "suggestion3"],
  "filename2": ["suggestion1", "suggestion2", "suggestion3"]
}}

No explanation. No markdown. Just JSON."""
    
    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        
        # Make API call
        response = model.generate_content(prompt)
        
        # Get the response text
        response_text = response.text
        
        # Parse JSON response
        try:
            # Try to find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON object found in response")
            
            json_str = response_text[json_start:json_end]
            suggestions_data = json.loads(json_str)
            
            # Validate structure: should be {filename: [3 suggestions]}
            for filename, suggestions in suggestions_data.items():
                if not isinstance(suggestions, list):
                    raise ValueError(f"Suggestions for '{filename}' must be a list")
                if len(suggestions) != 3:
                    # If not exactly 3, take first 3 or pad with empty strings
                    suggestions_data[filename] = (suggestions[:3] + ["", "", ""])[:3]
            
            return suggestions_data
            
        except json.JSONDecodeError as e:
            raise Exception(
                f"Failed to parse Gemini API response as JSON: {str(e)}\n"
                f"Response was: {response_text}"
            )
    
    except Exception as e:
        raise Exception(f"Gemini API call for suggestions failed: {str(e)}")
