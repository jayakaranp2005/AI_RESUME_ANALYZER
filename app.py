"""
Resume Analyzer - AI-Powered Resume Screening Tool
A Streamlit web application that analyzes and ranks resumes against a job description
using AI-powered keyword extraction and intelligent scoring.
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Import all modules
from parser.pdf_parser import extract_text_from_pdfs
from parser.jd_parser import extract_jd_keywords
from matcher.keywords import extract_resume_keywords
from matcher.scorer import score_resume, rank_results, get_top_moderate_candidates, get_skill_gap_frequency
from gemini.suggestions import generate_ai_suggestions
from utils.exporter import export_results_to_csv
from config import STRONG_THRESHOLD, MODERATE_THRESHOLD, TOP_N_MODERATE, LABEL_COLORS

# ── Page config (must be first st call) ──
st.set_page_config(
    page_title="Resume Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Load custom CSS (after st is imported) ──
with open("styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# LOAD ENVIRONMENT VARIABLES
# ════════════════════════════════════════════════════════════════════════════════

load_dotenv()
GEMINI_KEY_1 = os.getenv("GEMINI_KEY_1")
GEMINI_KEY_2 = os.getenv("GEMINI_KEY_2")

if not GEMINI_KEY_1 or not GEMINI_KEY_2:
    st.error("Missing environment variables: GEMINI_KEY_1 and/or GEMINI_KEY_2")
    st.info("Please create a `.env` file with your Gemini API keys.")
    st.stop()


# ════════════════════════════════════════════════════════════════════════════════
# UI LAYOUT - SECTION 1: HEADER
# ════════════════════════════════════════════════════════════════════════════════

st.title("AI-Powered Resume Analyzer")
st.markdown(
    """
    **Intelligent resume screening tool for recruiters**
    
    - Accepts multiple resume PDFs (20+)
    - Extracts keywords intelligently using AI
    - Scores and ranks all resumes
    - Provides AI suggestions for borderline candidates
    """
)



st.divider()
st.subheader(" Kindly upload the resumes and paste the job description to get started! ")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("**Resume PDFs**")
    uploaded_files = st.file_uploader(
        "Select multiple resume PDFs",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**Job Description**")
    jd_text = st.text_area(
        "Paste the job description",
        height=150,
        placeholder="Paste your job description here...",
        label_visibility="collapsed"
    )

# Analyze button
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    analyze_button = st.button(" Analyze Resumes", type="primary", use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════════
# MAIN ANALYSIS LOGIC
# ════════════════════════════════════════════════════════════════════════════════

if analyze_button:
    # Validation
    if not uploaded_files:
        st.error(" Please upload at least one resume PDF")
        st.stop()
    
    if not jd_text or not jd_text.strip():
        st.error(" Please provide a job description")
        st.stop()
    
    # ════════════════════════════════════════════════════════════════════════════
    # PHASE 1 & 2: PDF EXTRACTION
    # ════════════════════════════════════════════════════════════════════════════
    
    with st.spinner("Extracting text from resumes..."):
        try:
            resume_texts = extract_text_from_pdfs(uploaded_files)
            st.success(f"Extracted text from {len(resume_texts)} resume(s)")
        except Exception as e:
            st.error(f"PDF extraction failed: {str(e)}")
            st.stop()
    
    # ════════════════════════════════════════════════════════════════════════════
    # PHASE 3: JD KEYWORD EXTRACTION
    # ════════════════════════════════════════════════════════════════════════════
    
    with st.spinner(" Extracting keywords from job description..."):
        try:
            jd_keywords, jd_aliases = extract_jd_keywords(jd_text, GEMINI_KEY_1)
            st.success(f"Extracted {len(jd_keywords)} keywords from JD")
        except Exception as e:
            st.error(f"JD keyword extraction failed: {str(e)}")
            st.stop()
    
    # ════════════════════════════════════════════════════════════════════════════
    # PHASE 4: RESUME KEYWORD EXTRACTION & PHASE 5: SCORING
    # ════════════════════════════════════════════════════════════════════════════
    
    with st.spinner("Analyzing resumes and calculating scores..."):
        try:
            result_dicts = []
            
            for filename, resume_text in resume_texts.items():
                # Extract keywords from resume
                resume_keywords = extract_resume_keywords(resume_text, jd_keywords, jd_aliases)
                
                # Score the resume
                result = score_resume(resume_keywords, jd_keywords, filename)
                result_dicts.append(result)
            
            # Rank all results
            ranked_results = rank_results(result_dicts)
            
            st.success(f"Scored and ranked {len(ranked_results)} resume(s)")
        except Exception as e:
            st.error(f" Analysis failed: {str(e)}")
            st.stop()
    
    # ════════════════════════════════════════════════════════════════════════════
    # PHASE 6: AI SUGGESTIONS FOR MODERATE CANDIDATES
    # ════════════════════════════════════════════════════════════════════════════
    
    suggestions_dict = {}
    top_moderate = get_top_moderate_candidates(ranked_results, TOP_N_MODERATE)
    
    if top_moderate:
        with st.spinner(f" Generating AI suggestions for top {len(top_moderate)} moderate candidate(s)..."):
            try:
                suggestions_dict = generate_ai_suggestions(top_moderate, jd_keywords, GEMINI_KEY_2)
                st.success(f"Generated suggestions for {len(suggestions_dict)} candidate(s)")
            except Exception as e:
                st.warning(f"Could not generate AI suggestions: {str(e)}")
    
    # ════════════════════════════════════════════════════════════════════════════════
    # UI LAYOUT - SECTION 3: RESULTS TABLE
    # ════════════════════════════════════════════════════════════════════════════════
    
    st.divider()
    st.subheader("Results Summary")
    
    # Create display dataframe
    display_data = []
    for result in ranked_results:
        display_data.append({
            "Rank": result['rank'],
            "Filename": result['filename'],
            "Score %": result['score'],
            "Category": result['label'],
            "Matched": len(result['matched_keywords']),
            "Missing": len(result['missing_keywords'])
        })
    
    # Display as table
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width=80),
            "Filename": st.column_config.TextColumn("Resume File"),
            "Score %": st.column_config.ProgressColumn(
                "Match Score",
                min_value=0,
                max_value=100,
                format="%.1f%%"
            ),
            "Category": st.column_config.TextColumn("Category"),
            "Matched": st.column_config.NumberColumn("Matched Skills"),
            "Missing": st.column_config.NumberColumn("Missing Skills")
        }
    )
    
    # ════════════════════════════════════════════════════════════════════════════════
    # UI LAYOUT - SECTION 4: DETAIL CARDS (EXPANDABLE)
    # ════════════════════════════════════════════════════════════════════════════════
    
    st.divider()
    st.subheader("Detailed Analysis")
    
    for result in ranked_results:
        filename = result['filename']
        score = result['score']
        label = result['label']
        rank = result['rank']
        
        # Format label with color
        color_emoji = LABEL_COLORS.get(label, "")
        expander_title = f"#{rank} • {filename} • {color_emoji} {label} ({score}%)"
        
        with st.expander(expander_title, expanded=(rank == 1)):
            col1, col2, col3 = st.columns(3)
            
            # Column 1: Score and Category
            with col1:
                st.metric("Match Score", f"{score}%")
                st.metric("Category", label)
            
            # Column 2: Keywords Count
            with col2:
                st.metric("Matched Skills", len(result['matched_keywords']))
                st.metric("Missing Skills", len(result['missing_keywords']))
            
            # Column 3: Strengths
            with col3:
                st.metric("Extra Skills", len(result['strength_keywords']))
            
            # Details section
            st.divider()
            
            # Matched Skills
            st.markdown("** Matched Skills**")
            if result['matched_keywords']:
                matched_text = ', '.join(sorted(result['matched_keywords']))
                st.caption(matched_text)
            else:
                st.caption("None")
            
            # Missing Skills
            st.markdown("** Missing Skills**")
            if result['missing_keywords']:
                missing_text = ', '.join(sorted(result['missing_keywords']))
                st.caption(missing_text)
            else:
                st.caption("None")
            
            # Strengths (Extra Skills)
            st.markdown("** Extra Skills (Beyond JD)**")
            if result['strength_keywords']:
                strengths_text = ', '.join(sorted(result['strength_keywords']))
                st.caption(strengths_text)
            else:
                st.caption("None")
            
            # AI Suggestions (only for top 5 moderate)
            st.markdown("**AI Suggestions**")
            if filename in suggestions_dict:
                suggestions = suggestions_dict[filename]
                for idx, suggestion in enumerate(suggestions, 1):
                    st.write(f"{idx}. {suggestion}")
            else:
                if label == "Strong":
                    st.caption("🟢 AI Suggestions not generated for Strong candidates")
                elif label == "Weak":
                    st.caption("🔴 AI Suggestions not generated for Weak candidates")
                else:
                    st.caption("⚠️ AI Suggestions not generated for this candidate (outside top 5)")
    
    # ════════════════════════════════════════════════════════════════════════════════
    # UI LAYOUT - SECTION 5: SKILL GAP ANALYSIS
    # ════════════════════════════════════════════════════════════════════════════════
    
    gap_data = get_skill_gap_frequency(ranked_results)
    
    if gap_data:
        st.markdown("---")
        st.subheader(" Skill Gap Analysis — What The Talent Pool Is Missing")
        st.caption("Skills most commonly absent across all candidates")
        
        top_gaps = gap_data[:10]
        
        for gap in top_gaps:
            skill = gap["skill"]
            count = gap["count"]
            pct   = gap["percentage"]
            total = len(ranked_results)
            
            if pct >= 70:
                color = "🔴"
            elif pct >= 40:
                color = "🟡"
            else:
                color = "🟢"
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.progress(int(pct) / 100, text=f"{color} {skill}")
            with col2:
                st.metric("Candidates", f"{count}/{total}")
            with col3:
                st.metric("Gap Rate", f"{pct}%")
    
    # ════════════════════════════════════════════════════════════════════════════════
    # UI LAYOUT - SECTION 6: DOWNLOAD
    # ════════════════════════════════════════════════════════════════════════════════
    
    st.divider()
    st.subheader("📥 Export Results")
    
    try:
        csv_bytes = export_results_to_csv(ranked_results)
        
        st.download_button(
            label="📊 Download Results as CSV",
            data=csv_bytes,
            file_name="resume_analysis_results.csv",
            mime="text/csv",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"❌ Failed to export CSV: {str(e)}")


# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR - INFORMATION
# ════════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("###  How It Works")
    st.markdown("""
    1. **Upload Resumes** - Select multiple PDF files
    2. **Paste JD** - Provide the job description text
    3. **Analyze** - AI extracts and matches keywords
    4. **Review** - See scores, matches, and suggestions
    5. **Export** - Download results as CSV
    """)
    
    st.divider()
    
    st.markdown("###  Scoring Criteria")
    st.markdown(f"""
    - **🟢 Strong** - Score ≥ {STRONG_THRESHOLD}%
    - **🟡 Moderate** - Score {MODERATE_THRESHOLD}-{STRONG_THRESHOLD-1}%
    - **🔴 Weak** - Score < {MODERATE_THRESHOLD}%
    """)
    
    st.divider()
    
    st.markdown("###  Features")
    st.markdown(f"""
    - Intelligent keyword extraction using AI
    - Phrase-based matching (e.g., "machine learning")
    - Automated scoring and ranking
    - AI improvement suggestions for {TOP_N_MODERATE} top moderate candidates
    - Downloadable analysis results
    """)
