import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from search import SearchEngine

@pytest.fixture
def sample_index():
    return {
        "hello": {
            "url1": {"frequency": 1, "positions": [0]},
            "url2": {"frequency": 2, "positions": [0, 5]}
        },
        "world": {
            "url1": {"frequency": 1, "positions": [1]},
            "url3": {"frequency": 1, "positions": [0]}
        },
        "search": {
            "url2": {"frequency": 1, "positions": [10]}
        }
    }

def test_find_single_word(sample_index):
    searcher = SearchEngine(sample_index)
    results = searcher.find("hello")
    assert set(results) == {"url1", "url2"}

def test_find_multi_word_and(sample_index):
    searcher = SearchEngine(sample_index)
    results = searcher.find("hello world")
    assert set(results) == {"url1"}

def test_find_no_results(sample_index):
    searcher = SearchEngine(sample_index)
    results = searcher.find("missing")
    assert results == []

def test_find_multi_word_no_results(sample_index):
    searcher = SearchEngine(sample_index)
    results = searcher.find("hello missing")
    assert results == []

def test_print_word_info(sample_index):
    searcher = SearchEngine(sample_index)
    output = searcher.print_word_info("hello")
    assert "Inverted index for 'hello':" in output
    assert "URL: url1" in output
    assert "Frequency: 1" in output
