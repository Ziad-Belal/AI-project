"""
Player Search Module with DFS and BFS Tree Traversal
Implements graph-based search algorithms for finding related players
"""
import difflib
import re
import pandas as pd
from collections import deque
from typing import List, Set, Dict, Optional, Tuple

from utils import (
    normalize_text,
    COLUMN_MAPPING,
    POSITION_SYNONYMS,
    extract_integers,
    parse_comparison
)


class TreeNode:
    """
    Tree Node for representing player relationships in the search graph
    
    Attributes:
        player_name: Name of the player (node value)
        squad: Squad/team the player belongs to
        children: List of child nodes (teammates)
        visited: Whether this node has been visited during traversal
    """
    def __init__(self, player_name: str, squad: str):
        self.player_name = player_name
        self.squad = squad
        self.children: List['TreeNode'] = []
        self.visited = False
    
    def add_child(self, child: 'TreeNode'):
        """Add a child node to this tree node"""
        if child not in self.children:
            self.children.append(child)
    
    def __repr__(self):
        return f"TreeNode({self.player_name}, squad={self.squad}, children={len(self.children)})"


class PlayerSearchTree:
    """
    Tree structure for player search using DFS and BFS algorithms
    
    This class builds a graph where:
    - Nodes represent players
    - Edges connect players who are teammates (same squad)
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the search tree from player data
        
        Args:
            df: DataFrame containing player data with 'Player' and 'Squad' columns
        """
        self.df = df
        self.graph: Dict[str, List[str]] = {}
        self.node_map: Dict[str, TreeNode] = {}
        self._build_graph()
        self._build_tree()
    
    def _build_graph(self):
        """
        Build adjacency list representation of player relationships
        Players are connected if they belong to the same squad
        """
        print("Building player relationship graph...")
        
        for _, row in self.df.iterrows():
            player = str(row.get('Player', ''))
            squad = str(row.get('Squad', ''))
            
            if not player or pd.isna(player):
                continue
            
            # Initialize player in graph if not present
            if player not in self.graph:
                self.graph[player] = []
            
            # Find all teammates (players in the same squad)
            teammates = self.df[
                (self.df['Squad'] == squad) & 
                (self.df['Player'] != player)
            ]['Player'].tolist()
            
            # Add teammates to graph (avoid duplicates)
            for teammate in teammates:
                teammate_str = str(teammate)
                if teammate_str not in self.graph[player]:
                    self.graph[player].append(teammate_str)
        
        print(f"Graph built with {len(self.graph)} players")
    
    def _build_tree(self):
        """
        Build TreeNode objects from the graph structure
        Creates a tree representation for easier traversal
        """
        for player_name, neighbors in self.graph.items():
            if player_name not in self.node_map:
                # Get squad for this player
                player_row = self.df[self.df['Player'] == player_name]
                squad = str(player_row['Squad'].iloc[0]) if not player_row.empty else "Unknown"
                
                node = TreeNode(player_name, squad)
                self.node_map[player_name] = node
        
        # Connect nodes based on graph relationships
        for player_name, neighbors in self.graph.items():
            if player_name in self.node_map:
                parent_node = self.node_map[player_name]
                for neighbor in neighbors:
                    if neighbor in self.node_map:
                        parent_node.add_child(self.node_map[neighbor])
    
    def dfs_search(self, start_player: str, max_depth: int = 3) -> List[str]:
        """
        Depth-First Search (DFS) traversal of the player tree
        
        DFS explores as far as possible along each branch before backtracking.
        Uses a stack (LIFO - Last In First Out) data structure.
        
        Args:
            start_player: Name of the player to start search from
            max_depth: Maximum depth to search (default: 3)
        
        Returns:
            List of player names found during DFS traversal
        """
        if start_player not in self.node_map:
            return []
        
        # Reset visited flags
        for node in self.node_map.values():
            node.visited = False
        
        visited_players: List[str] = []
        stack: List[Tuple[TreeNode, int]] = [(self.node_map[start_player], 0)]  # (node, depth)
        
        while stack:
            current_node, depth = stack.pop()
            
            # Skip if already visited or max depth reached
            if current_node.visited or depth > max_depth:
                continue
            
            # Mark as visited and add to results
            current_node.visited = True
            if current_node.player_name != start_player:
                visited_players.append(current_node.player_name)
            
            # Add children to stack (reversed to maintain order)
            # DFS uses stack, so we reverse to process leftmost children first
            for child in reversed(current_node.children):
                if not child.visited:
                    stack.append((child, depth + 1))
        
        return visited_players
    
    def bfs_search(self, start_player: str, max_depth: int = 3) -> List[str]:
        """
        Breadth-First Search (BFS) traversal of the player tree
        
        BFS explores all nodes at the current depth before moving to next level.
        Uses a queue (FIFO - First In First Out) data structure.
        
        Args:
            start_player: Name of the player to start search from
            max_depth: Maximum depth to search (default: 3)
        
        Returns:
            List of player names found during BFS traversal
        """
        if start_player not in self.node_map:
            return []
        
        # Reset visited flags
        for node in self.node_map.values():
            node.visited = False
        
        visited_players: List[str] = []
        queue: deque = deque([(self.node_map[start_player], 0)])  # (node, depth)
        
        while queue:
            current_node, depth = queue.popleft()
            
            # Skip if already visited or max depth reached
            if current_node.visited or depth > max_depth:
                continue
            
            # Mark as visited and add to results
            current_node.visited = True
            if current_node.player_name != start_player:
                visited_players.append(current_node.player_name)
            
            # Add children to queue (FIFO order)
            # BFS uses queue, so we add children in order
            for child in current_node.children:
                if not child.visited:
                    queue.append((child, depth + 1))
        
        return visited_players
    
    def find_teammates(self, player_name: str, use_bfs: bool = True) -> List[str]:
        """
        Find teammates of a given player using tree traversal
        
        Args:
            player_name: Name of the player
            use_bfs: If True, use BFS (finds immediate teammates first)
                     If False, use DFS (explores deeper relationships)
        
        Returns:
            List of teammate names
        """
        if use_bfs:
            return self.bfs_search(player_name, max_depth=1)
        else:
            return self.dfs_search(player_name, max_depth=1)


