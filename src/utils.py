import re
from typing import List, Set

# A basic list of English stop words to improve index quality
STOP_WORDS: Set[str] = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were',
    'will', 'with'
}

def stem(word: str) -> str:
    """
    Apply very basic stemming to a word.
    
    This is a simplified approach to demonstrate the concept of stemming.
    In a production system, a library like NLTK's PorterStemmer would be used.
    
    Args:
        word: The word to stem.
        
    Returns:
        The stemmed version of the word.
    """
    word = word.lower()
    # Simple suffix removal
    if len(word) > 4:
        if word.endswith('ies'):
            return word[:-3] + 'y'
        if word.endswith('s') and not word.endswith('ss'):
            return word[:-1]
        if word.endswith('ing'):
            return word[:-3]
        if word.endswith('ed'):
            return word[:-2]
    return word

def clean_and_tokenize(text: str) -> List[str]:
    """
    Clean text and tokenize into a list of stemmed, non-stop words.
    
    Args:
        text: The raw text string.
        
    Returns:
        A list of tokens.
    """
    # Remove non-alphanumeric characters
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    tokens = text.lower().split()
    
    # Filter stop words and apply stemming
    processed_tokens = [
        stem(word) for word in tokens 
        if word not in STOP_WORDS
    ]
    
    return processed_tokens
