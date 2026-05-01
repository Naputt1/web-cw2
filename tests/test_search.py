import pytest
from unittest.mock import patch
import os
import sys
import sqlite3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from indexer import Indexer
from search import SearchEngine

@pytest.fixture
def searcher(tmp_path):
    # Setup a real database file in a temporary directory for tests
    db_path = str(tmp_path / "test_index.db")
    indexer = Indexer(db_path)
    
    # Populate test data with varying frequencies for ranking tests
    # Page 1 has "hello" twice
    indexer.add_page("url1", "<html><body>hello hello world</body></html>")
    # Page 2 has "hello" once
    indexer.add_page("url2", "<html><body>hello search engine</body></html>")
    # Page 3 has "world" once
    indexer.add_page("url3", "<html><body>world wide web</body></html>")
    indexer.close()
    
    return SearchEngine(db_path)

def test_find_ranking(searcher):
    # url1 has "hello" twice, url2 has it once. url1 should rank higher.
    results = searcher.find("hello")
    assert results[0][0] == "url1"
    assert results[1][0] == "url2"
    assert results[0][1] > results[1][1]

def test_find_plus_syntax(searcher):
    # Must have "hello" AND "world"
    results = searcher.find("+hello +world")
    assert len(results) == 1
    assert results[0][0] == "url1"

def test_find_minus_syntax(searcher):
    # Has "hello" but NOT "world"
    results = searcher.find("hello -world")
    assert len(results) == 1
    assert results[0][0] == "url2"

def test_find_contradictory_query(searcher):
    # Same word marked as MUST and MUST NOT should return nothing
    results = searcher.find("+hello -hello")
    assert results == []

def test_find_stop_words_only(searcher):
    # Query with only stop words should not return results (they aren't indexed)
    results = searcher.find("the and is")
    assert results == []

def test_find_mixed_syntax(searcher):
    # MUST have hello, SHOULD have engine, MUST NOT have world
    results = searcher.find("+hello engine -world")
    assert len(results) == 1
    assert results[0][0] == "url2"

def test_find_case_insensitivity(searcher):
    # Query case should not matter
    results = searcher.find("HELLO")
    assert len(results) == 2

def test_find_empty_query(searcher):
    assert searcher.find("") == []
    assert searcher.find("   ") == []

def test_find_db_error(searcher):
    # Mocking a database error during search
    with patch('sqlite3.connect') as mock_connect:
        mock_connect.side_effect = sqlite3.Error("Mock DB Error")
        results = searcher.find("hello")
        assert results == []

def test_find_no_results(searcher):
    results = searcher.find("missing")
    assert results == []

def test_print_word_info(searcher):
    output = searcher.print_word_info("hello")
    assert "Inverted index for term 'hello'" in output
    assert "URL: url1" in output
    assert "Term Frequency: 2" in output
