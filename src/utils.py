import re

COLUMN_MAPPING = {
    "goals": "Gls", "goal": "Gls", "scorer": "Gls",
    "assists": "Ast", "assist": "Ast",
    "minutes": "MP", "minute": "MP", "mp": "MP",
    "age": "Age",
    "position": "Pos", "pos": "Pos",
    "team": "Squad", "club": "Squad", "squad": "Squad",
    "nation": "Nation", "country": "Nation",
    "value": "Value"
}

POSITION_SYNONYMS = {
    "goalkeeper": "GK", "keeper": "GK", "gk": "GK",
    "defender": "DF", "df": "DF",
    "midfielder": "MF", "mf": "MF",
    "forward": "FW", "fw": "FW", "striker": "FW", "st": "FW", "attacker": "FW"
}

def normalize_text(s):
    """Normalize text"""
    if s is None:
        return ""
    s = s.strip().lower()
    s = re.sub(r'\s+', ' ', s)
    return s

def extract_integers(s):
    """Extract integers from text"""
    return [int(n) for n in re.findall(r'\d+', s)]

def parse_comparison(s):
    """Parse comparison operators"""
    s = s.lower()
    if "more than" in s or "over" in s or ">" in s:
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
    nums = extract_integers(s)
    if nums:
        return "==", nums[0]
    return None, None
