import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from indexer import Indexer
from utils import clean_and_tokenize, stem

@pytest.fixture
def indexer():
    # Use in-memory database for tests to keep them fast and isolated
    return Indexer(":memory:")

def test_utils_processing():
    # Test stop word removal and stemming
    tokens = clean_and_tokenize("The quotes are amazing and inspirational")
    # 'The', 'are', 'and' are stop words. 'quotes' -> 'quote', 'amazing' -> 'amaz', 'inspirational' -> 'inspirat'
    assert "quote" in tokens
    assert "the" not in tokens
    assert "are" not in tokens

def test_add_page(indexer):
    html = "<html><body><p>Hello world. Hello search.</p></body></html>"
    url = "http://example.com"
    indexer.add_page(url, html)
    
    cursor = indexer.conn.cursor()
    
    # Verify word was inserted (stemmed)
    cursor.execute('SELECT id, df FROM words WHERE word = ?', ('hello',))
    word_row = cursor.fetchone()
    assert word_row is not None
    assert word_row['df'] == 1
    word_id = word_row['id']
    
    # Verify occurrence statistics
    cursor.execute('SELECT frequency, positions FROM occurrences WHERE word_id = ?', (word_id,))
    occ = cursor.fetchone()
    assert occ['frequency'] == 2
    # "hello" "world" "hello" "search" -> pos 0 and 2
    assert occ['positions'] == "0,2"

def test_case_insensitivity(indexer):
    html = "<html><body>Good good GOOD</body></html>"
    url = "http://example.com"
    indexer.add_page(url, html)
    
    cursor = indexer.conn.cursor()
    cursor.execute('SELECT frequency FROM occurrences o JOIN words w ON o.word_id = w.id WHERE w.word = ?', ('good',))
    row = cursor.fetchone()
    assert row['frequency'] == 3

def test_load_index(tmp_path):
    db_path = str(tmp_path / "test.db")
    indexer = Indexer(db_path)
    indexer.add_page("url1", "<html><body>test</body></html>")
    indexer.close()
    
    # Load into a new indexer instance
    new_indexer = Indexer(":memory:")
    assert new_indexer.load_index(db_path) is True
    
    cursor = new_indexer.conn.cursor()
    cursor.execute('SELECT url FROM pages')
    assert cursor.fetchone()['url'] == "url1"

    # Non-existent file
    assert new_indexer.load_index("nonexistent.db") is False

def test_indexer_directory_creation(tmp_path):
    # Test that indexer creates parent directory if it doesn't exist
    new_dir = tmp_path / "new_subdir"
    db_path = str(new_dir / "index.db")
    Indexer(db_path)
    assert os.path.exists(db_path)

def test_indexer_no_content(indexer):
    # Test indexing a page with no valid tokens
    indexer.add_page("http://empty.com", "<html><body></body></html>")
    cursor = indexer.conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM pages")
    assert cursor.fetchone()['count'] == 0
