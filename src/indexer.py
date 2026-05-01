import sqlite3
import re
from bs4 import BeautifulSoup
import os

class Indexer:
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Create tables if they don't exist."""
        # Ensure directory exists if not in memory
        if self.db_path != ":memory:":
            db_dir = os.path.dirname(os.path.abspath(self.db_path))
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS occurrences (
                word_id INTEGER,
                page_id INTEGER,
                frequency INTEGER,
                positions TEXT,
                PRIMARY KEY (word_id, page_id),
                FOREIGN KEY (word_id) REFERENCES words(id),
                FOREIGN KEY (page_id) REFERENCES pages(id)
            )
        ''')
        self.conn.commit()

    def clean_text(self, text):
        """Remove non-alphanumeric characters and convert to lowercase."""
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        return text.lower()

    def tokenize(self, text):
        """Tokenize text into words."""
        return text.split()

    def add_page(self, url, html_content):
        """Extract text from HTML and add to the inverted index."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text, preserving some structure by replacing tags with spaces
        text = soup.get_text(separator=' ')
        clean_text = self.clean_text(text)
        words = self.tokenize(clean_text)
        
        # Aggregate word statistics for this page to minimize database hits
        page_index = {}
        for position, word in enumerate(words):
            if word not in page_index:
                page_index[word] = {'frequency': 0, 'positions': []}
            page_index[word]['frequency'] += 1
            page_index[word]['positions'].append(position)
            
        cursor = self.conn.cursor()
        
        # Get or create page_id
        cursor.execute('INSERT OR IGNORE INTO pages (url) VALUES (?)', (url,))
        cursor.execute('SELECT id FROM pages WHERE url = ?', (url,))
        page_id = cursor.fetchone()['id']
        
        for word, stats in page_index.items():
            # Get or create word_id
            cursor.execute('INSERT OR IGNORE INTO words (word) VALUES (?)', (word,))
            cursor.execute('SELECT id FROM words WHERE word = ?', (word,))
            word_id = cursor.fetchone()['id']
            
            # Insert or replace occurrence
            positions_str = ','.join(map(str, stats['positions']))
            cursor.execute('''
                INSERT OR REPLACE INTO occurrences (word_id, page_id, frequency, positions)
                VALUES (?, ?, ?, ?)
            ''', (word_id, page_id, stats['frequency'], positions_str))
            
        self.conn.commit()

    def save_index(self, filepath):
        """Save the inverted index (already handled by SQLite commit, but kept for compatibility)."""
        # If the filepath is different from current db_path, we might need to copy it,
        # but in this implementation, db_path is established at init/load.
        pass

    def load_index(self, filepath):
        """Load the inverted index from a SQLite file."""
        if not os.path.exists(filepath):
            return False
            
        if self.conn:
            self.conn.close()
            
        self.db_path = filepath
        self._initialize_db()
        return True

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
