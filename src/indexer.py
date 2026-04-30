import json
import re
from bs4 import BeautifulSoup
import os

class Indexer:
    def __init__(self):
        # index structure: { word: { url: { 'frequency': count, 'positions': [pos1, pos2, ...] } } }
        self.index = {}

    def clean_text(self, text):
        """Remove non-alphanumeric characters and convert to lowercase."""
        # Replace non-alphanumeric characters with spaces
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
        
        for position, word in enumerate(words):
            if word not in self.index:
                self.index[word] = {}
            
            if url not in self.index[word]:
                self.index[word][url] = {'frequency': 0, 'positions': []}
            
            self.index[word][url]['frequency'] += 1
            self.index[word][url]['positions'].append(position)

    def save_index(self, filepath):
        """Save the inverted index to a JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.index, f, indent=2)

    def load_index(self, filepath):
        """Load the inverted index from a JSON file."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.index = json.load(f)
            return True
        return False

    def get_word_index(self, word):
        """Get the inverted index entry for a specific word."""
        return self.index.get(word.lower(), {})