# Legacy functions for backward compatibility
def DFS(graph: Dict[str, List[str]], start: str) -> List[str]:
    """
    Depth First Search (DFS) - Legacy function
    
    Traverses a graph using DFS algorithm.
    Uses a stack data structure (LIFO).
    
    Args:
        graph: Dictionary representing adjacency list {node: [neighbors]}
        start: Starting node for traversal
    
    Returns:
        List of visited nodes in DFS order
    """
    visited = set()
    stack = [start]
    result = []
    
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            result.append(node)
            # Reverse to maintain left-to-right order
            stack.extend(reversed(graph.get(node, [])))
    
    return result


def BFS(graph: Dict[str, List[str]], start: str) -> List[str]:
    """
    Breadth First Search (BFS) - Legacy function
    
    Traverses a graph using BFS algorithm.
    Uses a queue data structure (FIFO).
    
    Args:
        graph: Dictionary representing adjacency list {node: [neighbors]}
        start: Starting node for traversal
    
    Returns:
        List of visited nodes in BFS order
    """
    visited = set()
    queue = deque([start])
    result = []
    
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            result.append(node)
            queue.extend(graph.get(node, []))
    
    return result


def _build_player_graph(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Build a graph where players are nodes, edges if same squad
    
    This is a helper function that creates an adjacency list representation.
    For better tree structure, use PlayerSearchTree class instead.
    
    Args:
        df: DataFrame with 'Player' and 'Squad' columns
    
    Returns:
        Dictionary mapping player names to lists of teammate names
    """
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


def _graph_search_related(query: str, df: pd.DataFrame) -> Optional[pd.Series]:
    """
    Search for related players using graph traversal (DFS/BFS)
    
    This function uses the PlayerSearchTree class to find teammates
    of a given player using tree traversal algorithms.
    
    Args:
        query: Search query (e.g., "teammates of Messi")
        df: DataFrame containing player data
    
    Returns:
        pandas Series of a related player, or None if not found
    """
    q = normalize_text(query)
    
    # Check if query is asking for teammates
    if "teammates of" in q or "teammates" in q:
        # Extract player name from query
        player_part = q.replace("teammates of", "").replace("teammates", "").strip()
        row = _match_player_by_name(df, player_part, threshold=0.7)
        
        if row is not None:
            # Build search tree
            search_tree = PlayerSearchTree(df)
            start_player = row['Player']
            
            # Use BFS to find teammates (finds immediate teammates first)
            teammates = search_tree.find_teammates(start_player, use_bfs=True)
            
            if teammates:
                # Return first teammate found
                teammate_df = df[df['Player'].isin(teammates)]
                if not teammate_df.empty:
                    return teammate_df.iloc[0]
    
    return None


def _fuzzy_choice(query: str, choices: List[str], cutoff: float = 0.6) -> Tuple[Optional[str], float]:
    """
    Return best fuzzy match from choices using difflib SequenceMatcher ratio.
    
    Args:
        query: Query string to match
        choices: List of strings to match against
        cutoff: Minimum similarity score (0-1)
    
    Returns:
        Tuple of (best_match, score) where score is 0..1
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


def _match_player_by_name(df: pd.DataFrame, query: str, threshold: float = 0.75) -> Optional[pd.Series]:
    """
    Try to match by player name (exact or fuzzy).
    
    Args:
        df: DataFrame with 'Player' column
        query: Player name to search for
        threshold: Minimum similarity score for fuzzy matching
    
    Returns:
        pandas Series (row) if match found, None otherwise
    """
    if 'Player' not in df.columns:
        return None
    
    query_n = normalize_text(query)
    
    # Try exact case-insensitive match first
    mask = df['Player'].astype(str).str.lower() == query_n
    if mask.any():
        return df[mask].iloc[0]
    
    # Try fuzzy match among player names
    names = df['Player'].astype(str).tolist()
    best, score = _fuzzy_choice(query_n, names)
    if best and score >= threshold:
        return df[df['Player'].astype(str).str.lower() == normalize_text(best)].iloc[0]
    
    return None


def search_player_only(query: str, df: pd.DataFrame) -> Optional[pd.Series]:
    """
    Minimal search: only match player names (exact or fuzzy).
    Does not use graph traversal, ranked queries, or column heuristics.
    """
    if query is None:
        return None
    q = normalize_text(query)
    return _match_player_by_name(df, q, threshold=0.7)


def _column_contains(df: pd.DataFrame, col: str, word: str) -> pd.DataFrame:
    """
    Case-insensitive contains search on a column.
    
    Args:
        df: DataFrame to search
        col: Column name to search in
        word: Word to search for
    
    Returns:
        Filtered DataFrame
    """
    if col not in df.columns:
        return pd.DataFrame()
    return df[df[col].astype(str).str.lower().str.contains(word.lower(), na=False)]


def smart_search(query: str, df: pd.DataFrame) -> Optional[pd.Series]:
    """
    Smart search that accepts any English input and returns a single player row.
    
    Search strategies (in priority order):
    1. Graph-based search using DFS/BFS trees for related players (e.g., teammates)
    2. Fuzzy player name matching
    3. Ranked requests: 'top scorer', 'most assists', 'highest value'
    4. Keyword -> column mapping with numeric comparisons
    5. Position synonyms: 'goalkeeper', 'defender', 'midfielder', 'forward'
    6. Fuzzy match on squad/team, nation, position
    
    Args:
        query: Search query string
        df: DataFrame containing player data
    
    Returns:
        pandas Series (player row) if match found, None otherwise
    """
    if query is None:
        return None
    
    q = normalize_text(query)
    
    # 1) Graph-based search for related players using DFS/BFS trees
    row = _graph_search_related(query, df)
    if row is not None:
        return row
    
    # 2) Direct player name fuzzy match
    row = _match_player_by_name(df, q, threshold=0.7)
    if row is not None:
        return row
    
    # 3) Ranked requests and superlatives
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
    
    # 4) Column keyword + numeric comparison parsing
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
            
            # Non-numeric search
            if col in df.columns:
                filtered = _column_contains(df, col, word)
                if not filtered.empty:
                    return filtered.iloc[0]
    
    # 5) Position synonyms
    for pos_word, pos_code in POSITION_SYNONYMS.items():
        if pos_word in q and 'Pos' in df.columns:
            filtered = df[df['Pos'].astype(str).str.upper() == pos_code]
            if not filtered.empty:
                return filtered.iloc[0]
    
    # 6) Fuzzy search on other text columns (Squad, Nation, Pos)
    for col in ['Squad', 'Nation', 'Pos']:
        if col in df.columns:
            values = df[col].astype(str).tolist()
            best, score = _fuzzy_choice(q, values)
            if best and score >= 0.7:
                return df[df[col].astype(str).str.lower() == normalize_text(best)].iloc[0]
    
    # 7) Final fallback: any column contains
    for col in df.columns:
        try:
            filtered = df[df[col].astype(str).str.lower().str.contains(q, na=False)]
            if not filtered.empty:
                return filtered.iloc[0]
        except Exception:
            continue
    
    return None
