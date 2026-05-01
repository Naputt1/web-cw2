import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from indexer import Indexer

@pytest.fixture
def indexer():
    # Use in-memory database for tests to keep them fast and isolated
    return Indexer(":memory:")

def test_clean_text(indexer):
    assert indexer.clean_text("Hello, World!") == "hello  world "
    assert indexer.clean_text("Python 3.10") == "python 3 10"

def test_tokenize(indexer):
    assert indexer.tokenize("hello world test") == ["hello", "world", "test"]

def test_add_page(indexer):
    html = "<html><body><p>Hello world. Hello search.</p></body></html>"
    url = "http://example.com"
    indexer.add_page(url, html)
    
    cursor = indexer.conn.cursor()
    
    # Verify word was inserted
    cursor.execute('SELECT id FROM words WHERE word = ?', ('hello',))
    word_row = cursor.fetchone()
    assert word_row is not None
    word_id = word_row['id']
    
    # Verify page was inserted
    cursor.execute('SELECT id FROM pages WHERE url = ?', (url,))
    page_row = cursor.fetchone()
    assert page_row is not None
    page_id = page_row['id']
    
    # Verify occurrence statistics
    cursor.execute('SELECT frequency, positions FROM occurrences WHERE word_id = ? AND page_id = ?', (word_id, page_id))
    occ = cursor.fetchone()
    assert occ['frequency'] == 2
    assert occ['positions'] == "0,2"
    
    # Check another word
    cursor.execute('SELECT frequency FROM occurrences o JOIN words w ON o.word_id = w.id WHERE w.word = ?', ('search',))
    assert cursor.fetchone()['frequency'] == 1

def test_case_insensitivity(indexer):
    indexer = Indexer(":memory:")
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
