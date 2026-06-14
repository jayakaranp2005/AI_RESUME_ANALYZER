

# SCORE THRESHOLDS

STRONG_THRESHOLD = 75
MODERATE_THRESHOLD = 40
TOP_N_MODERATE = 5 # Number of moderate candidates to generate AI suggestions for


# STOPWORDS - Common English words to filter

STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "you", "your",
    "he", "she", "they", "them", "what", "which", "who",
    "this", "that", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might",
    "the", "a", "an", "and", "or", "but", "in", "on",
    "at", "to", "for", "of", "with", "by", "from", "is",
    "as", "it", "its", "so", "if", "up", "out", "about",
    "into", "than", "then", "when", "where", "how", "all",
    "any", "both", "each", "few", "more", "most", "other",
    "such", "no", "not", "only", "own", "same", "too",
    "very", "just", "also", "over", "after", "use", "used"
}


# FILLER WORDS - Resume-specific filler words to exclude

FILLER_WORDS = {
    "experience", "candidate", "ideal", "strong", "passionate",
    "responsible", "ability", "knowledge", "seeking", "role",
    "looking", "various", "including", "multiple", "duties",
    "worked", "working", "developed", "developing", "years",
    "good", "excellent", "proven", "solid", "exposure",
    "understanding", "familiar", "proficient", "skilled",
    "hands", "plus", "bonus", "preferred", "required",
    "minimum", "bachelor", "master", "degree", "equivalent",
    "team", "work", "using", "tools", "skills", "ability",
    "must", "nice", "great", "well", "need", "join"
}



# LABEL COLORS FOR UI DISPLAY

LABEL_COLORS = {
    "Strong": "🟢",
    "Moderate": "🟡",
    "Weak": "🔴"
}


# CSV EXPORT COLUMNS

CSV_COLUMNS = [
    "Rank",
    "Filename",
    "Score",
    "Label",
    "Matched Skills",
    "Missing Skills",
    "Strengths"
]
