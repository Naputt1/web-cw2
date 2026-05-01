import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from indexer import Indexer
from search import SearchEngine

@pytest.fixture
def searcher(tmp_path):
    # Setup a real database file in a temporary directory for tests
    db_path = str(tmp_path / "test_index.db")
    indexer = Indexer(db_path)
    
    # Populate test data
    indexer.add_page("url1", "<html><body>hello world</body></html>")
    indexer.add_page("url2", "<html><body>hello search engine</body></html>")
    indexer.add_page("url3", "<html><body>world wide web</body></html>")
    indexer.close()
    
    return SearchEngine(db_path)

def test_find_single_word(searcher):
    results = searcher.find("hello")
    assert set(results) == {"url1", "url2"}

def test_find_multi_word_and(searcher):
    results = searcher.find("hello world")
    assert set(results) == {"url1"}

def test_find_no_results(searcher):
    results = searcher.find("missing")
    assert results == []

def test_find_multi_word_no_results(searcher):
    results = searcher.find("hello missing")
    assert results == []

def test_print_word_info(searcher):
    output = searcher.print_word_info("hello")
    assert "Inverted index for 'hello':" in output
    assert "URL: url1" in output
    assert "Frequency: 1" in output
    assert "Positions: [0]" in output
