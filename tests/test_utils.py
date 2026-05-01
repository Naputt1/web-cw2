import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from utils import stem, clean_and_tokenize, STOP_WORDS

def test_stem_suffixes():
    """Test that the custom stemmer correctly handles common English suffixes."""
    assert stem("quotes") == "quote"  # Suffix 's' removed
    assert stem("quoted") == "quot"   # Suffix 'ed' removed
    assert stem("quoting") == "quot"  # Suffix 'ing' removed
    assert stem("fairies") == "fairy" # Suffix 'ies' -> 'y'
    assert stem("running") == "runn"  # Suffix 'ing' removed (double consonant remains)
    assert stem("walked") == "walk"  # Suffix 'ed' removed

def test_stem_short_words():
    """Test that very short words are not over-stemmed."""
    assert stem("is") == "is"
    assert stem("bed") == "bed"
    assert stem("sing") == "sing"

def test_clean_and_tokenize_stop_words():
    """Test that stop words are filtered out."""
    text = "The world is amazing and beautiful"
    tokens = clean_and_tokenize(text)
    
    # 'The', 'is', 'and' are stop words
    assert "the" not in tokens
    assert "is" not in tokens
    assert "and" not in tokens
    assert "world" in tokens
    assert "amaz" in tokens  # stemmed from amazing
    assert "beautiful" in tokens  # not handled by simplified stemmer

def test_clean_and_tokenize_punctuation():
    """Test that punctuation is removed during tokenization."""
    text = "Hello, world! (Search-Tool)."
    tokens = clean_and_tokenize(text)
    assert tokens == ["hello", "world", "search", "tool"]

def test_stop_words_list():
    """Verify the stop words set is correctly initialized."""
    assert "the" in STOP_WORDS
    assert "and" in STOP_WORDS
    assert "python" not in STOP_WORDS
