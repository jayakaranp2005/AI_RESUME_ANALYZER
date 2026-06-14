
"""
Job Description parser module for extracting keywords using Google Gemini API.
Makes ONE Gemini API call to extract all technical skills and keywords from JD.
"""

import json
import google.generativeai as genai


def extract_jd_keywords(jd_text, gemini_key_1):
    """
    Extract keywords and aliases from job description using Google Gemini API (Account 1).
    
    Args:
        jd_text (str): Raw job description text
        gemini_key_1 (str): First Gemini API key (for JD keyword extraction)
        
    Returns:
        tuple: (jd_keywords, jd_aliases) where:
               - jd_keywords (set): Set of extracted keywords from JD
                 Example: {"python", "machine learning", "docker", "aws"}
               - jd_aliases (dict): Mapping of keywords to their synonyms/abbreviations
                 Example: {"retrieval augmented generation": ["rag", "retrieval augmented"], ...}
             
    Raises:
        ValueError: If API key is missing or invalid
        Exception: If API call fails or response cannot be parsed
    """
    
    if not jd_text or not jd_text.strip():
        raise ValueError("Job description text is empty")
    
    if not gemini_key_1:
        raise ValueError("GEMINI_KEY_1 environment variable is not set")
    
    # Configure Gemini API with first key
    genai.configure(api_key=gemini_key_1)
    
    # Create the prompt for keyword extraction with aliases
    prompt = f"""You are an expert HR analyst. Extract all technical skills, tools, technologies, frameworks, domain knowledge and important keywords from this job description.

Also for each keyword, list common synonyms or abbreviations that mean the same thing so we can match them against resumes that may use different terms.

Return ONLY a valid JSON object like this:
{{
  "keywords": ["python", "large language models", "docker"],
  "aliases": {{
    "large language models": ["llms", "llm", "language models"],
    "retrieval augmented generation": ["rag", "retrieval augmented"],
    "autonomous agents": ["agentic", "ai agents", "agent systems"],
    "generative ai": ["genai", "gen ai"],
    "natural language processing": ["nlp"],
    "computer vision": ["cv"],
    "ci/cd pipelines": ["ci cd", "cicd", "continuous integration"]
  }}
}}

Rules:
- Include ONLY keywords that actually appear in the JD
- Aliases should be common abbreviations or synonyms
- Not every keyword needs aliases
- No explanation. No markdown. Just JSON.

JD:
{jd_text}"""
    
    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        
        # Make API call
        response = model.generate_content(prompt)
        
        # Get the response text
        response_text = response.text
        
        # Parse JSON response
        try:
            # Try to find JSON in the response (in case of extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON object found in response")
            
            json_str = response_text[json_start:json_end]
            keywords_data = json.loads(json_str)
            
            if "keywords" not in keywords_data:
                raise ValueError("Response JSON missing 'keywords' key")
            
            keywords = keywords_data["keywords"]
            
            if not isinstance(keywords, list):
                raise ValueError("'keywords' must be a list")
            
            # Convert to lowercase set for case-insensitive matching
            jd_keywords = set(keyword.lower().strip() for keyword in keywords if keyword)
            
            if not jd_keywords:
                raise ValueError("No keywords extracted from job description")
            
            # Extract and normalize aliases
            jd_aliases = {}
            if "aliases" in keywords_data and isinstance(keywords_data["aliases"], dict):
                for key, alias_list in keywords_data["aliases"].items():
                    key_lower = key.lower().strip()
                    if isinstance(alias_list, list):
                        # Normalize all aliases to lowercase
                        normalized_aliases = [alias.lower().strip() for alias in alias_list if alias]
                        if normalized_aliases:
                            jd_aliases[key_lower] = normalized_aliases
            
            return jd_keywords, jd_aliases
            
        except json.JSONDecodeError as e:
            raise Exception(
                f"Failed to parse Gemini API response as JSON: {str(e)}\n"
                f"Response was: {response_text}"
            )
    
    except Exception as e:
        raise Exception(f"Gemini API call failed: {str(e)}")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # test JD
    test_jd = """
    Key Responsibilities
• Design and implement GenAI solutions using LLMs and RAG architectures
• Develop and optimize prompt engineering strategies for:
• Text generation
• Chatbots
• Language translation
• Build AI workflows using
• LangChain, LangGraph, Agentic RAG frameworks
• Develop and deploy models on AWS cloud infrastructure
• Implement retrieval mechanisms for efficient data querying
• Perform model evaluation and optimization
• Create reusable prompt libraries and AI components
• Build automation scripts using Python for testing and evaluation
• Collaborate with data scientists and engineers to integrate AI into products
• Design scalable AI architectures and pipelines
• Ensure ethical AI usage and model governance

MustHave Skills
AI / GenAI
• Strong expertise in:
• LLMs (GPT, LLaMA, etc.)
• RAG (Retrieval-Augmented Generation)
• Prompt Engineering
• Experience with
• LangChain / LangGraph frameworks

Programming
• Strong proficiency in:
• Python
• Experience in
• Scripting, automation, and model integration

Cloud & DevOps
• Experience with:
• AWS cloud services
• CI/CD pipelines and DevOps practices

AI Development
• Experience with:
• Embeddings, tokenization
• Model fine-tuning and optimization
• Exposure to
• GPT, HuggingFace, Bedrock (or similar platforms)

GoodtoHave Skills
• Experience building:
• AI-powered applications (Streamlit, Flask, Gradio)
• Exposure to
• Multi-agent architectures
• Experience in
• Team leadership or mentoring
    """
    
    gemini_key_1 = os.getenv("GEMINI_KEY_1")
    
    keywords, aliases = extract_jd_keywords(test_jd, gemini_key_1)
    
    print(f"\nTotal keywords extracted: {len(keywords)}")
    print("\nSingle word keywords:")
    for k in sorted([k for k in keywords if " " not in k]):
        print(f"  • {k}")
    
    print("\nMulti word keywords:")
    for k in sorted([k for k in keywords if " " in k]):
        print(f"  • {k}")
    
    print(f"\nRaw set: {keywords}")
    
    print(f"\n\nAliases found: {len(aliases)}")
    for keyword, alias_list in sorted(aliases.items()):
        print(f"  {keyword}: {alias_list}")