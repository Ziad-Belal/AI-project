import difflib
import pandas as pd
from collections import deque
from utils import normalize_text, COLUMN_MAPPING, POSITION_SYNONYMS, extract_integers, parse_comparison

def DFS(graph, start):
    """Depth First Search"""
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            print(node, end=' ')
            stack.extend(reversed(graph[node]))

def BFS(graph, start):
    """Breadth First Search"""
    visited = set()
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            print(node, end=' ')
            queue.extend(graph[node])

def _build_player_graph(df):
    """Build graph where players are connected if same squad"""
    graph = {}
    for _, row in df.iterrows():
        player = row['Player']
        squad = row['Squad']
        if player not in graph:
            graph[player] = []
        teammates = df[df['Squad'] == squad]['Player'].tolist()
        for tm in teammates:
            if tm != player and tm not in graph[player]:
                graph[player].append(tm)
    return graph

def _graph_search_related(query, df):
    """Search for related players using graph"""
    q = normalize_text(query)
    if "teammates of" in q or "teammates" in q:
        player_part = q.replace("teammates of", "").replace("teammates", "").strip()
        row = _match_player_by_name(df, player_part, threshold=0.7)
        if row is not None:
            graph = _build_player_graph(df)
            start = row['Player']
            visited = set()
            queue = deque([start])
            teammates = []
            while queue:
                node = queue.popleft()
                if node not in visited:
                    visited.add(node)
                    if node != start:
                        teammates.append(node)
                    queue.extend(graph.get(node, []))
            if teammates:
                return df[df['Player'].isin(teammates)].iloc[0]
    return None

def _fuzzy_choice(query, choices, cutoff=0.6):
    """Find best fuzzy match"""
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

def _match_player_by_name(df, query, threshold=0.75):
    """Match player by name"""
    if 'Player' not in df.columns:
        return None
    
    query_n = normalize_text(query)
    mask = df['Player'].astype(str).str.lower() == query_n
    if mask.any():
        return df[mask].iloc[0]
    
    names = df['Player'].astype(str).tolist()
    best, score = _fuzzy_choice(query_n, names)
    if best and score >= threshold:
        return df[df['Player'].astype(str).str.lower() == normalize_text(best)].iloc[0]
    return None

def _column_contains(df, col, word):
    """Search column for word"""
    if col not in df.columns:
        return pd.DataFrame()
    return df[df[col].astype(str).str.lower().str.contains(word.lower(), na=False)]

def smart_search(query, df):
    """Smart search for players"""
    if query is None:
        return None
    
    q = normalize_text(query)
    
    # 1) Graph search
    row = _graph_search_related(query, df)
    if row is not None:
        return row
    
    # 2) Name match
    row = _match_player_by_name(df, q, threshold=0.7)
    if row is not None:
        return row
    
    # 3) Ranked requests
    if "top scorer" in q or "most goals" in q:
        if "Gls" in df.columns:
            sorted_df = df.copy()
            sorted_df['__g'] = pd.to_numeric(sorted_df.get('Gls', 0), errors='coerce').fillna(0)
            sorted_df = sorted_df.sort_values('__g', ascending=False)
            return sorted_df.iloc[0]
    
    if "most assists" in q:
        if "Ast" in df.columns:
            sorted_df = df.copy()
            sorted_df['__a'] = pd.to_numeric(sorted_df.get('Ast', 0), errors='coerce').fillna(0)
            sorted_df = sorted_df.sort_values('__a', ascending=False)
            return sorted_df.iloc[0]
    
    # 4) Column keyword search
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
                except:
                    filtered = _column_contains(df, col, q)
                
                if not filtered.empty:
                    return filtered.iloc[0]
            
            if col in df.columns:
                filtered = _column_contains(df, col, word)
                if not filtered.empty:
                    return filtered.iloc[0]
    
    # 5) Position search
    for pos_word, pos_code in POSITION_SYNONYMS.items():
        if pos_word in q and 'Pos' in df.columns:
            filtered = df[df['Pos'].astype(str).str.upper() == pos_code]
            if not filtered.empty:
                return filtered.iloc[0]
    
    # 6) Fuzzy search on columns
    for col in ['Squad', 'Nation', 'Pos']:
        if col in df.columns:
            values = df[col].astype(str).tolist()
            best, score = _fuzzy_choice(q, values)
            if best and score >= 0.7:
                return df[df[col].astype(str).str.lower() == normalize_text(best)].iloc[0]
    
    # 7) Final fallback
    for col in df.columns:
        try:
            filtered = df[df[col].astype(str).str.lower().str.contains(q, na=False)]
            if not filtered.empty:
                return filtered.iloc[0]
        except:
            continue
    
    return None
