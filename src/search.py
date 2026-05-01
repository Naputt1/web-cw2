import sqlite3

class SearchEngine:
    def __init__(self, db_path):
        """Initialize with path to the SQLite database."""
        self.db_path = db_path

    def _get_connection(self):
        """Create a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def find(self, query):
        """
        Find pages containing all words in the query.
        Returns a list of URLs.
        """
        words = query.lower().split()
        if not words:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Use INTERSECT to find pages that contain ALL words in the query
        # This is an efficient way to implement the AND logic for multiple search terms
        sql_parts = []
        params = []
        for word in words:
            sql_parts.append('''
                SELECT p.url 
                FROM pages p
                JOIN occurrences o ON p.id = o.page_id
                JOIN words w ON o.word_id = w.id
                WHERE w.word = ?
            ''')
            params.append(word)
            
        final_sql = " INTERSECT ".join(sql_parts)
        
        try:
            cursor.execute(final_sql, params)
            results = [row['url'] for row in cursor.fetchall()]
        except sqlite3.Error:
            results = []
        finally:
            conn.close()
            
        return results

    def print_word_info(self, word):
        """
        Return the inverted index entry for a word as a string.
        """
        word = word.lower()
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.url, o.frequency, o.positions
            FROM pages p
            JOIN occurrences o ON p.id = o.page_id
            JOIN words w ON o.word_id = w.id
            WHERE w.word = ?
        ''', (word,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return f"Word '{word}' not found in index."
        
        output = [f"Inverted index for '{word}':"]
        for row in rows:
            output.append(f"  URL: {row['url']}")
            output.append(f"    Frequency: {row['frequency']}")
            # Wrap positions in brackets to match the previous output format
            output.append(f"    Positions: [{row['positions']}]")
        
        return "\n".join(output)
