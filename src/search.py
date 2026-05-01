import sqlite3
import math
import logging
from typing import List, Tuple, Dict
from utils import stem

logger = logging.getLogger(__name__)

class SearchEngine:
    """
    An advanced search engine that implements ranked retrieval using TF-IDF.
    
    This implementation supports complex boolean queries including:
    - '+term': Must be present in the document.
    - '-term': Must NOT be present in the document.
    - 'term': Used for relevance ranking.
    """
    
    def __init__(self, db_path: str):
        """
        Initializes the search engine with a database path.
        
        Args:
            db_path: Path to the SQLite index file.
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Establishes a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def find(self, query: str) -> List[Tuple[str, float]]:
        """
        Finds pages matching the query, ranked by TF-IDF relevance.
        
        Args:
            query: The search query string.
            
        Returns:
            A list of (url, score) tuples, sorted by relevance score descending.
        """
        raw_terms = query.lower().split()
        if not raw_terms:
            return []

        must_include = []
        must_exclude = []
        should_include = []

        # Parse advanced query syntax
        for term in raw_terms:
            if term.startswith('+'):
                must_include.append(stem(term[1:]))
            elif term.startswith('-'):
                must_exclude.append(stem(term[1:]))
            else:
                should_include.append(stem(term))
                
        # All terms that contribute to the score
        ranking_terms = must_include + should_include
        if not ranking_terms:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Retrieve global document count
            cursor.execute('SELECT value FROM metadata WHERE key = "total_documents"')
            n_docs_row = cursor.fetchone()
            n_docs = n_docs_row['value'] if n_docs_row else 1
            
            # 2. Identify candidate pages based on boolean constraints
            candidate_sql, params = self._build_candidate_query(must_include, must_exclude, should_include)
            
            # 3. Fetch frequencies and document frequencies for ranking
            placeholders = ','.join(['?'] * len(ranking_terms))
            cursor.execute(f'''
                SELECT o.page_id, p.url, w.word, o.frequency, w.df
                FROM occurrences o
                JOIN words w ON o.word_id = w.id
                JOIN pages p ON o.page_id = p.id
                WHERE o.page_id IN ({candidate_sql})
                AND w.word IN ({placeholders})
            ''', (*params, *ranking_terms))
            
            rows = cursor.fetchall()
            
            # 4. Calculate TF-IDF scores
            page_scores: Dict[str, float] = {}
            for row in rows:
                url = row['url']
                tf = row['frequency']
                df = row['df']
                
                # IDF = log(Total Documents / Documents with Term)
                idf = math.log(n_docs / df) if df > 0 else 0
                score = tf * idf
                
                page_scores[url] = page_scores.get(url, 0.0) + score
                
            # Sort results by score in descending order
            return sorted(page_scores.items(), key=lambda x: x[1], reverse=True)
            
        except sqlite3.Error as e:
            logger.error(f"Database error during search: {e}")
            return []
        finally:
            conn.close()

    def _build_candidate_query(self, must: List[str], exclude: List[str], should: List[str]) -> Tuple[str, List]:
        """Constructs the SQL to filter documents based on boolean constraints."""
        params = []
        
        # Start with MUST include terms (INTERSECT ensures all are present)
        if must:
            parts = []
            for term in must:
                parts.append('SELECT page_id FROM occurrences o JOIN words w ON o.word_id = w.id WHERE w.word = ?')
                params.append(term)
            candidate_sql = " INTERSECT ".join(parts)
        else:
            # If no strict requirements, any page containing any "should" term is a candidate
            placeholders = ','.join(['?'] * len(should))
            candidate_sql = f'SELECT DISTINCT page_id FROM occurrences o JOIN words w ON o.word_id = w.id WHERE w.word IN ({placeholders})'
            params.extend(should)
            
        # Apply MUST NOT exclude terms
        if exclude:
            placeholders = ','.join(['?'] * len(exclude))
            candidate_sql = f'''
                SELECT page_id FROM ({candidate_sql})
                WHERE page_id NOT IN (
                    SELECT page_id FROM occurrences o 
                    JOIN words w ON o.word_id = w.id 
                    WHERE w.word IN ({placeholders})
                )
            '''
            params.extend(exclude)
            
        return candidate_sql, params

    def print_word_info(self, word: str) -> str:
        """
        Retrieves and formats detailed index information for a specific term.
        
        Args:
            word: The term to inspect.
            
        Returns:
            A formatted string containing statistics and positions.
        """
        stemmed_word = stem(word)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.url, o.frequency, o.positions, w.df
            FROM pages p
            JOIN occurrences o ON p.id = o.page_id
            JOIN words w ON o.word_id = w.id
            WHERE w.word = ?
        ''', (stemmed_word,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return f"Term '{word}' (stemmed: '{stemmed_word}') not found in index."
        
        df = rows[0]['df']
        output = [f"Inverted index for term '{word}' (Stemmed: '{stemmed_word}', Document Frequency: {df}):"]
        for row in rows:
            output.append(f"  URL: {row['url']}")
            output.append(f"    Term Frequency: {row['frequency']}")
            output.append(f"    Positions: [{row['positions']}]")
        
        return "\n".join(output)
