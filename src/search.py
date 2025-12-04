# src/search.py
import difflib
import re
import pandas as pd

from .utils import (
    normalize_text,
    COLUMN_MAPPING,
    POSITION_SYNONYMS,
    extract_integers,
    parse_comparison
)

def _fuzzy_choice(query, choices, cutoff=0.6):
    """
    Return best fuzzy match from choices using difflib SequenceMatcher ratio.
    Returns (best_match, score) where score is 0..1
    """
    if not choices:
        return None, 0.0
    query = normalize_text(query)
    best = None
    best_score = 0.0
    for choice in choices:
        if choice is None:
            continue
        score = difflib.SequenceMatcher(None, query, normalize_text(str(choice))).ratio()
        if score > best_score:
            best = choice
            best_score = score
    return best, best_score

def _match_player_by_name(df: pd.DataFrame, query: str, threshold=0.75):
    """
    Try to match by player name (exact or fuzzy).
    Returns a single Series (row) or None.
    """
    if 'Player' not in df.columns:
        return None

    query_n = normalize_text(query)
    # exact case-insensitive match
    mask = df['Player'].astype(str).str.lower() == query_n
    if mask.any():
        return df[mask].iloc[0]

    # fuzzy match among player names
    names = df['Player'].astype(str).tolist()
    best, score = _fuzzy_choice(query_n, names)
    if best and score >= threshold:
        return df[df['Player'].astype(str).str.lower() == normalize_text(best)].iloc[0]
    return None

def _column_contains(df: pd.DataFrame, col: str, word: str):
    """Case-insensitive contains search on a column"""
    if col not in df.columns:
        return pd.DataFrame()
    return df[df[col].astype(str).str.lower().str.contains(word.lower(), na=False)]

def smart_search(query: str, df: pd.DataFrame):
    """
    Smart search that accepts any English input and returns a single player row (pandas Series),
    or None if nothing matched.
    Rules implemented (in priority order):
      1. Try fuzzy player name match.
      2. Handle ranked requests: 'top scorer', 'most assists', 'highest value'.
      3. Keyword -> column mapping (e.g., 'goals', 'assists', 'age', 'team').
         It supports numeric comparisons like 'more than 10 goals', 'age < 25'.
      4. Position synonyms: 'goalkeeper', 'defender', 'midfielder', 'forward'.
      5. Fuzzy match squad/team, nation, position when query looks like a name.
    """
    if query is None:
        return None
    q = normalize_text(query)

    # 1) direct player name fuzzy match
    row = _match_player_by_name(df, q, threshold=0.7)
    if row is not None:
        return row

    # 2) ranked requests and superlatives
    if "top scorer" in q or "top scorers" in q or "most goals" in q or "highest goals" in q:
        if "Gls" in df.columns:
            sorted_df = df.copy()
            sorted_df['__g'] = pd.to_numeric(sorted_df.get('Gls', 0), errors='coerce').fillna(0)
            sorted_df = sorted_df.sort_values('__g', ascending=False)
            return sorted_df.iloc[0]
    if "most assists" in q or "top assist" in q:
        if "Ast" in df.columns:
            sorted_df = df.copy()
            sorted_df['__a'] = pd.to_numeric(sorted_df.get('Ast', 0), errors='coerce').fillna(0)
            sorted_df = sorted_df.sort_values('__a', ascending=False)
            return sorted_df.iloc[0]
    if "highest value" in q or "most valuable" in q or "highest market value" in q:
        if "Value" in df.columns:
            sorted_df = df.copy()
            sorted_df['__v'] = pd.to_numeric(sorted_df.get('Value', 0), errors='coerce').fillna(0)
            sorted_df = sorted_df.sort_values('__v', ascending=False)
            return sorted_df.iloc[0]
        elif "Gls" in df.columns or "Ast" in df.columns:
            sorted_df = df.copy()
            g = pd.to_numeric(sorted_df.get('Gls', 0), errors='coerce').fillna(0)
            a = pd.to_numeric(sorted_df.get('Ast', 0), errors='coerce').fillna(0)
            sorted_df['__score'] = g + 0.8 * a
            sorted_df = sorted_df.sort_values('__score', ascending=False)
            return sorted_df.iloc[0]

    # 3) column keyword + numeric comparison parsing
    for word, col in COLUMN_MAPPING.items():
        if word in q:
            op, val = parse_comparison(q)
            if op is None:
                nums = extract_integers(q)
                if nums:
                    op = "=="
                    val = nums[0]
            if val is not None and col in df.columns:
                try:
                    series = pd.to_numeric(df[col], errors='coerce')
                    if op == ">":
                        filtered = df[series > val]
                    elif op == "<":
                        filtered = df[series < val]
                    elif op == ">=":
                        filtered = df[series >= val]
                    elif op == "<=":
                        filtered = df[series <= val]
                    elif op == "==":
                        filtered = df[series == val]
                    else:
                        filtered = _column_contains(df, col, q)
                except Exception:
                    filtered = _column_contains(df, col, q)

                if not filtered.empty:
                    return filtered.iloc[0]

            # non-numeric search
            if col in df.columns:
                filtered = _column_contains(df, col, word)
                if not filtered.empty:
                    return filtered.iloc[0]

    # 4) position synonyms
    for pos_word, pos_code in POSITION_SYNONYMS.items():
        if pos_word in q and 'Pos' in df.columns:
            filtered = df[df['Pos'].astype(str).str.upper() == pos_code]
            if not filtered.empty:
                return filtered.iloc[0]

    # 5) fuzzy search on other text columns (Squad, Nation, Pos)
    for col in ['Squad', 'Nation', 'Pos']:
        if col in df.columns:
            values = df[col].astype(str).tolist()
            best, score = _fuzzy_choice(q, values)
            if best and score >= 0.7:
                return df[df[col].astype(str).str.lower() == normalize_text(best)].iloc[0]

    # 6) final fallback: any column contains
    for col in df.columns:
        try:
            filtered = df[df[col].astype(str).str.lower().str.contains(q, na=False)]
            if not filtered.empty:
                return filtered.iloc[0]
        except Exception:
            continue

    return None
