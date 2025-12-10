# src/utils.py
import re

# Mapping common English words to CSV column names
COLUMN_MAPPING = {
    "goals": "Gls",
    "goal": "Gls",
    "scorer": "Gls",
    "assists": "Ast",
    "assist": "Ast",
    "minutes": "MP",
    "minute": "MP",
    "mp": "MP",
    "age": "Age",
    "position": "Pos",
    "pos": "Pos",
    "team": "Squad",
    "club": "Squad",
    "squad": "Squad",
    "nation": "Nation",
    "country": "Nation",
    "value": "Value"  # if you have a Value column or similar
}

# Some common synonyms mapping for positions
POSITION_SYNONYMS = {
    "goalkeeper": "GK",
    "keeper": "GK",
    "gk": "GK",
    "defender": "DF",
    "df": "DF",
    "midfielder": "MF",
    "mf": "MF",
    "forward": "FW",
    "fw": "FW",
    "striker": "FW",
    "st": "FW",
    "attacker": "FW"
}

# Normalize function for incoming text
def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = s.strip().lower()
    # collapse multiple spaces
    s = re.sub(r'\s+', ' ', s)
    return s

# Extract all integers from text (e.g., "more than 10 goals" -> [10])
def extract_integers(s: str):
    return [int(n) for n in re.findall(r'\d+', s)]

# Detect comparison keywords and return operator and value if present
def parse_comparison(s: str):
    s = s.lower()
    # patterns: "> 10", ">=10", "more than 10", "less than 5", "under 25", "over 1000"
    if "more than" in s or "over" in s or "greater than" in s or ">" in s:
        nums = extract_integers(s)
        if nums:
            return ">", nums[0]
    if "less than" in s or "under" in s or "<" in s:
        nums = extract_integers(s)
        if nums:
            return "<", nums[0]
    if "at least" in s or ">=" in s:
        nums = extract_integers(s)
        if nums:
            return ">=", nums[0]
    if "at most" in s or "<=" in s:
        nums = extract_integers(s)
        if nums:
            return "<=", nums[0]
    # direct equality like "age 22" or "5 goals"
    nums = extract_integers(s)
    if nums:
        return "==", nums[0]
    return None, None
