import sqlite3
import logging
import os
from bs4 import BeautifulSoup
from typing import Optional, Dict
from utils import clean_and_tokenize

logger = logging.getLogger(__name__)

class Indexer:
    """
    Manages the creation and persistence of a SQLite-based inverted index.
    
    This implementation tracks Term Frequency (TF) and Document Frequency (DF)
    to support relevance ranking via TF-IDF.
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Initializes the indexer with a database path.
        
        Args:
            db_path: Path to the SQLite file. Defaults to ":memory:".
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Sets up the SQLite schema for the inverted index and metadata."""
        if self.db_path != ":memory:":
            db_dir = os.path.dirname(os.path.abspath(self.db_path))
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # words: stores unique terms and their global document frequency
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE,
                df INTEGER DEFAULT 0
            )
        ''')
        
        # pages: stores crawled URLs and their total word counts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                total_words INTEGER DEFAULT 0
            )
        ''')
        
        # occurrences: mapping between words and pages with local statistics
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
        
        # metadata: tracks global statistics like total document count
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value INTEGER
            )
        ''')
        cursor.execute('INSERT OR IGNORE INTO metadata (key, value) VALUES (?, ?)', ('total_documents', 0))
        
        self.conn.commit()

    def add_page(self, url: str, html_content: str) -> None:
        """
        Processes a page, extracts tokens, and updates the inverted index.
        
        Args:
            url: The URL of the page.
            html_content: The raw HTML content of the page.
        """
        if self.conn is None:
            logger.error("Database connection is not initialized.")
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove non-content elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ')
        tokens = clean_and_tokenize(text)
        
        if not tokens:
            logger.warning(f"No valid tokens found for {url}")
            return

        # Aggregate term frequency and positions for this document
        page_stats: Dict[str, Dict] = {}
        for pos, token in enumerate(tokens):
            if token not in page_stats:
                page_stats[token] = {'tf': 0, 'pos': []}
            page_stats[token]['tf'] += 1
            page_stats[token]['pos'].append(pos)
            
        cursor = self.conn.cursor()
        
        # Insert page and update global document count
        cursor.execute('INSERT OR IGNORE INTO pages (url, total_words) VALUES (?, ?)', (url, len(tokens)))
        cursor.execute('SELECT id FROM pages WHERE url = ?', (url,))
        page_id = cursor.fetchone()['id']
        
        cursor.execute('UPDATE metadata SET value = value + 1 WHERE key = ?', ('total_documents',))
        
        # Index each term
        for word, stats in page_stats.items():
            # Insert word and increment Document Frequency (df)
            cursor.execute('INSERT OR IGNORE INTO words (word, df) VALUES (?, ?)', (word, 0))
            cursor.execute('UPDATE words SET df = df + 1 WHERE word = ?', (word,))
            
            cursor.execute('SELECT id FROM words WHERE word = ?', (word,))
            word_id = cursor.fetchone()['id']
            
            # Store occurrence details
            pos_str = ','.join(map(str, stats['pos']))
            cursor.execute('''
                INSERT OR REPLACE INTO occurrences (word_id, page_id, frequency, positions)
                VALUES (?, ?, ?, ?)
            ''', (word_id, page_id, stats['tf'], pos_str))
            
        self.conn.commit()
        logger.debug(f"Successfully indexed {url}")

    def load_index(self, filepath: str) -> bool:
        """
        Loads an existing index from the file system.
        
        Args:
            filepath: Path to the SQLite file.
            
        Returns:
            True if successful, False otherwise.
        """
        if not os.path.exists(filepath):
            return False
            
        if self.conn:
            self.conn.close()
            
        self.db_path = filepath
        self._initialize_db()
        return True

    def close(self) -> None:
        """Closes the active database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")
