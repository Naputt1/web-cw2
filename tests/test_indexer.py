import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from indexer import Indexer

def test_clean_text():
    indexer = Indexer()
    assert indexer.clean_text("Hello, World!") == "hello  world "
    assert indexer.clean_text("Python 3.10") == "python 3 10"

def test_tokenize():
    indexer = Indexer()
    assert indexer.tokenize("hello world test") == ["hello", "world", "test"]

def test_add_page():
    indexer = Indexer()
    html = "<html><body><p>Hello world. Hello search.</p></body></html>"
    url = "http://example.com"
    indexer.add_page(url, html)
    
    assert "hello" in indexer.index
    assert url in indexer.index["hello"]
    assert indexer.index["hello"][url]["frequency"] == 2
    assert indexer.index["hello"][url]["positions"] == [0, 2]
    
    assert "world" in indexer.index
    assert indexer.index["world"][url]["frequency"] == 1
    assert indexer.index["world"][url]["positions"] == [1]

def test_case_insensitivity():
    indexer = Indexer()
    html = "<html><body>Good good GOOD</body></html>"
    url = "http://example.com"
    indexer.add_page(url, html)
    
    assert "good" in indexer.index
    assert indexer.index["good"][url]["frequency"] == 3
